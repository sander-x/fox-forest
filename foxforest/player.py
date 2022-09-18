from __future__ import annotations


import foxforest.game as game


from typing import List
import numpy as np
import numpy.typing as npt
import random


############
#
# Player classes
#
############


class Player:
    def __init__(self, name: str):

        self.hand: List["game.Card"] = []
        self.name = name
        self.tricks_won: List[List["game.Card"]] = []

    def sort_hand(self) -> None:

        self.hand.sort(key=lambda x: x.value)
        self.hand.sort(key=lambda x: x.suit)
        return None

    def add_to_hand(self, cards: List["game.Card"]) -> None:

        for card in cards:
            self.hand.append(card)

    def add_to_tricks_won(self, trick: List["game.Card"]) -> None:

        self.tricks_won.append(trick)

    def get_valid_moves(self, game_being_played: "game.Game") -> List["game.Play"]:

        proposed_moves = [game.Play(self, card) for card in self.hand]

        valid_moves = [
            move for move in proposed_moves if game_being_played.is_valid_play(move)
        ]

        return valid_moves

    def request_play(self, game: "game.Game") -> "game.Play":

        pass

    def request_discard(self, game: "game.Game") -> "game.Card":

        pass


class RandomPlayer(Player):
    def request_play(self, game_being_played: "game.Game") -> "game.Play":

        valid_moves = self.get_valid_moves(game_being_played)

        return random.choice(valid_moves)

    def request_discard(self, game_being_played: "game.Game") -> "game.Card":

        return random.choice(self.hand)


class AIPlayer(Player):
    def request_play(self, game_being_played: "game.Game") -> "game.Play":

        valid_moves = self.get_valid_moves(game_being_played)

        return random.choice(valid_moves)

    def get_gamestate(self, game_being_played: "game.Game") -> npt.ArrayLike:

        # state encoding consists of
        # - encoded hand cards
        # - played cards (separate own vs other played?)
        # - turn nr
        # - nr tricks won
        # - opponent out of certain suit?

        pass

    def encode_cards(self, cards: List["game.Card"]) -> npt.ArrayLike:

        # encode cards to array, order of suits is 'K', 'B', 'M'

        state = np.array([0 for _ in range(33)])

        for card in cards:

            pos = card.value - 1

            if card.suit == "B":

                pos = pos + 11

            if card.suit == "M":

                pos = pos + 22

            state[pos] = 1

        return state

    def decode_cards(self, encoded_cards: npt.ArrayLike) -> List["game.Card"]:

        pass

    def request_discard(self, game_being_played: "game.Game") -> "game.Card":

        return random.choice(self.hand)


class HumanPlayer(Player):
    def request_play(self, game_being_played: "game.Game") -> "game.Play":

        valid_moves = self.get_valid_moves(game_being_played)

        print([[play.card.value, play.card.suit] for play in valid_moves])
        chosen_move = int(input("Choose a card to play:")) - 1

        chosen_play = valid_moves[int(chosen_move)]

        if chosen_play.card.value == 3:

            use_ability = input("Do you want to exchange the decree card? (Y/N):")

            if use_ability.lower() == "y":

                chosen_play.use_ability == True

                print([[card.value, card.suit] for card in self.hand])

                ability_card_nr = int(input("game.Card to exchange from hand:")) - 1

                ability_card = self.hand[ability_card_nr]

                chosen_play.ability_card = ability_card

        return chosen_play

    def request_discard(self, game_being_played: "game.Game") -> "game.Card":

        print([[card.value, card.suit] for card in self.hand])
        chosen_move_nr = input("Choose a card to discard:")
        chosen_move = int(chosen_move_nr) - 1

        return self.hand[int(chosen_move)]
