import os
from flask import *
from camera import camera
from drone_manager import DroneManager
from werkzeug.utils import secure_filename
from googleDrive import *

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))
TEMPLATES=os.path.join(PROJECT_ROOT,'templates')
STATIC_FOLDER=os.path.join(PROJECT_ROOT,'static')
app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

def get_drone():
    return DroneManager()

@app.route('/')
def index():
    return render_template('index.html')

# https://kr.freepik.com/premium-vector/battery-icons-charge-level-ui-design-elements-of-battery-full-low-and-empty-battery-status-set-of-smartphone-battery-charge-level-indicators_17743907.htm
@app.route('/battery')
def drone_battery():
    drone=get_drone()
    battery=drone.battery()
    return  jsonify({"battery":battery})

@app.route('/controller/')
def controller():
    return render_template('controller.html')

@app.route('/api/command/', methods=['POST'])
def command():
    drone = get_drone()
    cmd=request.form.get('command')
    if cmd=="cammove":
        direction = request.form.get('direction')
        print(f"direction : {direction}")
        if direction.find('R') != -1 :
            drone.clockwise(5)
        if direction.find('L') != -1 :
            drone.counter_clockwise(5)
        if direction.find('U') != -1 :
            drone.up(20)
        if direction.find('D') != -1 :
            drone.down(20)

    elif cmd == "dronemove":
        direction = request.form.get('direction')
        print(f"direction : {direction}")
        x = 0
        y = 0
        if direction.find('R') != -1 :
            x -= 30
        if direction.find('L') != -1 :
            x += 30
        if direction.find('U') != -1 :
            y += 30
        if direction.find('D') != -1 :
            y -= 30
        drone.send_command(f"go {x} {y} 0 100 blocking=False")

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

@app.route('/setting/ap')
def ap():
    drone = get_drone()
    ssid = request.form.get('SSID')
    password = request.form.get('password')
    drone.send_command(f'ap {ssid} {password}')
    return render_template('setting.html')

@app.route('/about/')
def about():
    return render_template('about.html')


def video_generator():
    drone = get_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')


@app.route('/video/streaming')
def video_feed():
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #cam = camera('192.168.137.47', 4210)
    app.run(host='0.0.0.0',port="9999", threaded=True)
