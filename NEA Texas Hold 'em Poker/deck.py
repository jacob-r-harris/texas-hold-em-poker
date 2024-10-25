import random


class Deck:

    def __init__(self):
        self.cards = []

        for suit in "schd":
            for value in range(0, 13):
                if value == 0:
                    self.cards.append("a" + suit)

                elif 0 < value < 10:
                    self.cards.append(str(value + 1) + suit)

                elif value == 10:
                    self.cards.append("j" + suit)

                elif value == 11:
                    self.cards.append("q" + suit)

                elif value == 12:
                    self.cards.append("k" + suit)

    def printDeck(self):
        print(self.cards)

    def deal(self, playerlist, amountPerPlayer):

        for p in playerlist:
            p.stats["Hand"] = random.sample(self.cards, amountPerPlayer)
            for c in p.stats["Hand"]:
                self.cards.remove(c)


if __name__ == "__main__":
    d = Deck()

    d.printDeck()

    p1 = {"Name": "Bob", "Hand": []}

    p2 = {"Name": "John Doe", "Hand": []}

    p3 = {"Name": "Chell", "Hand": []}

    p4 = {"Name": "Stormzy", "Hand": []}

    playerlist = [p1, p2, p3, p4]

    d.deal(playerlist, 2)

    print(p1)
    print(p2)
    print(p3)
    print(p4)

    d.printDeck()