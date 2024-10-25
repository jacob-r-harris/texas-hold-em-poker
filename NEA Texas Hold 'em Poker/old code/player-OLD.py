class Player:

    def __init__(self, funds, name):
        self.name = name

        self.money = funds

        self.id = 0

        self.stats = {"ID": self.id, "Name": self.name, "Cash": self.money, "Hand": [], "Bet": 0, "SB": ""}

        self.b = 0

        self.r = 0

    def fold(self):
        self.stats["Hand"] = []

    def call(self, prev_player):
        self.stats["Bet"] = prev_player.stats["Bet"]

    def pokerRaise(self, prev_player):
        self.r = int(input("Raise to: "))

        if self.r < prev_player.stats["Bet"] * 2:
            print("Invalid amount\n"
                  "Raise must be at least double previous players bet (" + str(prev_player.stats["Bet"]) + ")")

            self.pokerRaise(prev_player)

        elif self.r > self.stats["Cash"]:
            print("Invalid amount\n"
                  "You can't raise to more money than you have! (" + str(self.stats["Cash"]) + ")")

        else:
            self.stats["Bet"] = self.r

    def bet(self, minbet):
        self.b = int(input("Bet: "))

        if self.b < minbet:
            print("Invalid amount\n"
                  "Minimum bet is", str(minbet))

            self.bet(minbet)

        else:
            self.stats["Bet"] = self.b

    def smallblindbet(self, cash):
        self.b = int(input("Small blind bet: "))

        if cash*0.1 < self.b:
            print("Your small blind bet is too big for the players funds. It must be at most 10% of your funds")

            self.smallblindbet(cash)

        else:
            self.stats["Bet"] = self.b


if __name__ == "__main__":
    # Testing folding

    funds = 1000

    p1 = Player(funds, "1")

    p1.stats["Hand"] = ["as", "qh"]

    p1.fold()

    print(p1.stats)

    # Testing calling

    p2 = Player(funds, "2")

    p2.stats["Bet"] = 100

    p1.call(p2)

    print(p1.stats)

    # Testing Raising

    p1.pokerRaise(p2)

    print(p1.stats)

    # Testing betting

    p1.bet(10)

    print(p1.stats)
