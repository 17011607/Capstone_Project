import os
from re import A, X, match
from urllib import request
from flask import *
from camera import camera
from drone_manager import DroneManager
from werkzeug.utils import secure_filename
from googleDrive import *
import subprocess
from multiprocessing import Process, Value, Array, Lock
import socket
import shutil
import requests
import json


PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))
TEMPLATES=os.path.join(PROJECT_ROOT,'templates')
STATIC_FOLDER=os.path.join(PROJECT_ROOT,'static')
app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

app.config['STATIC_FOLDER'] = STATIC_FOLDER

DISTANCE = 50
HEIGHT = 50
DEGREE = 50

rec_proc = None

def get_drone():
    return DroneManager()

def json_parser(name, value):
    f = open("setting.json", "r")
    data = json.load(f)
    data[name] = value
    f.close()
    with open("setting.json", "w") as f:
        json.dump(data,f)

def video_generator():
    drone = get_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

def move_control(a,b,height,degree):
    temp_a = 0
    temp_b = 0
    temp_height = 0
    temp_degree = 0
    move_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    drone_ip = "192.168.10.1"
    drone_port = 8889
    drone_address=(drone_ip,drone_port)
    while 1:
        #print(f"{a.value}, {b.value}, {height.value}, {degree.value}")
        #socket.sendto(f"rc 10 0 0 0".encode('utf-8'), drone_address)
        if a.value == temp_a and b.value == temp_b and height.value == temp_height and degree.value == temp_degree:
            #print(f"[-] temp_a : {temp_a}, temp_b : {temp_b}, temp_height : {temp_height}, temp_degree : {temp_degree}")
            continue
        elif a.value == 0 and b.value == 0 and height.value  == 0 and degree.value == 0:
            move_socket.sendto(f"stop".encode('utf-8'), drone_address)
            #drone.send_command(f"stop")
            print(f"Drone Stop!")
        else:
            print(f"[+] a : {a.value}, b : {b.value}, height : {height.value}, degree : {degree.value}")
            print(f"[+] temp_a : {temp_a}, temp_b : {temp_b}, temp_height : {temp_height}, temp_degree : {temp_degree}")
            move_socket.sendto(f"rc 0 0 0 0".encode('utf-8'), drone_address)
            move_socket.sendto(f"rc {a.value} {b.value} {height.value} {degree.value}".encode('utf-8'), drone_address)
        temp_a = a.value
        temp_b = b.value
        temp_height = height.value
        temp_degree = degree.value

def get_processes_running():
    # 영어일때는 `ignore` 인자 없어도 됨  
    tasks = subprocess.check_output(['tasklist']).decode('cp949', 'ignore').split("\r\n")
    p = []
    for task in tasks:
        m = match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.* K).*",task)
        if m is not None:
            p.append({"image":m.group(1),
                        "pid":m.group(2),
                        "session_name":m.group(3),
                        "session_num":m.group(4),
                        "mem_usage":m.group(5)
                        })
    return p



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/battery')
def drone_battery():
    drone = get_drone()
    battery = drone.battery()
    return jsonify({"battery":battery})

@app.route('/user_list')
def user_list():
    files=os.listdir('./ids')
    data={}
    for file in files:
        data[f"{file}"]=file
    return jsonify(data)

@app.route('/controller/')
def controller():
    return render_template('controller.html')

@app.route('/api/command/', methods=['POST'])
def command():
    drone = get_drone()
    cmd=request.form.get('command')
    print(f"command : {cmd}")
    if cmd == "cammove":
        global height
        global degree
        direction = request.form.get('direction')
        height.value = 0
        degree.value = 0
        if direction == 'N':
            height.value = HEIGHT

        elif direction == 'S':
            height.value = -HEIGHT

        elif direction == 'W':
            degree.value = -DEGREE

        elif direction == 'E':
            degree.value = DEGREE

        elif direction == 'NW':
            height.value = HEIGHT
            degree.value = -DEGREE

        elif direction == 'NE':
            height.value = HEIGHT
            degree.value = DEGREE

        elif direction == 'SW':
            height.value = -HEIGHT
            degree.value = -DEGREE

        elif direction == 'SE':
            height.value = -HEIGHT
            degree.value = DEGREE

        else:
            height.value = 0
            degree.value = 0

        
    elif cmd == "dronemove":
        global a
        global b
        direction = request.form.get('direction')
        a.value = 0
        b.value = 0
        if direction == 'R' :
            a.value = DISTANCE
            b.value = 0

        elif direction == 'L' :
            a.value = -DISTANCE
            b.value = 0

        elif direction == 'U' :
            a.value = 0
            b.value = DISTANCE

        elif direction == 'D':
            a.value = 0
            b.value = -DISTANCE

        elif direction == 'RU':
            a.value = DISTANCE
            b.value = DISTANCE

        elif direction == 'LU' :
            a.value = -DISTANCE
            b.value = DISTANCE

        elif direction == 'RD':
            a.value = DISTANCE
            b.value = -DISTANCE

        elif direction == 'LD':
            a.value = -DISTANCE
            b.value = -DISTANCE

        else:
            a.value = 0
            b.value = 0

    elif cmd == "takeoff":
        drone.takeoff()

    elif cmd == "land":
        drone.land()

    elif cmd == "streamon":
        drone.streamon()
    
    elif cmd == "speed":
        speed=request.form.get('speed')
        drone.set_speed(speed)
        json_parser('speed', speed)

    elif cmd == "height":
        height=request.form.get('height')
        # set height code
        json_parser('height', height)

    return jsonify(status='success'), 200




