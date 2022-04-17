import os
from flask import *
from camera import camera

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))
TEMPLATES=os.path.join(PROJECT_ROOT,'templates')
STATIC_FOLDER=os.path.join(PROJECT_ROOT,'static')
app = Flask(__name__,
            template_folder=TEMPLATES,
            static_folder=STATIC_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/controller/')
def controller():
    return render_template('controller.html')

@app.route('/api/command/', methods=['POST'])
def command():
    cmd=request.form.get('command') # move commnad 시 coordX, coordY 매개변수도 같이 전달됨
    if cmd == "move":
        direction = request.form.get('direction')
        cam.send(direction)
    return jsonify(status='success'), 200


@app.route('/setting/')
def setting():
    return render_template('setting.html')

@app.route('/about/')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    cam = camera('192.168.137.47', 4210)
    app.run(host='0.0.0.0',port="9999", threaded=True)
