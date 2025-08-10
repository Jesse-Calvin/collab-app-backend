from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = []

@app.get("/")
def read_root():
    return {"message": "Collaborative Drawing App"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ New client connected")
    connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print("📨 Received from client:", data)
            for conn in connections:
                if conn != websocket:
                    print("➡️ Sending to another client")
                    await conn.send_text(data)
    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        connections.remove(websocket)
        print("👋 Client disconnected")
