# Game engine: all zsiros game logic lives here.
# Both 2-player (human vs human) and AI mode use this same engine.
# Human moves arrive via WebSocket; AI moves come from an AI player function.


class GameEngine:
    """
    Placeholder — game rules will be implemented here step by step.
    """

    def __init__(self, room_code: str):
        self.room_code = room_code
        self.state: dict = {}

    def start_game(self) -> dict:
        raise NotImplementedError("Game logic not implemented yet")

    def play_card(self, player_id: str, card: dict) -> dict:
        raise NotImplementedError("Game logic not implemented yet")

    def get_state_for_player(self, player_id: str) -> dict:
        raise NotImplementedError("Game logic not implemented yet")
