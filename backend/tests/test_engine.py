"""
Unit tests for ClassicGameEngine.

Covered scenarios:
  - Basic chain: lead with no capture by responder → opener takes pile
  - Basic chain: lead with 7 capturing → responder takes pile
  - Capture chain: multiple rounds, base rank stays fixed
  - Yield: attacker yields when they have a capturing card
  - Yield blocked: no capturing cards → must sacrifice
  - Sacrifice: attacker has no capturing card, plays any card
  - Sacrifice then capture by responder: responder becomes new attacker
  - Refill: both hands restored to HAND_SIZE after chain
  - Draw pile exhaustion: no refill when pile is empty
  - Full game: total points always equal 84
"""

import random
import pytest
from app.game.engine import ClassicGameEngine, Card, HAND_SIZE


# ── helpers ──────────────────────────────────────────────────────────────────

def fresh_engine(opener='p0') -> ClassicGameEngine:
    """Engine with empty hands, no draw pile, opener set."""
    e = ClassicGameEngine('TEST')
    e.player_ids = ['p0', 'p1']
    e.hands = {'p0': [], 'p1': []}
    e.draw_pile = []
    e.collected = {'p0': [], 'p1': []}
    e.chain = None
    e.opener = opener
    e.finished = False
    return e


def c(value: str, suit: str = 'P') -> Card:
    return Card(suit=suit, value=value)


def play(engine: ClassicGameEngine, player_id: str, card: Card) -> dict:
    result = engine.play_card(player_id, card.to_dict())
    assert 'error' not in result, f"Unexpected error: {result.get('error')}"
    return result


def make_valid_move(engine: ClassicGameEngine, player_id: str, *, prefer_capture=True) -> dict:
    """Make a legal move; used for full-game simulation."""
    chain = engine.chain
    if chain is None:
        card = engine.hands[player_id][0]
        return engine.play_card(player_id, card.to_dict())

    if chain.phase == 'attacker_play' and chain.attacker_id == player_id:
        capturing = engine._capturing_cards(player_id, chain.base_rank)
        if capturing and prefer_capture:
            if random.random() < 0.25:
                r = engine.yield_trick(player_id)
                assert 'error' not in r
                return r
            return engine.play_card(player_id, random.choice(capturing).to_dict())
        # sacrifice
        card = engine.hands[player_id][0]
        return engine.play_card(player_id, card.to_dict())

    # responder
    card = random.choice(engine.hands[player_id])
    return engine.play_card(player_id, card.to_dict())


# ── chain basics ──────────────────────────────────────────────────────────────

class TestChainBasics:
    def test_opener_takes_pile_when_responder_misses(self):
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('9')]  # 9 does not capture K

        play(e, 'p0', c('K'))
        assert e.chain is not None
        assert e.chain.phase == 'responder_play'
        assert e.chain.attacker_id == 'p0'

        play(e, 'p1', c('9'))
        assert e.chain is None
        assert len(e.collected['p0']) == 2
        assert len(e.collected['p1']) == 0
        assert e.opener == 'p0'

    def test_seven_always_captures_any_lead(self):
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('A')]
        e.hands['p1'] = [c('7')]

        play(e, 'p0', c('A'))
        play(e, 'p1', c('7'))
        assert e.chain is None
        assert len(e.collected['p1']) == 2
        assert e.opener == 'p1'

    def test_same_rank_captures(self):
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('Q')]
        e.hands['p1'] = [c('Q', 'T')]

        play(e, 'p0', c('Q'))
        play(e, 'p1', c('Q', 'T'))
        assert e.chain is None
        assert len(e.collected['p1']) == 2

    def test_wrong_player_cannot_lead(self):
        e = fresh_engine(opener='p0')
        e.hands['p1'] = [c('K')]
        result = e.play_card('p1', c('K').to_dict())
        assert 'error' in result

    def test_card_not_in_hand_is_rejected(self):
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        result = e.play_card('p0', c('A').to_dict())
        assert 'error' in result


# ── base rank is fixed ────────────────────────────────────────────────────────

