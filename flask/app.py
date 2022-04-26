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
        direction = request.form.get('direction')
        print(f"direction : {direction}")
        if direction.find('R') != -1 :
            drone.right()
        if direction.find('L') != -1 :
            drone.left()
        if direction.find('U') != -1 :
            drone.forward()
        if direction.find('D') != -1 :
            drone.back()

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
