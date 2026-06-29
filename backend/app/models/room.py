from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import uuid


class RoomStatus(str, Enum):
    LOBBY = "lobby"
    IN_GAME = "in_game"
    FINISHED = "finished"


class PlayerRole(str, Enum):
    HOST = "host"
    GUEST = "guest"


@dataclass
class Player:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: PlayerRole = PlayerRole.GUEST
    websocket: Optional[object] = field(default=None, repr=False)


@dataclass
class Room:
    code: str
    status: RoomStatus = RoomStatus.LOBBY
    host: Optional[Player] = None
    guest: Optional[Player] = None
    pending_guest: Optional[Player] = None
    engine: Optional[object] = field(default=None, repr=False)
