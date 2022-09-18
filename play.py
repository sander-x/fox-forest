from importlib.metadata import files
import foxforest as ff


# p1 = ff.player.HumanPlayer("Human")
p1 = ff.player.RandomPlayer("Computer 1")
p2 = ff.player.RandomPlayer("Computer 2")

game = ff.Game(p1, p2)
game.play_game()
