from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.config import settings
from backend.services.attendance import AttendanceManager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)

    try:
        while True:
            await websocket.receive_text()
            await AttendanceManager.broadcast_update(client_id, websocket)
    except WebSocketDisconnect:
        AttendanceManager.remove_connection(client_id)
    except Exception as e:
        print(f"Error in WebSocket endpoint: {str(e)}")
