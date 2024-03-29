from __future__ import annotations

from typing import Optional
from typing import List

import random
from dataclasses import dataclass

from .player import Player


class InvalidPlay(Exception):
    pass


@dataclass(order=True)
class Card:
    value: int
    suit: str
    played_by: Optional[Player] = None

    def __str__(self):
        return f"{self.value}{self.suit}"


class Play:
    def __init__(
        self,
        player: Player,
        card: Card,
        use_ability: bool = False,
        ability_card: Card = None,
    ):

        self.player = player
        self.card = card
        self.use_ability = use_ability
        self.ability_card = ability_card


class Deck:
    def __init__(self):
        self.cards = []

    def __str__(self):

        output = ""

        for card in self.cards:
            output.append(str(card) + "\n")

        return output

    def create_deck(self) -> None:

        cards = []

        for value in range(1, 12):
            for suit in ["K", "B", "M"]:
                cards.append(Card(value, suit))

        self.cards = cards

    def shuffle_deck(self) -> None:

        random.shuffle(self.cards)

    def draw_top_n_cards(self, n: int) -> List[Card]:

        drawn_cards: List[Card] = []

        while len(drawn_cards) < n:
            drawn_cards.append(self.cards.pop(0))

        return drawn_cards


class Game:
    def __init__(self, player1: Player, player2: Player):
        self.turns = 0
        self.deck: Deck
        self.player1 = player1
        self.player2 = player2

        self.player_turn: Player = player1

        self.decree_card: Card
        self.current_trick_cards: List[Card] = []
        self.round_done: bool = True

        self.played_tricks: List[List[Card]] = []

    def setup_game(self):

        self.deck = Deck()
        self.deck.create_deck()
        self.deck.shuffle_deck()

        self.current_trick_cards = []

        # define players and deal cards
        self.player1.hand = []
        self.player2.hand = []
        self.player1.tricks_won = []
        self.player2.tricks_won = []
        self.player1.add_to_hand(self.deck.draw_top_n_cards(13))
        self.player2.add_to_hand(self.deck.draw_top_n_cards(13))

        self.player1.sort_hand()
        self.player2.sort_hand()

        # assign top card as suit card
        self.decree_card = self.deck.draw_top_n_cards(1)[0]

        # set whose turn it is
        self.player_turn = self.player1
        self.turns = 0

        # used in step() to signify card to discard must be provided
        self.wait_for_discard = False

        # initiate round
        self.round_done = False

    def change_turn(self) -> Player:

        if self.player_turn == self.player1:

            self.player_turn = self.player2
            return self.player2

        else:
            self.player_turn = self.player1
            return self.player1

    def is_valid_play(self, play: Play) -> bool:

        card = play.card
        hand = play.player.hand
        player = play.player

        # check it is the turn of the player
        if self.player_turn != player:
            return False

        # check card is in the hand of the player
        if card not in hand:
            return False

        # check if a 3 is played and ability used, that that card is in hand player
        if card.value == 3 and play.use_ability == True:

            if (play.ability_card not in hand) or (play.ability_card == play.card):
                return False

        # if this is the first card to be played
        if len(self.current_trick_cards) == 0:

            return True

        # if second card to be played
        else:

            # if suit matches first card play is valid
            if self.current_trick_cards[0].suit == card.suit:

                # exception: if 11 was played, check it is 1 or highest
                if self.current_trick_cards[0].value == 11:

                    # check value is 1 or no higher card exists in hand
                    if card.value != 1 and not all(
                        card.suit != x.suit or card.value >= x.value for x in hand
                    ):

                        return False

                return True

            # if not, verify no suit matching first card in hand
            else:

                return self.current_trick_cards[0].suit not in [x.suit for x in hand]

    def execute_play(self, play: Play) -> None:

        if not self.is_valid_play(play):

            raise InvalidPlay("Proposed Play is not valid")

        setattr(play.card, "played_by", play.player)

        self.current_trick_cards.append(play.card)
        play.player.hand.remove(play.card)

        # if 3 played and ability used, exhange decree card with ability card
        if play.card.value == 3 and play.use_ability:

            assert type(play.ability_card) == Card
            play.player.add_to_hand([self.decree_card])
            self.decree_card = play.ability_card
            play.player.hand.remove(play.ability_card)

        # if 5 is played, add card to hand player and request_discard
        if play.card.value == 5:

            play.player.add_to_hand(self.deck.draw_top_n_cards(1))

            # TODO set to false again in next block
            self.wait_for_discard = True

            return None

        # if first card played, change turn
        if len(self.current_trick_cards) == 1:

            self.change_turn()

    def execute_discard(self, play: Play) -> None:

        if play.card not in play.player.hand:

            raise InvalidPlay("Suggested card to discard not in hand")

        play.player.hand.remove(play.card)

        self.deck.cards.append(play.card)

        self.wait_for_discard = False

        self.change_turn()

        return None

    def determine_trick_winner(self) -> Player:

        card_1 = self.current_trick_cards[0]
        card_2 = self.current_trick_cards[1]

        assert isinstance(card_1.played_by, Player)
        assert isinstance(card_2.played_by, Player)

        trump_suit = self.decree_card.suit

        # if only one 9 is played, counts as trump
        if card_1.value == 9 and card_2.value != 9:
            # other card also trump suit, highest wins
            if card_2.suit == trump_suit:
                if card_1.value > card_2.value:
                    return card_1.played_by
                else:
                    return card_2.played_by
            else:
                return card_1.played_by

        if card_1.value != 9 and card_2.value == 9:
            # other card also trump suit, highest wins
            if card_1.suit == trump_suit:
                if card_1.value > card_2.value:
                    return card_1.played_by
                else:
                    return card_2.played_by
            else:
                return card_2.played_by

        # if equal suit, highest wins
        if card_1.suit == card_2.suit:
            if card_1.value > card_2.value:
                return card_1.played_by
            else:
                return card_2.played_by

        # if card 2 is trump it wins
        if card_2.suit == self.decree_card.suit:
            return card_2.played_by

        # else first card played wins, since suit was not matched
        return card_1.played_by

    def determine_points_end_round(self) -> List[int]:

        # count sevens won by each player
        p1_points = sum(
            1 for hand in self.player2.tricks_won for card in hand if card.value == 7
        )
        p2_points = sum(
            1 for hand in self.player2.tricks_won for card in hand if card.value == 7
        )

        trick_points = {
            0: [6, 0],
            1: [6, 0],
            2: [6, 0],
            3: [6, 0],
            4: [1, 6],
            5: [2, 6],
            6: [3, 6],
            7: [6, 3],
            8: [6, 2],
            9: [6, 1],
            10: [0, 6],
            11: [0, 6],
            12: [0, 6],
            13: [0, 6],
        }

        p1_tricks = len(self.player1.tricks_won)

        end_of_round_points = trick_points[p1_tricks]

        p1_points = p1_points + end_of_round_points[0]
        p2_points = p2_points + end_of_round_points[1]

        return [p1_points, p2_points]

    def play_game(self) -> None:
        def print_hand(hand: List[Card]):

            string = ""
            for card in hand:
                string = string + str(card.value) + " " + card.suit + ", "
            print(string)

        self.setup_game()

        print(
            "Decree card is: "
            + str(self.decree_card.value)
            + str(self.decree_card.suit)
        )

        print("Player 1 hand:")
        print_hand(self.player1.hand)

        print("Player 2 hand:")
        print_hand(self.player2.hand)

        while self.turns < 13:

            # both players make their turns
            play1 = self.player_turn.request_play(self)
            self.execute_play(play1)

            if self.wait_for_discard == True:
                card_to_discard = play1.player.request_discard(self)
                discard_play = Play(play1.player, card_to_discard)
                self.execute_discard(discard_play)

            print(
                f"Player {play1.player.name} plays: {play1.card.value} {play1.card.suit}"
            )

            play2 = self.player_turn.request_play(self)
            self.execute_play(play2)

            if self.wait_for_discard == True:
                card_to_discard = play2.player.request_discard(self)
                discard_play = Play(play2.player, card_to_discard)
                self.execute_discard(discard_play)

            print(
                f"Player {play2.player.name} plays: {play2.card.value} {play2.card.suit}"
            )

            # winner is determined
            winner = self.determine_trick_winner()

            print(f"Winner is: {winner.name}")

            # cards added to hand and turn given to winner
            self.played_tricks.append(self.current_trick_cards)
            winner.add_to_tricks_won(self.current_trick_cards)

            self.player_turn = winner

            # unless 1 was played but did not win trick
            for card in self.current_trick_cards:
                assert isinstance(card.played_by, Player)
                if card.value == 1 and card.played_by != winner:
                    self.player_turn = card.played_by

            self.current_trick_cards = []

            self.turns += 1

        self.round_done = True

        print(f"Player 1 won {len(self.player1.tricks_won)} tricks")
        print(f"Player 2 won {len(self.player2.tricks_won)} tricks")

        print(f"Final points {self.determine_points_end_round()}")

    def step(self, play: Play) -> None:
        """Steps through one round of play,
        executing the passed Play, until it is player1's turn again.
        In this way it is possible to play a game using direct function calls as input from the player

        Args:
            play (Play): _description_
        """

        # if waiting for discard from player execute discard and return
        if self.wait_for_discard == True:

            self.execute_discard(play)

        else:

            self.execute_play(play)

            # if waiting for discard, return and wait for next play
            if self.wait_for_discard == True:

                return None

        # If this was first card played, player2 needs to play a card
        if len(self.current_trick_cards) == 1:

            play2 = self.player_turn.request_play(self)
            self.execute_play(play2)

            # if 5 was played, request discard
            if self.wait_for_discard == True:

                card_to_discard = self.player_turn.request_discard(self)
                discard_play = Play(self.player_turn, card_to_discard)

                self.execute_discard(discard_play)

        # winner is determined
        winner = self.determine_trick_winner()

        # cards added to hand and turn given to winner
        self.played_tricks.append(self.current_trick_cards)
        winner.add_to_tricks_won(self.current_trick_cards)

        self.player_turn = winner

        # unless 1 was played but did not win trick
        for card in self.current_trick_cards:
            assert isinstance(card.played_by, Player)
            if card.value == 1 and card.played_by != winner:
                self.player_turn = card.played_by

        self.current_trick_cards = []

        self.turns += 1

        # If it is player2's turn, make them play the first card

        if self.player_turn == self.player2 and self.turns < 13:

            play2 = self.player2.request_play(self)
            self.execute_play(play2)

            # if 5 was played, request discard
            if self.wait_for_discard == True:

                card_to_discard = self.player_turn.request_discard(self)
                discard_play = Play(self.player_turn, card_to_discard)

                self.execute_discard(discard_play)

        if self.turns >= 13:

            self.round_done = True

        return None


def print_deck(deck: Deck):

    for card in deck.cards:
        print_card(card)


def print_card(card: Card):

    print(str(card.value) + " " + card.suit)


def print_hand(hand: List[Card]):

    for card in hand:
        print_card(card)
