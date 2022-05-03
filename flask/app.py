import os
from flask import *
from camera import camera
from drone_manager import DroneManager
from werkzeug.utils import secure_filename
from googleDrive import *
import time
import threading

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
    drone = get_drone
    while 1:
        if status == 'R' :
            #drone.right(20)
            print("right")
        elif status == 'L' :
            #drone.left(20)
            print("left")
        elif status == 'U' :
            #drone.forward(20)
            print("forward")
        elif status == 'D':
            #drone.back(20)
            print("down")
        elif status == 'LU':
            #drone.send_command(f"go 30 30 0 100")
            print("Left up")
        elif status == 'RU' :
            #drone.send_command(f"go -30 30 0 100")
            print("Right up")
        elif status == 'LD':
            #drone.send_command(f"go 30 -30 0 100")
            print("left down")
        elif status == 'RD':
            #drone.send_command(f"go -30 -30 0 100")
            print("right down")
        else:
            #drone.send_command(f"go 0 0 0 10")
            print("stop")
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/controller/')
def controller():
    return render_template('controller.html')

@app.route('/api/command/', methods=['POST'])
def command():
    drone = get_drone()
    cmd=request.form.get('command')
    if cmd == "cammove":
        direction = request.form.get('direction')
        #cam.send(direction)
    elif cmd == "dronemove":
        global status
        direction = request.form.get('direction')
        print(f"direction : {direction}")
        status = direction
        
    
    elif cmd == "takeoff":
        drone.takeoff()

    elif cmd == "land":
        drone.land()

    elif cmd == "streamon":
        drone.streamon()

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

@app.route('/setting/ap')
def ap():
    drone = get_drone()
    ssid = request.form.get('SSID')
    password = request.form.get('password')
    drone.send_command(f'ap {ssid} {password}')
    return render_template('setting.html')


@app.route('/video/streaming')
def video_feed():
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')





if __name__ == '__main__':
    #cam = camera('192.168.137.47', 4210)
    #temp_direction = "SS"
    status = "S"
    _move = threading.Thread(target=move_control)
    _move.start()
    app.run(host='0.0.0.0',port="9999", threaded=True)
