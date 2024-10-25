class Player:

    def __init__(self, funds, name, ID):
        self.name = name

        self.money = funds

        self.stats = {"ID": ID, "Name": self.name, "Cash": self.money, "Hand": [], "Bet": 0, "SB": ""}

        self.b = 0

        self.r = 0

    def fold(self):
        self.stats["Hand"] = []

    def call(self, prev_player):
        self.stats["Bet"] += prev_player.stats["Bet"] - self.stats["Bet"]

        self.stats["Cash"] -= self.stats["Bet"]

    def pokerRaise(self, prev_player, amount):
        self.r = int(amount)

        if self.r < prev_player.stats["Bet"] * 2:
            return "<"

        elif self.r > int(self.stats["Cash"]):
            return ">"

        else:
            self.stats["Bet"] = self.r

            self.stats["Cash"] -= self.stats["Bet"]

            return "="

    def smallblindbet(self, cash, bet):
        self.b = bet

        if cash*0.1 < self.b:
            print("Your small blind bet is too big for the players funds. It must be at most 10% of your funds")

            self.smallblindbet(cash, bet)

        else:
            self.stats["Bet"] = self.b

            #self.stats["Cash"] -= self.stats["Bet"]


if __name__ == "__main__":
    # Testing folding

    funds = 1000

    p1 = Player(funds, "1", "1")

    p1.stats["Hand"] = ["as", "qh"]

    p1.fold()

    print(p1.stats)

    # Testing calling

    p2 = Player(funds, "2", "2")

    p2.stats["Bet"] = 100

    p1.call(p2)

    print(p1.stats)

    # Testing Raising

    p1.pokerRaise(p2, "900")

    print(p1.stats)

    # Testing betting

    #p1.bet(10)

    print(p1.stats)
