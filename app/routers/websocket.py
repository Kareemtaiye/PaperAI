from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jwt import ExpiredSignatureError, InvalidSignatureError
from app.core.security import verify_websocket_token
from app.services.pubsub import pubsub_manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str):
    try:
        valid = verify_websocket_token(token, user_id)
    except ExpiredSignatureError:
        await websocket.close(code=4001, reason="Token expired")
        return
    except InvalidSignatureError:
        await websocket.close(code=4002, reason="Invalid token")
        return
    except Exception as e:
        # logger.error(f"WS auth failed: {type(e).__name__}: {e}")
        await websocket.close(code=4003, reason="Unauthorized")
        return

    if not valid:
        await websocket.close(code=4002, reason="Unauthorized")

    # Accept only after validation passes
    await websocket.accept()

    try:
        async for message in pubsub_manager.subscribe(user_id):
            await websocket.send_json(message)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        # logger.exception(f"Websocket error for user {user_id}: {exc}")
        await websocket.close()
