import streamlit as st
import foxforest as ff
import streamlit as st
import pandas as pd
import numpy as np

# set up the players and game objects as persistent variables

if "game" not in st.session_state:

    p1 = ff.player.StreamlitPlayer("Human")
    p2 = ff.player.RandomPlayer("Computer 1")
    game = ff.Game(p1, p2)

    setattr(st.session_state, "game", game)

if "game_state" not in st.session_state:

    setattr(st.session_state, "game_state", "not_initialised")

if "proposed_play" not in st.session_state:

    setattr(st.session_state, "proposed_play", None)


def st_select_card_button(play: ff.game.Play, game: ff.Game, state) -> None:

    # switch input to cards instead of play
    # give option to not switch decree card

    if state.game_state == "select_decree_switch":

        # make something if user doesn't want to switch
        if play != None:
            state.proposed_play.ability_card = play.card
            state.proposed_play.use_ability = True

        if not game.is_valid_play(state.proposed_play):

            state.game_state = "invalid_play_selected"
            state.proposed_play = None
            return None

        else:

            game.step(state.proposed_play)
            state.game_state = "round_playing"
            state.proposed_play = None

            return None

    elif state.game_state == "select_card_to_discard":

        if play.card not in game.player1.hand:

            state.game_state = "invalid_play_selected"
            return None

        else:

            game.step(play)
            state.game_state = "round_playing"

            return None

    else:

        if game.is_valid_play(play):

            if play.card.value == 3:

                state.proposed_play = play

                state.game_state = "switch_decree_or_not"

                return None

            elif play.card.value == 5:

                state.game_state = "select_card_to_discard"

                game.step(play)

                return None

            else:

                game.step(play)

                return None

        else:
            state.game_state = "invalid_play_selected"
            return None


def st_start_new_game(game: ff.Game, state) -> None:

    game.setup_game()
    state.game_state = "round_playing"


# for easier reference
game = st.session_state.game
state = st.session_state

st.title("Play a game of the fox in the forest")

st.write(state.game_state)

nr_of_cards = len(game.player1.hand)

# print decree card, cards involved in last trick, and card played by opponent in current trick (if applicable)
if game.round_done == False:
    st.write(f"The decree cards is {game.decree_card.value} {game.decree_card.suit}")

    if game.turns > 0:

        last_trick = game.played_tricks[-1]
        st.write(
            f"Last turn {last_trick[0].value} {last_trick[0].suit} and {last_trick[1].value} {last_trick[1].suit} were played"
        )

    if game.player_turn == game.player1 and game.current_trick_cards == []:
        st.write("Your turn, play the first card:")

    elif state.game_state == "select_card_to_discard":

        st.write("You have received an extra card, select a card to discard:")

    elif game.current_trick_cards != []:
        played_card = game.current_trick_cards[0]

        st.write(f"Your opponent played {played_card.value} {played_card.suit}:")


# print hand

if game.round_done == False and state.game_state != "switch_decree_or_not":
    st.write("Your hand:")

    if nr_of_cards > 0:
        hand_column = st.columns([1 for x in range(nr_of_cards)])
    else:
        hand_column = []

    for card, column in zip(game.player1.hand, hand_column):

        label = f"{card.value} {card.suit}"
        play = ff.game.Play(game.player1, card)

        column.button(
            label,
            key=None,
            help=None,
            on_click=st_select_card_button,
            args=[play, game, state],
            kwargs=None,
            disabled=False,
        )

if state.game_state == "invalid_play_selected":

    st.write("You cannot play that card")

    setattr(state, "game_state", "round_playing")

elif state.game_state == "select_decree_switch":

    st.write("Select card to switch with the decree card")

elif state.game_state == "select_card_to_discard":

    st.write("Select card to discard")

# If player needs to decide whether to switch decree or not
if game.round_done == False and state.game_state == "switch_decree_or_not":

    st.write(f"Do you want to switch the decree card with a card from your hand?")

    setattr(state, "game_state", "select_decree_switch")

    hand_column = st.columns([1, 1])

    hand_column[0].button(
        "Yes",
        kwargs=None,
        disabled=False,
    )

    hand_column[1].button(
        "No",
        on_click=st_select_card_button,
        args=[None, game, state],
        kwargs=None,
        disabled=False,
    )


# misc info
st.write(f"Tricks won: {len(game.player1.tricks_won)}")
st.write(f"Turn: {game.turns}")

st.button("Start new game", on_click=st_start_new_game, args=[game, state])

if game.round_done == True and state.game_state != "not_initialised":

    p1_points, p2_points = game.determine_points_end_round()

    st.write(
        f"The round is over, you scored {p1_points} points, while the computer scored {p2_points}"
    )


if state.proposed_play != None:

    st.write(f"card: {state.proposed_play.card.value} {state.proposed_play.card.suit}")

    if state.proposed_play.ability_card != None:

        st.write(
            f", switch: {state.proposed_play.ability_card.value} {state.proposed_play.ability_card.suit}"
        )