@app.route('/setting/')
def setting():
    return render_template('setting.html')

@app.route('/setting/get_credentials')
def get_credentials():
    # make token
    client_id="303423050557-q0j988opbao7sgqefm2roi7cam0rk1i6.apps.googleusercontent.com"
    redirect_uri="http://localhost:9999/authcode"
    scope="https://www.googleapis.com/auth/drive.file"
    response_type="code"
    url = "https://accounts.google.com/o/oauth2/v2/auth"
    return redirect(f"{url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}")

@app.route('/authcode', methods=['GET'])
def google_auth():
    code = request.args.get('code')
    data = {
        "code":code,
        "client_id":"303423050557-q0j988opbao7sgqefm2roi7cam0rk1i6.apps.googleusercontent.com",
        "client_secret":"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",
        "redirect_uri":"http://localhost:9999/authcode",
        "grant_type":"authorization_code"
    }
    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    with open("token.json", "w") as f:
        f.write(response.text)
    return "ok"

@app.route('/setting/ap', methods=['POST'])
def ap():
    drone = get_drone()
    ssid = request.form.get('SSID')
    password = request.form.get('password')
    drone.send_command(f'ap {ssid} {password}')
    return render_template('setting.html')

@app.route('/setting/regist_file', methods=['POST'])
def regist_file(): # 프론트에서 파일을 못가져옴...ㅠㅠ
    name=request.form.get('user_name')
    f = request.files['file']
    os.makedirs(f"./ids/{name}", exist_ok=True)
    os.makedirs(f"./static/img/profile/{name}", exist_ok=True)
    shutil.copy("./static/img/profile.jpg",f"./static/img/profile/{name}/profile.jpg")
    f.save(os.path.join(app.config['STATIC_FOLDER'], "1.jpg"))
    os.replace("./static/1.jpg",f"./ids/{name}/{name}.jpg")
    return render_template('regist_fileupload.html')

@app.route('/setting/regist_snapshot', methods=['POST'])
def regist_snapshot():
    name=request.form.get('user_name')
    os.makedirs(f"./ids/{name}", exist_ok=True)
    os.replace("./static/img/snapshots/snapshot.jpg",f"./ids/{name}/{name}.jpg")
    os.makedirs(f"./static/img/profile/{name}", exist_ok=True)
    shutil.copy("./static/img/profile.jpg",f"./static/img/profile/{name}/profile.jpg")
    return render_template('regist_snapshot.html')

@app.route('/setting/user_delete', methods=['POST'])
def user_delete():
    name=request.form.get('user_name')
    if os.path.isdir(f"./ids/{name}")==False:
        return render_template('regist_del.html')
    shutil.rmtree(f"./ids/{name}")
    shutil.rmtree(f"./static/img/profile/{name}")
    return render_template('regist_del.html')

@app.route('/setting/gesture', methods=['POST'])
def set_gesture():
    f=open("gesture.json","w")
    data=request.json
    print(data)
    f.write(json.dumps(data))
    f.close()
    return render_template('gesture.html')

@app.route('/gesture')
def gesture_page():
    return render_template('gesture.html')

@app.route('/regist/')
def regist():
    return render_template('regist.html')

@app.route('/regist/regist_snapshot')
def regist_snpashot_page():
    return render_template('regist_snapshot.html')

@app.route('/regist/regist_fileupload')
def regist_fileupload_page():
    return render_template('regist_fileupload.html')

@app.route('/regist/regist_del')
def regist_delete_page():
    return render_template('regist_del.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/video/streaming')
def video_feed():
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video/snapshot')
def snap_shot():
    drone = get_drone()
    drone.snapshot()
    try:
        with open('token.json', 'r') as json_file:
            json_data = json.load(json_file)
            access_token = json_data['access_token']
            upload(access_token,"./static/img/snapshots/snapshot.jpg")
    except:
        pass
    
@app.route('/user_select', methods=['GET'])
def user_select():
    try:
        rec_proc.kill()
    except:
        pass
    name = request.args.get('name')
    rec_proc = subprocess.Popen(['python','main.py','./ids',name])
    return render_template('index.html')

if __name__ == '__main__':
    a = Value('i', 0)
    b = Value('i', 0)
    height = Value('i', 0)
    degree = Value('i', 0)
    move_proc = Process(target=move_control, args=(a,b,height,degree))
    move_proc.start()
    app.run(host='0.0.0.0',port="9999", threaded=True)
