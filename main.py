import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins for now (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []
strokes = []  # Store all strokes in memory

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    # Send existing strokes to new client
    await ws.send_text(json.dumps({"type": "init", "strokes": strokes}))

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "start":
                current_stroke = [{"x": msg["x"], "y": msg["y"], "color": msg["color"]}]
                strokes.append(current_stroke)
                await broadcast(msg)

            elif msg["type"] == "draw":
                if strokes:
                    strokes[-1].append({"x": msg["x"], "y": msg["y"], "color": msg["color"]})
                await broadcast(msg)

            elif msg["type"] == "endStroke":
                await broadcast(msg)

            elif msg["type"] == "clear":
                strokes.clear()
                await broadcast({"type": "clear"})

            elif msg["type"] == "undo":
                if strokes:
                    strokes.pop()
                await broadcast({"type": "undo", "strokes": strokes})

    except WebSocketDisconnect:
        clients.remove(ws)

async def broadcast(message):
    """Send message to all connected clients."""
    for client in clients:
        await client.send_text(json.dumps(message))
