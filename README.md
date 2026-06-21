# zsiros-lan

Zsírozás, a Hungarian card game — self-hosted LAN webapp, playable from phones in the same network.

## Stack

- **Backend:** Python 3.11 + FastAPI + WebSocket (uvicorn)
- **Frontend:** React + Vite (Node 26)

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host   # --host exposes it on LAN
```

The frontend will be available at `http://<your-local-ip>:5173` from any device on the network.

## WebSocket Protocol

All messages are JSON. Client sends → server receives (and vice versa).

### Lobby flow

| Direction | Type | Payload | Description |
|-----------|------|---------|-------------|
| C → S | `create_room` | `player_name` | Host creates a new room |
| S → C | `room_created` | `room_code`, `player_id`, `role` | Room created successfully |
| C → S | `join_request` | `room_code`, `player_name` | Guest requests to join |
| S → C | `join_pending` | `room_code` | Guest told to wait for approval |
| S → C | `join_request_received` | `player_id`, `player_name` | Host notified of pending guest |
| C → S | `approve_join` | _(no extra fields)_ | Host approves the guest |
| C → S | `reject_join` | _(no extra fields)_ | Host rejects the guest |
| S → C | `join_approved` | `player_id`, `room_code` | Guest is now in the room |
| S → C | `join_rejected` | — | Guest was rejected |

### Game flow

| Direction | Type | Payload | Description |
|-----------|------|---------|-------------|
| C → S | `start_game` | — | Host starts the game |
| S → C | `game_started` | — | Broadcast to both players |
| S → C | `game_state_update` | `hand`, `table`, `scores`, `current_turn`, … | Full state snapshot (player-specific) |
| C → S | `play_card` | `card: { suit, rank }` | Player plays a card |

### Error / connection

| Direction | Type | Payload | Description |
|-----------|------|---------|-------------|
| S → C | `error` | `message` | Something went wrong |
| S → C | `opponent_disconnected` | — | Other player dropped |

> `game_state_update` shape will be finalized when game logic is implemented.