class TestBaseRankFixed:
    def test_base_rank_never_changes_after_lead(self):
        """
        Lead: K  →  capturing cards are K or 7 — NOT whatever was last played.
        Chain: p0 leads K, p1 responds 7 (captures), p1 is attacker.
        p1 plays 7 again (capturing), p0 responds with K (base rank → captures).
        p0 becomes attacker. Pile should have 4 cards.
        """
        e = fresh_engine(opener='p0')
        # p0 needs a spare card so the hand isn't empty when p0 captures (which
        # would trigger an auto-end instead of leaving the chain open)
        e.hands['p0'] = [c('K'), c('K', 'T'), c('9', 'T')]
        e.hands['p1'] = [c('7'), c('7', 'T'), c('9')]

        play(e, 'p0', c('K'))            # lead K, base_rank = 'K'
        play(e, 'p1', c('7'))            # 7 captures → p1 is attacker
        assert e.chain.attacker_id == 'p1'
        assert e.chain.base_rank == 'K'  # base rank unchanged

        play(e, 'p1', c('7', 'T'))       # p1 plays second 7 (capturing)
        play(e, 'p0', c('K', 'T'))       # p0 responds with K (= base rank, captures)
        assert e.chain.attacker_id == 'p0'

        # pile has 4 cards so far
        assert len(e.chain.pile) == 4

    def test_seven_as_lead_only_seven_can_capture(self):
        """If the lead card IS a 7, the only capturing rank is 7."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('7')]
        e.hands['p1'] = [c('A')]   # Ace does not capture a 7-lead

        play(e, 'p0', c('7'))
        assert e.chain.base_rank == '7'
        play(e, 'p1', c('A'))      # A ≠ 7 → no capture → p0 takes pile
        assert e.chain is None
        assert len(e.collected['p0']) == 2


# ── yield ─────────────────────────────────────────────────────────────────────

class TestYield:
    def test_attacker_yields_after_opponent_captures(self):
        """p1 captures, becomes attacker, then yields — p1 takes pile."""
        e = fresh_engine(opener='p0')
        # p0 needs a spare card so it isn't empty after leading (which would
        # trigger end-game during _end_chain and inflate p1's collected count)
        e.hands['p0'] = [c('K'), c('9')]
        e.hands['p1'] = [c('K', 'T'), c('7')]  # has capturing cards

        play(e, 'p0', c('K'))
        play(e, 'p1', c('K', 'T'))   # p1 captures, p1 = attacker
        assert e.chain.attacker_id == 'p1'

        result = e.yield_trick('p1')
        assert 'error' not in result
        assert e.chain is None
        assert len(e.collected['p1']) == 2   # exactly the 2 cards from the pile
        assert e.opener == 'p1'

    def test_yield_requires_capturing_card(self):
        """Cannot yield if you have no capturing card — must sacrifice."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('K', 'T'), c('9')]  # one capturing, one not

        play(e, 'p0', c('K'))
        play(e, 'p1', c('K', 'T'))   # p1 captures, p1 = attacker

        # now remove p1's remaining capturing card to simulate empty capturer
        e.hands['p1'] = [c('9')]     # only a 9 left
        result = e.yield_trick('p1')
        assert 'error' in result

    def test_yield_only_valid_for_attacker(self):
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K'), c('7')]
        e.hands['p1'] = [c('9')]

        play(e, 'p0', c('K'))        # chain started, p1 is responder
        result = e.yield_trick('p0') # p0 is NOT attacker at this moment
        assert 'error' in result


# ── sacrifice ─────────────────────────────────────────────────────────────────

