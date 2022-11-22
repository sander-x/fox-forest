import pytest
import foxforest
import numpy as np

from foxforest import __version__
from foxforest.player import Player
from foxforest.player import AIPlayer
from foxforest.game import Card
from foxforest.game import Game
from foxforest.game import Play
from foxforest.game import Deck


def test_version():
    assert __version__ == "0.1.0"


class TestPlayer:
    @pytest.fixture
    def basic_player(self) -> Player:

        player = Player(name="test_name")
        return player

    def test_sort_hand(self, basic_player):

        basic_player.hand = [Card(11, "K"), Card(3, "B"), Card(5, "B"), Card(6, "M")]
        basic_player.sort_hand()

        assert [[x.value, x.suit] for x in basic_player.hand] == [
            [3, "B"],
            [5, "B"],
            [11, "K"],
            [6, "M"],
        ]

    def test_add_to_hand(self, basic_player):

        card = Card(4, "M")
        basic_player.add_to_hand([card])

        assert card in basic_player.hand

    def test_add_to_tricks(self, basic_player):

        trick = [Card(4, "M"), Card(10, "K")]

        basic_player.add_to_tricks_won(trick)

        assert trick in basic_player.tricks_won

    def test_get_valid_moves(self, basic_player):

        game = Game(basic_player, basic_player)

        card = Card(4, "M")

        basic_player.hand = [card]

        valid_moves = basic_player.get_valid_moves(game)

        assert valid_moves[0].card == card


class TestAIPlayer:
    @pytest.fixture
    def ai_player(self) -> Player:

        ai_player = AIPlayer(name="test_name")
        return ai_player

    def test_encode_cards(self, ai_player):

        ai_player.hand = [Card(11, "K"), Card(3, "B"), Card(5, "B"), Card(6, "M")]

        encoded_cards = np.zeros(33)
        encoded_cards[10] = 1
        encoded_cards[13] = 1
        encoded_cards[15] = 1
        encoded_cards[27] = 1

        np.testing.assert_array_equal(
            encoded_cards, ai_player.encode_cards(ai_player.hand)
        )


class TestGame:
    @pytest.fixture
    def test_game(self) -> Game:
        game = Game(Player(name="player1"), Player(name="player2"))
        game.setup_game()
        return game

    @pytest.fixture
    def test_play(self) -> Play:

        play = Play(Player(name="test_player"), Card(9, "K"))

        return play

    # define various hands that are not valid plays
    @pytest.mark.parametrize(
        "first_card, second_card, hand",
        [
            (Card(7, "K"), Card(9, "K"), [Card(8, "K")]),
            (Card(7, "K"), Card(9, "K"), [Card(8, "K"), Card(9, "M")]),
            (Card(11, "K"), Card(9, "K"), [Card(9, "K"), Card(10, "K")]),
            (Card(11, "K"), Card(2, "K"), [Card(4, "K"), Card(2, "K"), Card(1, "K")]),
        ],
    )
    def test_is_valid_play_second_card(
        self, test_game, test_play, first_card, second_card, hand
    ):

        test_game.decree_card = Card(3, "K", None)

        test_game.player_turn = test_game.player2

        test_game.current_trick_cards.append(first_card)
        test_game.player2.hand = hand

        test_play = Play(test_game.player2, second_card, use_ability=False)

        assert test_game.is_valid_play(test_play) == False

    # define various hands that are valid plays involving 11 played first
    @pytest.mark.parametrize(
        "first_card, second_card, hand",
        [
            (Card(11, "K"), Card(9, "K"), [Card(3, "K"), Card(5, "K"), Card(9, "K")]),
            (Card(11, "K"), Card(1, "K"), [Card(8, "K"), Card(1, "K")]),
        ],
    )
    def test_is_valid_play_eleven_ability(
        self, test_game, test_play, first_card, second_card, hand
    ):

        test_game.decree_card = Card(10, "K", None)

        test_game.player_turn = test_game.player2

        test_game.current_trick_cards.append(first_card)
        test_game.player2.hand = hand

        test_play = Play(test_game.player2, second_card, use_ability=False)

        assert test_game.is_valid_play(test_play) == True

    def test_is_valid_play_three_ability(self, test_game, test_play):

        test_game.decree_card = Card(1, "K", None)

        test_game.player1.hand = [Card(3, "K"), Card(8, "B")]

        test_play = Play(
            test_game.player1,
            test_game.player1.hand[0],
            use_ability=True,
            ability_card=test_game.player1.hand[1],
        )

        assert test_game.is_valid_play(test_play) == True

    def test_determine_trick_winner_trump(self, test_game):

        test_game.decree_card = Card(1, "K", None)

        # trump suit beats higher value
        test_game.current_trick_cards = [
            Card(5, "K", test_game.player1),
            Card(10, "B", test_game.player2),
        ]

        assert test_game.determine_trick_winner() == test_game.player1

    def test_determine_trick_winner_non_trump(self, test_game):
        # higher value wins for non-trump suit
        test_game.decree_card = Card(1, "K", None)

        test_game.current_trick_cards = [
            Card(5, "B", test_game.player1),
            Card(10, "B", test_game.player2),
        ]

        assert test_game.determine_trick_winner() == test_game.player2

    def test_determine_trick_winner_nines(self, test_game):
        # if one 9 is played counts as trump
        test_game.decree_card = Card(1, "K", None)

        test_game.current_trick_cards = [
            Card(9, "M", test_game.player1),
            Card(10, "B", test_game.player2),
        ]

        assert test_game.determine_trick_winner() == test_game.player1

        test_game.current_trick_cards = [
            Card(9, "M", test_game.player1),
            Card(8, "K", test_game.player2),
        ]

        assert test_game.determine_trick_winner() == test_game.player1

        test_game.current_trick_cards = [
            Card(9, "M", test_game.player1),
            Card(9, "K", test_game.player2),
        ]

        assert test_game.determine_trick_winner() == test_game.player2

    # check three ability switches decree card
    def test_execute_play_three_ability(self, test_game):

        decree = Card(1, "K")
        hand = [Card(3, "K"), Card(8, "B")]

        test_game.decree_card = decree
        test_game.player1.hand = hand

        test_play = Play(
            test_game.player1,
            hand[0],
            use_ability=True,
            ability_card=hand[1],
        )

        test_game.execute_play(test_play)

        assert test_game.decree_card == Card(8, "B")

        assert test_game.player1.hand == [decree]

    def test_execute_play_five_ability(self, test_game):

        decree = Card(1, "K")
        hand = [Card(5, "K"), Card(8, "B")]
        deck = [Card(9, "M"), Card(8, "M")]

        test_game.decree_card = decree
        test_game.player1.hand = hand
        test_game.deck.cards = deck

        # implement request_discard method to return first card in hand
        def return_first(self, game_played: "Game"):

            return self.hand[0]

        test_game.player1.request_discard = return_first.__get__(
            test_game.player1, Player
        )

        test_play = Play(test_game.player1, hand[0])

        test_game.execute_play(test_play)

        card_to_discard = test_game.player1.request_discard(self)
        discard_play = Play(test_game.player1, card_to_discard)

        test_game.execute_discard(discard_play)

        assert test_game.deck.cards[-1] == Card(8, "B")
        assert test_game.player1.hand == [Card(9, "M")]
