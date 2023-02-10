from importlib.metadata import files
import foxforest as ff


p1 = ff.player.HumanPlayer("Human")
p2 = ff.player.RandomPlayer("Computer")

game = ff.Game(p1, p2)
game.play_game()
