import random
from dataclasses import dataclass, field
from typing import Optional


SUITS = ['P', 'T', 'Z', 'M']
VALUES = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_POINTS = {'A': 11, '10': 10}
HAND_SIZE = 4


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


@dataclass
class Chain:
    """Tracks the state of a single trick (lánc)."""
    base_rank: str           # rank of the lead card — fixed for the whole chain
    pile: list[Card]         # all cards played so far in this chain
    attacker_id: str         # last capturer (or opener); takes the pile when chain ends
    responder_id: str
    phase: str               # 'attacker_play' | 'responder_play'


class ClassicGameEngine:
    """
    Self-contained classic Zsíros engine.

    Game flow
    ---------
    1.  Each player starts with HAND_SIZE cards; the rest is the draw pile.
    2.  The opener plays any card to start a chain (lánc).
    3.  Within the chain:
          - The *attacker* (last capturer, initially the opener) plays a capturing
            card (same rank as the lead OR any 7), or *yields* if they have one,
            or *sacrifices* any card if they have no capturing card.
          - The *responder* plays any card.
            · If it captures (same lead-rank or any 7) → responder becomes new attacker.
            · If it doesn't → chain ends; attacker (last capturer) takes the pile.
          - Attacker can also call yield_trick() instead of playing; this ends the
            chain and the attacker takes the pile.
    4.  After each chain: both players refill to HAND_SIZE from the draw pile
        (attacker draws first).  When the draw pile is exhausted, no refill.
    5.  Game ends when both hands are empty.  Aces score 11 pts, tens 10 pts.
        Total points always sum to 84.
    """

    def __init__(self, room_code: str):
        self.room_code = room_code
        self.player_ids: list[str] = []
        self.hands: dict[str, list[Card]] = {}
        self.draw_pile: list[Card] = []
        self.collected: dict[str, list[Card]] = {}
        self.chain: Optional[Chain] = None
        self.opener: str = ''
        self.finished: bool = False

    # ── public API ────────────────────────────────────────────────────────────

    def start_game(self, player_ids: list[str]) -> dict[str, dict]:
        self.player_ids = list(player_ids)
        deck = _full_deck()
        random.shuffle(deck)
        self.hands = {
            player_ids[0]: list(deck[:HAND_SIZE]),
            player_ids[1]: list(deck[HAND_SIZE: 2 * HAND_SIZE]),
        }
        self.draw_pile = list(deck[2 * HAND_SIZE:])
        self.collected = {pid: [] for pid in player_ids}
        self.chain = None
        self.opener = random.choice(player_ids)
        self.finished = False
        return self._states()

    def play_card(self, player_id: str, card_dict: dict) -> dict:
        """
        Play a card from the player's hand.

        On chain start: any card is valid (becomes the lead / base card).
        On attacker_play: must play a capturing card if the player has one;
                          otherwise any card (sacrifice).
        On responder_play: any card; whether it captures is determined by rank.

        Returns per-player state dicts, or {'error': str} on invalid input.
        """
        if self.finished:
            return {'error': 'Game is already finished'}

        card = Card.from_dict(card_dict)

        if self.chain is None:
            return self._handle_lead(player_id, card)

        if self.chain.phase == 'attacker_play':
            return self._handle_attacker_play(player_id, card)

        if self.chain.phase == 'responder_play':
            return self._handle_responder_play(player_id, card)

        return {'error': 'Unknown game phase'}

    def yield_trick(self, player_id: str) -> dict:
        """
        Explicitly yield the current chain.  Only valid for the attacker when
        they still hold at least one capturing card (if they have none, they
        must sacrifice via play_card instead).

        The attacker ends the chain and takes the pile.
        """
        if self.finished:
            return {'error': 'Game is already finished'}
        if self.chain is None:
            return {'error': 'No active chain'}
        chain = self.chain
        if chain.phase != 'attacker_play':
            return {'error': 'Can only yield on your attacker turn'}
        if player_id != chain.attacker_id:
            return {'error': 'Not your turn'}
        if not self._capturing_cards(player_id, chain.base_rank):
            return {'error': 'No capturing cards — must sacrifice via play_card instead'}
        return self._end_chain(chain.attacker_id)

    def get_state_for_player(self, player_id: str) -> dict:
        other = self._other(player_id)
        chain = self.chain
        can_yield = (
            chain is not None
            and chain.phase == 'attacker_play'
            and chain.attacker_id == player_id
            and bool(self._capturing_cards(player_id, chain.base_rank))
        )
        return {
            'type': 'game_state',
            'my_hand': [c.to_dict() for c in self.hands.get(player_id, [])],
            'opp_hand_count': len(self.hands.get(other, [])),
            'draw_pile_count': len(self.draw_pile),
            'chain': self._chain_dict() if chain else None,
            'is_my_turn': self._is_my_turn(player_id),
            'can_yield': can_yield,
            'my_points': self._points(player_id),
            'opp_points': self._points(other),
            'my_collected': self._summary(player_id),
            'opp_collected': self._summary(other),
            'finished': self.finished,
            'winner': self._winner() if self.finished else None,
        }

    # ── internal play handlers ────────────────────────────────────────────────

    def _handle_lead(self, player_id: str, card: Card) -> dict:
        if player_id != self.opener:
            return {'error': 'Not your turn to lead'}
        if card not in self.hands[player_id]:
            return {'error': 'Card not in hand'}
        self.hands[player_id].remove(card)
        other = self._other(player_id)
        self.chain = Chain(
            base_rank=card.value,
            pile=[card],
            attacker_id=player_id,
            responder_id=other,
            phase='responder_play',
        )
        return self._states()

    def _handle_attacker_play(self, player_id: str, card: Card) -> dict:
        chain = self.chain
        if player_id != chain.attacker_id:
            return {'error': 'Not your turn'}
        if card not in self.hands[player_id]:
            return {'error': 'Card not in hand'}
        capturing = self._capturing_cards(player_id, chain.base_rank)
        if capturing and not self._is_capturing(card, chain.base_rank):
            return {'error': 'You have a capturing card — play it or yield instead'}
        self.hands[player_id].remove(card)
        chain.pile.append(card)
        chain.phase = 'responder_play'
        return self._states()

    def _handle_responder_play(self, player_id: str, card: Card) -> dict:
        chain = self.chain
        if player_id != chain.responder_id:
            return {'error': 'Not your turn'}
        if card not in self.hands[player_id]:
            return {'error': 'Card not in hand'}
        self.hands[player_id].remove(card)
        chain.pile.append(card)
        if self._is_capturing(card, chain.base_rank):
            chain.attacker_id, chain.responder_id = chain.responder_id, chain.attacker_id
            chain.phase = 'attacker_play'
            # if new attacker has no cards left, end immediately
            if not self.hands[chain.attacker_id]:
                return self._end_chain(chain.attacker_id)
            return self._states()
        return self._end_chain(chain.attacker_id)

    # ── chain resolution ──────────────────────────────────────────────────────

    def _end_chain(self, winner_id: str) -> dict[str, dict]:
        self.collected[winner_id].extend(self.chain.pile)
        self.chain = None
        self.opener = winner_id
        self._refill()
        # If any player has no cards, neither can participate in the next chain.
        # Each player keeps their remaining hand cards as scored cards.
        if any(not self.hands[pid] for pid in self.player_ids):
            for pid in self.player_ids:
                self.collected[pid].extend(self.hands[pid])
                self.hands[pid] = []
            self.finished = True
        return self._states()

    def _refill(self) -> None:
        # winner draws first
        order = [self.opener, self._other(self.opener)]
        for pid in order:
            need = HAND_SIZE - len(self.hands[pid])
            if need > 0:
                drawn = self.draw_pile[:need]
                self.draw_pile = self.draw_pile[need:]
                self.hands[pid].extend(drawn)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _is_capturing(self, card: Card, base_rank: str) -> bool:
        return card.value == base_rank or card.value == '7'

    def _capturing_cards(self, player_id: str, base_rank: str) -> list[Card]:
        return [c for c in self.hands[player_id] if self._is_capturing(c, base_rank)]

    def _is_my_turn(self, player_id: str) -> bool:
        if self.chain is None:
            return player_id == self.opener
        if self.chain.phase == 'attacker_play':
            return player_id == self.chain.attacker_id
        return player_id == self.chain.responder_id

    def _chain_dict(self) -> dict:
        c = self.chain
        return {
            'base_rank': c.base_rank,
            'pile': [card.to_dict() for card in c.pile],
            'phase': c.phase,
            'attacker_id': c.attacker_id,
        }

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