class TestSacrifice:
    def test_attacker_sacrifices_when_no_capturing_card(self):
        """Attacker has no 7 or base-rank card → sacrifice is allowed."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('K', 'T'), c('9')]  # K to capture, then 9 to sacrifice

        play(e, 'p0', c('K'))
        play(e, 'p1', c('K', 'T'))     # p1 captures, p1 = attacker (has only '9' left)
        assert e.chain.attacker_id == 'p1'

        # p1 has only '9', no capturing card → sacrifice
        play(e, 'p1', c('9'))          # sacrifice goes through
        assert e.chain.phase == 'responder_play'
        assert len(e.chain.pile) == 3

    def test_cannot_sacrifice_when_has_capturing_card(self):
        """If attacker has a capturing card, playing a non-capturing card is rejected."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('K', 'T'), c('7'), c('9')]

        play(e, 'p0', c('K'))
        play(e, 'p1', c('K', 'T'))    # p1 captures, p1 = attacker (has 7 and 9)
        assert e.chain.attacker_id == 'p1'

        result = e.play_card('p1', c('9').to_dict())  # 9 is not capturing
        assert 'error' in result

    def test_sacrifice_followed_by_responder_capture(self):
        """After a sacrifice, responder can still capture and become attacker."""
        e = fresh_engine(opener='p0')
        # p0 needs a spare card so capturing K,T doesn't empty the hand
        # (empty hand → auto-end, preventing the assertion below)
        e.hands['p0'] = [c('K'), c('K', 'T'), c('9', 'T')]
        e.hands['p1'] = [c('K', 'Z'), c('9')]

        play(e, 'p0', c('K'))         # lead K
        play(e, 'p1', c('K', 'Z'))   # p1 captures, p1 = attacker, only '9' left
        play(e, 'p1', c('9'))         # sacrifice: p1 has no capturing card
        # p0 responds with K,T (base rank K) → p0 captures
        play(e, 'p0', c('K', 'T'))   # p0 becomes attacker
        assert e.chain.attacker_id == 'p0'
        assert len(e.chain.pile) == 4

    def test_sacrifice_then_responder_misses(self):
        """After sacrifice, if responder also misses, attacker (sacrificer) takes pile."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K'), c('9', 'T')]
        e.hands['p1'] = [c('K', 'T'), c('8')]   # will sacrifice 8

        play(e, 'p0', c('K'))         # lead K
        play(e, 'p1', c('K', 'T'))   # p1 captures → attacker
        play(e, 'p1', c('8'))         # sacrifice (no capturing card left in p1's hand)
        play(e, 'p0', c('9', 'T'))   # p0 responds with 9 (not capturing) → chain ends
        # p1 was attacker (last capturer) → p1 takes pile
        assert e.chain is None
        assert len(e.collected['p1']) == 4
        assert e.opener == 'p1'


# ── refill & draw pile ────────────────────────────────────────────────────────

class TestRefill:
    def test_both_players_refill_after_chain(self):
        """After a 2-card chain both players should have HAND_SIZE cards again."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('9')]
        e.draw_pile = [c('A'), c('10'), c('Q'), c('J'),   # 4 for p0
                       c('8'), c('7'), c('Q', 'T'), c('J', 'T')]  # 4 for p1

        play(e, 'p0', c('K'))
        play(e, 'p1', c('9'))   # no capture → p0 takes pile, refill triggers
        assert len(e.hands['p0']) == HAND_SIZE
        assert len(e.hands['p1']) == HAND_SIZE

    def test_winner_draws_first(self):
        """Chain winner draws from the pile before the loser."""
        e = fresh_engine(opener='p0')
        # Give both players a spare card so neither ends up empty after the
        # 2-card chain (which would trigger end-game and flush hands to collection)
        unique = c('A', 'M')
        e.hands['p0'] = [c('K'), c('8')]
        e.hands['p1'] = [c('9'), c('J')]
        e.draw_pile = [unique]   # only 1 card left in pile

        play(e, 'p0', c('K'))
        play(e, 'p1', c('9'))   # p0 wins, p0 draws first
        # p0 had 1 spare, drew the unique card; p1 had 1 spare, drew nothing
        assert unique in e.hands['p0']
        assert unique not in e.hands['p1']

    def test_no_refill_when_draw_pile_empty(self):
        """When the draw pile is empty, finished hands stay empty."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('9')]
        e.draw_pile = []

        play(e, 'p0', c('K'))
        play(e, 'p1', c('9'))
        # Both played their last card; draw pile empty → game ends
        assert e.finished
        assert e.hands['p0'] == []
        assert e.hands['p1'] == []

    def test_partial_refill_when_draw_pile_nearly_empty(self):
        """When draw pile can't fill both hands, each gets what's available."""
        e = fresh_engine(opener='p0')
        # Start with 2 cards each; play 1 each (leaving 1 each), then refill
        # with only 1 pile card — p0 (winner) draws it, p1 gets nothing
        e.hands['p0'] = [c('K'), c('8')]
        e.hands['p1'] = [c('9'), c('J')]
        e.draw_pile = [c('A')]   # only 1 card

        play(e, 'p0', c('K'))
        play(e, 'p1', c('9'))   # p0 wins; p0 has [8], p1 has [J]
        # after refill: p0 gets 1 card (now 2 total), p1 gets 0 (pile empty)
        total_in_hands = len(e.hands['p0']) + len(e.hands['p1'])
        # p0: [8, A] = 2, p1: [J] = 1 → total = 3
        assert total_in_hands == 3

    def test_game_ends_when_both_hands_empty(self):
        """After the last chain, if no cards remain anywhere, finished = True."""
        e = fresh_engine(opener='p0')
        e.hands['p0'] = [c('K')]
        e.hands['p1'] = [c('9')]
        e.draw_pile = []

        play(e, 'p0', c('K'))
        play(e, 'p1', c('9'))
        assert e.finished is True


# ── full game simulation ──────────────────────────────────────────────────────

class TestFullGame:
    def _run_game(self, seed: int) -> ClassicGameEngine:
        random.seed(seed)
        e = ClassicGameEngine('SIM')
        e.start_game(['p0', 'p1'])
        while not e.finished:
            pid = e.chain.attacker_id if (e.chain and e.chain.phase == 'attacker_play') \
                else (e.chain.responder_id if e.chain else e.opener)
            make_valid_move(e, pid)
        return e

    def test_total_points_always_84(self):
        for seed in range(20):
            e = self._run_game(seed)
            total = e._points('p0') + e._points('p1')
            assert total == 84, f"seed={seed}: total={total}"

    def test_all_cards_collected(self):
        """Every card in the deck ends up in some player's collection."""
        for seed in range(10):
            e = self._run_game(seed)
            collected = e.collected['p0'] + e.collected['p1']
            assert len(collected) == 32, f"seed={seed}: {len(collected)} cards collected"

    def test_hands_and_pile_empty_at_finish(self):
        for seed in range(10):
            e = self._run_game(seed)
            assert not e.hands['p0']
            assert not e.hands['p1']
            assert not e.draw_pile
            assert e.chain is None
