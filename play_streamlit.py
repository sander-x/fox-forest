import streamlit as st
import foxforest as ff
import streamlit as st
import pandas as pd
import numpy as np

# set up the players and game objects as persistent variables

if 'game' not in st.session_state:
    
    p1 = ff.player.StreamlitPlayer("Human")
    p2 = ff.player.RandomPlayer("Computer 1")   
    game = ff.Game(p1, p2)
          
    st.session_state.game = game
    
    
# for easier reference
game = st.session_state.game 

st.title('Play a game of the fox in the forest')

nr_of_cards = len(game.player1.hand)

# print decree card, cards involved in last trick, and card played by opponent in current trick (if applicable)
if game.round_done == False:    
    st.write(f"The decree cards is {game.decree_card.value} {game.decree_card.suit}")
    
    if game.turns > 0:
            
        last_trick = game.played_tricks[-1]
        st.write(f"Last turn {last_trick[0].value} {last_trick[0].suit} and {last_trick[1].value} {last_trick[1].suit} were played")    

    if game.player_turn == game.player1 and game.current_trick_cards == []:
        st.write("Your turn, play the first card:")
        
    elif game.current_trick_cards != []:
        played_card = game.current_trick_cards[0]
                
        st.write(f"Your opponent played {played_card.value} {played_card.suit}:")
        
    

# print hand
st.write("Your hand:")

if nr_of_cards > 0:
    hand_column = st.columns([1 for x in range(nr_of_cards)])
else:
    hand_column = []

for card, column in zip(game.player1.hand, hand_column):         
        
    label = f"{card.value} {card.suit}"    
    play = ff.game.Play(game.player1, card)
    
    column.button(label, key=None, help=None, on_click=game.step, args=[play], kwargs=None, disabled=False)
    
    
# misc info     
st.write(f"Tricks won: {len(game.player1.tricks_won)}")

st.button("Start new game", on_click=game.setup_game)
st.write(f"Turn: {game.turns}")

if game.round_done == True:
    
    p1_points, p2_points = game.determine_points_end_round()
    
    st.write(f"The round is over, you scored {p1_points} points, while the computer scored {p2_points}")