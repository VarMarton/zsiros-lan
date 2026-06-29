import random
from dataclasses import dataclass
from typing import Optional


SUITS = ['P', 'T', 'Z', 'M']
VALUES = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_POINTS = {'A': 11, '10': 10}


@dataclass(frozen=True)
class Card:
    suit: str
    value: str

    def to_dict(self) -> dict:
        return {'suit': self.suit, 'value': self.value}

    @staticmethod
    def from_dict(d: dict) -> 'Card':
        return Card(suit=d['suit'], value=d['value'])


def _full_deck() -> list[Card]:
    return [Card(suit=s, value=v) for s in SUITS for v in VALUES]


def _card_points(value: str) -> int:
    return CARD_POINTS.get(value, 0)


class ClassicGameEngine:
    def __init__(self, room_code: str):
        self.room_code = room_code
        self.player_ids: list[str] = []
        self.hands: dict[str, list[Card]] = {}
        self.collected: dict[str, list[Card]] = {}
        self.trick: list[tuple[str, Card]] = []
        self.leader: str = ''
        self.turn: str = ''
        self.finished: bool = False

    def start_game(self, player_ids: list[str]) -> dict[str, dict]:
        self.player_ids = list(player_ids)
        deck = _full_deck()
        random.shuffle(deck)
        mid = len(deck) // 2
        self.hands = {
            player_ids[0]: list(deck[:mid]),
            player_ids[1]: list(deck[mid:]),
        }
        self.collected = {pid: [] for pid in player_ids}
        self.trick = []
        self.leader = random.choice(player_ids)
        self.turn = self.leader
        self.finished = False
        return self._states()

    def play_card(self, player_id: str, card_dict: dict) -> dict:
        if self.finished:
            return {'error': 'Game is already finished'}
        if player_id != self.turn:
            return {'error': 'Not your turn'}

        card = Card.from_dict(card_dict)
        hand = self.hands[player_id]
        if card not in hand:
            return {'error': 'Card not in hand'}

        hand.remove(card)
        self.trick.append((player_id, card))

        if len(self.trick) == 1:
            self.turn = self._other(player_id)
            return self._states()

        return self._resolve_trick()

    def get_state_for_player(self, player_id: str) -> dict:
        other = self._other(player_id)
        return {
            'type': 'game_state',
            'my_hand': [c.to_dict() for c in self.hands.get(player_id, [])],
            'opp_hand_count': len(self.hands.get(other, [])),
            'table': [
                {'player_id': pid, 'card': c.to_dict()}
                for pid, c in self.trick
            ],
            'is_my_turn': self.turn == player_id,
            'my_points': self._points(player_id),
            'opp_points': self._points(other),
            'my_collected': self._summary(player_id),
            'opp_collected': self._summary(other),
            'finished': self.finished,
            'winner': self._winner() if self.finished else None,
        }

    def _resolve_trick(self) -> dict[str, dict]:
        (first_pid, first_card), (second_pid, second_card) = self.trick

        second_wins = (
            second_card.value == first_card.value
            or second_card.value == '7'
        )
        winner = second_pid if second_wins else first_pid

        self.collected[winner].extend([first_card, second_card])
        self.trick = []
        self.leader = winner
        self.turn = winner

        if all(len(self.hands[pid]) == 0 for pid in self.player_ids):
            self.finished = True

        return self._states()

    def _states(self) -> dict[str, dict]:
        return {pid: self.get_state_for_player(pid) for pid in self.player_ids}

    def _other(self, player_id: str) -> str:
        return next(pid for pid in self.player_ids if pid != player_id)

    def _points(self, player_id: str) -> int:
        return sum(_card_points(c.value) for c in self.collected[player_id])

    def _summary(self, player_id: str) -> dict:
        cards = self.collected[player_id]
        return {
            'aces': sum(1 for c in cards if c.value == 'A'),
            'tens': sum(1 for c in cards if c.value == '10'),
            'points': self._points(player_id),
        }

    def _winner(self) -> Optional[str]:
        p0, p1 = self.player_ids
        pts0, pts1 = self._points(p0), self._points(p1)
        if pts0 > pts1:
            return p0
        if pts1 > pts0:
            return p1
        return None
