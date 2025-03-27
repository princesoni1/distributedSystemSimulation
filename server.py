from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import base64
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Serve the frontend
@app.get("/")
async def get():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if data["type"] == "file":
            filename = data["filename"]
            filedata = data["filedata"]

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(filedata))

            await websocket.send_json({"filename": filename, "filedata": filedata})

