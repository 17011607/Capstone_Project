import os
from flask import *
from camera import camera
from drone_manager import DroneManager
from werkzeug.utils import secure_filename
from googleDrive import *
import time
import threading
import drone_state 

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))
TEMPLATES=os.path.join(PROJECT_ROOT,'templates')
STATIC_FOLDER=os.path.join(PROJECT_ROOT,'static')
app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

def get_drone():
    return DroneManager()

def video_generator():
    drone = get_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

def move_control():
    global status
    global height
    drone = get_drone()
    while 1:
        if status == 'R' :
            #drone.right(40)
            drone.send_command(f'go 0 -30 {height} 100', blocking=False)
            #print("right")
        elif status == 'L' :
            #drone.left(40)
            drone.send_command(f'go 0 30 {height} 100', blocking=False)
            #print("left")
        elif status == 'U' :
            #drone.forward(40)
            drone.send_command(f'go 30 0 {height} 100', blocking=False)
            #print("forward")
        elif status == 'D':
            #drone.back(40)
            drone.send_command(f'go -30 0 {height} 100', blocking=False)
            #print("down")
        elif status == 'LU':
            drone.send_command(f"go 30 30 {height} 100",blocking=False)
            #print("Left up")
        elif status == 'RU' :
            drone.send_command(f"go 30 -30 {height} 100",blocking=False)
            #print("Right up")
        elif status == 'LD':
            drone.send_command(f"go -30 30 {height} 100",blocking=False)
            #print("left down")
        elif status == 'RD':
            drone.send_command(f"go -30 -30 {height} 100",blocking=False)
            #print("right down")
        #else:
            drone.send_command(f"go 0 0 {height} 10",blocking=False)
            #print("stop")
        time.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/battery')
def drone_battery():
    battery=drone_state.battery()
    print(battery)
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
        direction = request.form.get('direction')
        if direction == 'C':
            height = 0
        elif direction == 'N':
            height = 10
        elif direction == 'S':
            height = -10
        elif direction == 'W':
            print(f'direction : W')
            # cw 
        elif direction == 'E':
            print(f'direction : E')
            # ccw
        elif direction == 'NW':
            height = 10 
            # cw
        elif direction == 'NE':
            height = 10 
            # ccw
        elif direction == 'SW':
            height = -10
            # cw
        elif direction == 'SE':
            height = -10
            # ccw
        
    elif cmd == "dronemove":
        global status
        direction = request.form.get('direction')
        status = direction

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

if __name__ == '__main__':
    #cam = camera('192.168.137.47', 4210)
    status = "S"
    _move = threading.Thread(target=move_control)
    _move.start()
    app.run(host='0.0.0.0',port="9999", threaded=True)
