import random
import string
from typing import Optional
from app.models.room import Room, Player, PlayerRole, RoomStatus


def _generate_room_code(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase, k=length))


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def create_room(self, host_name: str, host_ws) -> tuple[Room, Player]:
        code = self._unique_code()
        host = Player(name=host_name, role=PlayerRole.HOST, websocket=host_ws)
        room = Room(code=code, host=host)
        self._rooms[code] = room
        return room, host

    def get_room(self, code: str) -> Optional[Room]:
        return self._rooms.get(code.upper())

    def remove_room(self, code: str) -> None:
        self._rooms.pop(code.upper(), None)

    def _unique_code(self) -> str:
        for _ in range(20):
            code = _generate_room_code()
            if code not in self._rooms:
                return code
        raise RuntimeError("Could not generate a unique room code")


room_manager = RoomManager()
