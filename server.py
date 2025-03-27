from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import base64
import os

app = Flask(__name__)
socketio = SocketIO(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"User joined room: {room}"}, room=room)

@socketio.on('send_file')
def handle_file(data):
    room = data['room']
    filename = data['filename']
    filedata = data['filedata']

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Decode and save the file
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(filedata))

    emit('receive_file', {'filename': filename, 'filedata': filedata}, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
