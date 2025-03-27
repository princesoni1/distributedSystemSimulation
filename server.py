from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import base64
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dictionary to store active WebSocket connections per room
rooms = {}

@app.get("/")
async def get():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()

    # Add user to the room
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "file":
                filename = data["filename"]
                filedata = data["filedata"]

                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(filedata))

                # Send the file to all users in the room except the sender
                for client in rooms[room]:
                    if client != websocket:
                        await client.send_json({"filename": filename, "filedata": filedata})

    except WebSocketDisconnect:
        rooms[room].remove(websocket)
        if not rooms[room]:  # Delete room if empty
            del rooms[room]
