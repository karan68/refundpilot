from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

from config import CORS_ORIGINS
from models.database import init_db
from data.seed_data import seed_database
from routers import refund_router, dashboard_router, query_router, webhook_router
from routers import demo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB + seed
    await init_db()
    await seed_database()
    print("🚀 RefundPilot backend ready")
    yield
    # Shutdown
    print("👋 RefundPilot shutting down")


app = FastAPI(
    title="RefundPilot",
    description="The Instant Justice Machine — Autonomous Refund Decision Agent",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(refund_router.router)
app.include_router(dashboard_router.router)
app.include_router(query_router.router)
app.include_router(webhook_router.router)
app.include_router(demo_router.router)


# WebSocket for real-time streaming (reasoning chain, risk score updates)
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # In Phase 2, incoming WS messages will trigger the agent
            await websocket.send_json({"type": "ack", "message": "Connected to RefundPilot"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "name": "RefundPilot",
        "tagline": "The Instant Justice Machine",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
