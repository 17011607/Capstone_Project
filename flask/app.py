import os
from re import A, X
from flask import *
from camera import camera
from drone_manager import DroneManager
from werkzeug.utils import secure_filename
from googleDrive import *
import time
import threading
import subprocess
from multiprocessing import Process, Value, Array, Lock
import socket

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))
TEMPLATES=os.path.join(PROJECT_ROOT,'templates')
STATIC_FOLDER=os.path.join(PROJECT_ROOT,'static')
app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

DISTANCE = 50
HEIGHT = 50
DEGREE = 50

def get_drone():
    return DroneManager()

def video_generator():
    drone = get_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

def move_control(a,b,height,degree):
    # global a
    # global b
    # global height
    # global degree
    temp_a = 0
    temp_b = 0
    temp_height = 0
    temp_degree = 0
    #socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #drone = get_drone()
    while 1:
        if a.value == temp_a and b.value == temp_b and height.value == temp_height and degree.value == temp_degree:
            #print(f"[-] temp_a : {temp_a}, temp_b : {temp_b}, temp_height : {temp_height}, temp_degree : {temp_degree}")
            continue
        elif a == 0 and b == 0 and height  == 0 and degree == 0:
            drone.send_command(f"stop")
            print(f"Drone Stop!")
        else:
            print(f"[+] a : {a.value}, b : {b.value}, height : {height.value}, degree : {degree.value}")
            print(f"[+] temp_a : {temp_a}, temp_b : {temp_b}, temp_height : {temp_height}, temp_degree : {temp_degree}")
            drone.send_command(f'rc 0 0 0 0')
            drone.send_command(f'rc {a} {b} {height} {degree}')
        time.sleep(0.01)
        temp_a = a.value
        temp_b = b.value
        temp_height = height.value
        temp_degree = degree.value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/battery')
def drone_battery():
    drone = get_drone()
    battery = drone.battery()
    return jsonify({"battery":battery})

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
            #height = HEIGHT
            #print(f"joystic1 : N = {direction}, {height}, {degree}")
        elif direction == 'S':
            height.value = -HEIGHT
            #height = -HEIGHT
            #print(f"joystic1 : S = {direction}, {height}, {degree}")
        elif direction == 'W':
            degree.value = -DEGREE
            #degree = -DEGREE
            #print(f"joystic1 : W = {direction}, {height}, {degree}")
        elif direction == 'E':
            degree.value = DEGREE
            #degree = DEGREE
            #print(f"joystic1 : E = {direction}, {height}, {degree}")
        elif direction == 'NW':
            height.value = HEIGHT
            degree.value = -DEGREE
            #height = HEIGHT
            #degree = -DEGREE
            #print(f"joystic1 : NW = {direction}, {height}, {degree}")
        elif direction == 'NE':
            height.value = HEIGHT
            degree.value = DEGREE
            #height = HEIGHT
            #degree = DEGREE
            #print(f"joystic1 : NE = {direction}, {height}, {degree}")
        elif direction == 'SW':
            height.value = -HEIGHT
            degree.value = -DEGREE
            #height = -HEIGHT
            #degree = -DEGREE
            #print(f"joystic1 : SW = {direction}, {height}, {degree}")
        elif direction == 'SE':
            height.value = -HEIGHT
            degree.value = DEGREE
            #height = -HEIGHT
            #degree = DEGREE
            #print(f"joystic1 : SE = {direction}, {height}, {degree}")
        else:
            height.value = 0
            degree.value = 0
            #height = 0
            #degree = 0
            #print(f"joystic1 : C = {direction}, {height}, {degree}")
        
    elif cmd == "dronemove":
        global a
        global b
        direction = request.form.get('direction')
        a.value = 0
        b.value = 0
        if direction == 'R' :
            a.value = DISTANCE
            b.value = 0
            #a = DISTANCE
            #b = 0
            #print(f"joystic2 : R = {direction}, {a}, {b}")
        elif direction == 'L' :
            a.value = -DISTANCE
            b.value = 0
            #a = -DISTANCE
            #b = 0
            #print(f"joystic2 : L = {direction}, {a}, {b}")
        elif direction == 'U' :
            a.value = 0
            b.value = DISTANCE
            #a = 0
            #b = DISTANCE
            #print(f"joystic2 : U = {direction}, {a}, {b}")
        elif direction == 'D':
            a.value = 0
            b.value = -DISTANCE
            #a = 0
            #b = -DISTANCE
            #print(f"joystic2 : D = {direction}, {a}, {b}")
        elif direction == 'RU':
            a.value = DISTANCE
            b.value = DISTANCE
            #a = DISTANCE
            #b = DISTANCE
            #print(f"joystic2 : RU = {direction}, {a}, {b}")
        elif direction == 'LU' :
            a.value = -DISTANCE
            b.value = DISTANCE
            #a = -DISTANCE
            #b = DISTANCE
            #print(f"joystic2 : LU = {direction}, {a}, {b}")
        elif direction == 'RD':
            a.value = DISTANCE
            b.value = -DISTANCE
            #a = DISTANCE
            #b = -DISTANCE
            #print(f"joystic2 : RD = {direction}, {a}, {b}")
        elif direction == 'LD':
            a.value = -DISTANCE
            b.value = -DISTANCE
            #a = -DISTANCE
            #b = -DISTANCE
            #print(f"joystic2 : LD = {direction}, {a}, {b}")
        else:
            a.value = 0
            b.value = 0
            #a = 0
            #b = 0
            #print(f"joystic2 : S = {direction}, {a}, {b}")

    elif cmd == "takeoff":
        drone.takeoff()

    elif cmd == "land":
        drone.land()

    elif cmd == "streamon":
        drone.streamon()
    
    elif cmd == "speed":
        speed=request.form.get('speed')
        drone.set_speed(speed)

    return jsonify(status='success'), 200


@app.route('/setting/')
def setting():
    return render_template('setting.html')

@app.route('/setting/get_credentials', methods=['POST'])
def get_credentials():
    f = request.files['file']
    os.makedirs("./credentials", exist_ok=True)
    f.save("./credentials/credentials.json")
    make_token()
    return render_template('setting.html')

@app.route('/setting/ap', methods=['POST'])
def ap():
    drone = get_drone()
    ssid = request.form.get('SSID')
    password = request.form.get('password')
    drone.send_command(f'ap {ssid} {password}')
    return render_template('setting.html')

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
    

if __name__ == '__main__':
    # if os.fork() == 0:
    #     # child process
    #     os.execl('/usr/bin/python3','python3','main.py','./ids','Son')
    # else:
    #     # parent Process
    #     a = 0
    #     b = 0
    #     height = 0
    #     degree = 0
    #     _move = threading.Thread(target=move_control)
    #     _move.start()
    #     app.run(host='0.0.0.0',port="9999", threaded=True)
    
    #a = 0
    #b = 0
    #height = 0
    #degree = 0
    rec_proc = subprocess.Popen(['python','main.py','./ids','Son'])
    #_move = threading.Thread(target=move_control)
    #_move.start()
    a = Value('i', 0)
    b = Value('i', 0)
    height = Value('i', 0)
    degree = Value('i', 0)
    move_proc = Process(target=move_control, args=(a,b,height,degree))
    move_proc.start()
    #move_proc.join()
    app.run(host='0.0.0.0',port="9999", threaded=True)