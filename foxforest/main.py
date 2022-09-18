for i in range(5):  # this comment has too many spaces
    print(i)  # this line has 6 space indentation.

import numpy as np

encoded_cards = np.zeros(33)
encoded_cards[10] = 1
encoded_cards[13] = 1
encoded_cards[15] = 1
encoded_cards[27] = 1

print(encoded_cards)
