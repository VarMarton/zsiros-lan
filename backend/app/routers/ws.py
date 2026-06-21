import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.room_manager import room_manager
from app.models.room import RoomStatus, PlayerRole

router = APIRouter()


async def _send(ws: WebSocket, msg: dict) -> None:
    await ws.send_text(json.dumps(msg))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    player = None
    room = None

    try:
        async for raw in websocket.iter_text():
            data = json.loads(raw)
            msg_type = data.get("type")

            # ── create_room ──────────────────────────────────────────────
            if msg_type == "create_room":
                room, player = room_manager.create_room(
                    host_name=data["player_name"],
                    host_ws=websocket,
                )
                await _send(websocket, {
                    "type": "room_created",
                    "room_code": room.code,
                    "player_id": player.id,
                    "role": player.role,
                })

            # ── join_request ─────────────────────────────────────────────
            elif msg_type == "join_request":
                room = room_manager.get_room(data["room_code"])
                if room is None:
                    await _send(websocket, {"type": "error", "message": "Room not found"})
                    continue
                if room.status != RoomStatus.LOBBY:
                    await _send(websocket, {"type": "error", "message": "Room is not in lobby"})
                    continue
                if room.pending_guest or room.guest:
                    await _send(websocket, {"type": "error", "message": "Room is full"})
                    continue

                from app.models.room import Player
                pending = Player(name=data["player_name"], role=PlayerRole.GUEST, websocket=websocket)
                room.pending_guest = pending
                player = pending

                # notify guest that request is pending
                await _send(websocket, {"type": "join_pending", "room_code": room.code})

                # notify host
                await _send(room.host.websocket, {
                    "type": "join_request_received",
                    "player_id": pending.id,
                    "player_name": pending.name,
                })

            # ── approve_join / reject_join ────────────────────────────────
            elif msg_type in ("approve_join", "reject_join"):
                if room is None or player is None or player.role != PlayerRole.HOST:
                    await _send(websocket, {"type": "error", "message": "Not authorized"})
                    continue
                pending = room.pending_guest
                if pending is None:
                    await _send(websocket, {"type": "error", "message": "No pending join request"})
                    continue

                if msg_type == "approve_join":
                    room.guest = pending
                    room.pending_guest = None
                    await _send(pending.websocket, {
                        "type": "join_approved",
                        "player_id": pending.id,
                        "room_code": room.code,
                    })
                    await _send(websocket, {"type": "join_approved_ack", "player_name": pending.name})
                else:
                    room.pending_guest = None
                    await _send(pending.websocket, {"type": "join_rejected"})
                    await _send(websocket, {"type": "join_rejected_ack"})

            # ── start_game ───────────────────────────────────────────────
            elif msg_type == "start_game":
                if room is None or player is None or player.role != PlayerRole.HOST:
                    await _send(websocket, {"type": "error", "message": "Not authorized"})
                    continue
                if room.guest is None:
                    await _send(websocket, {"type": "error", "message": "Need two players to start"})
                    continue
                room.status = RoomStatus.IN_GAME
                # TODO: initialize game engine and deal cards
                for p in [room.host, room.guest]:
                    await _send(p.websocket, {"type": "game_started"})

            # ── play_card ────────────────────────────────────────────────
            elif msg_type == "play_card":
                # TODO: forward to game engine, broadcast updated game_state
                await _send(websocket, {"type": "error", "message": "Game logic not implemented yet"})

            else:
                await _send(websocket, {"type": "error", "message": f"Unknown message type: {msg_type}"})

    except WebSocketDisconnect:
        # TODO: notify the other player and clean up if needed
        if room and room.host and room.host.websocket is websocket:
            if room.guest and room.guest.websocket:
                await _send(room.guest.websocket, {"type": "opponent_disconnected"})
            room_manager.remove_room(room.code)
        elif room and room.guest and room.guest.websocket is websocket:
            if room.host and room.host.websocket:
                await _send(room.host.websocket, {"type": "opponent_disconnected"})
