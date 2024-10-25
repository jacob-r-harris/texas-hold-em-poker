from player import Player

import random

import time


class AI(Player):

    def __init__(self, funds, ID):
        # Generates Ai with random name from list of names
        super().__init__(funds,
                         random.choice(["Not A Robot", "Poker Face", "Royally Flushed", "0100000101001001", "Gonch"]),
                         ID)

        # Tells the main code that this is an AI
        self.stats["AI"] = True

    def listen(self):  # "Listens" to the code to see when it can make a move
        while True:
            if self.stats["SB"] is not None:  # If they are the small blind, they wait a short amount of time and put down a SB bet
                time.sleep(random.choice(range(3, 13)))  # Arbitrary numbers to make it seem more human

                percentage = "0.0" + str(
                    random.choice(range(2, 7)))  # Percentage amount of their funds to put as small blind
                return float(percentage)


if __name__ == "__main__":
    p1 = AI(1000)

    p1.stats["SB"] = True

    print(p1.listen())
