import random

import hierarchy

from deck import Deck

from player import Player

#  Networking Host and Port as well as a message log
HOST = "192.168.0.16"

PORT = 52002

messages = []


def lobby(funds):
    p1 = Player(funds, input("Name: "), 1)

    p2 = Player(funds, input("Name: "), 2)

    p3 = Player(funds, input("Name: "), 3)

    p4 = Player(funds, input("Name: "), 4)

    dealer = Player(0, "dler", 0)

    plist = [p1, p2, p3, p4]

    return plist, dealer


def opener(playerlist, funds):
    pseudo_dealer = random.choice(playerlist)

    smallblind = playerlist[(playerlist.index(pseudo_dealer) + 1) % len(playerlist)]

    bigblind = playerlist[(playerlist.index(pseudo_dealer) + 2) % len(playerlist)]

    print(smallblind.stats["Name"], "is the small blind\n"
                                    "And", bigblind.stats["Name"], "is the big blind")

    smallblind.stats["SB"] = True

    smallblind.smallblindbet(funds, int(input(smallblind.stats["Name"]+"'s Small blind bet:")))

    bigblind.stats["Bet"] = smallblind.stats["Bet"] * 2

    print(smallblind.stats["Name"], "put down a small blind bet of", str(smallblind.stats["Bet"]), "\n"
                                    "This means the big blind bet is",
          str(bigblind.stats["Bet"]))

    plyr = playerlist[(playerlist.index(bigblind) + 1) % len(playerlist)]

    return plyr, bigblind.stats["Bet"]


def betting(player, playerlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    prevplayer = playerlist[(playerlist.index(player) - 1) % len(playerlist)]

    if not player.stats["Hand"]:
        playerlist.remove(player)

        betting(nextplayer, playerlist)

    print(player.stats["Name"] + ", your hand is", str(player.stats["Hand"]) + ", do you wish to:\n"
                                                                               "(F)old\n"
                                                                               "(C)all\n"
                                                                               "(R)aise")

    i = input(">")

    if i.lower().startswith("f"):
        player.fold()

        playerlist.remove(player)

        print("You have folded for this round")

    elif i.lower().startswith("c"):
        player.call(prevplayer)

        print("Your bet is now", player.stats["Bet"])

    elif i.lower().startswith("r"):
        player.pokerRaise(prevplayer)

        print("Your bet is now", player.stats["Bet"])

    else:
        player.fold()

        playerlist.remove(player)

        print("You have folded for this round")

    for p in playerlist:
        if playerlist[(playerlist.index(p) + 1) % len(playerlist)].stats["Bet"] != p.stats["Bet"]:
            betting(nextplayer, playerlist)


def flop(deck, dealer):
    deck.deal([dealer], 5)

    print("Here is the flop:\n"
          "" + str(dealer.stats["Hand"][:3]))


def post_flop_bets(player, minbet, playerlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    print(player.stats["Name"] + ", it is your turn\n"
                                 "Your cards are", str(player.stats["Hand"]) + ", do you:\n"
                                                                               "(C)heck\n"
                                                                               "(B)et")

    i = input(">")

    if i.lower().startswith("b"):
        player.bet(minbet)

        betting(nextplayer, playerlist)


def winning_hand(playerlist, dealer):
    # Defining the community cards, which I've stored in the dealers hand
    community_cards = dealer.stats["Hand"]

    # Giving point values to each different hand
    rankings = {"royalflush": 10, "straightflush": 9, "foak": 8, "fullhouse": 7, "flush": 6, "straight": 5, "toak": 4,
                "2pair": 3, "pair": 2, "highcard": 1}

    # This determines all of the hands that a player has and subsequently set their score as the best hands score
    for player in playerlist:
        # Creating a temporary hand that consists of the community cards and the players hand
        player.stats["Hand"] = hierarchy.temphand(player.stats["Hand"], community_cards)

        # Seeing What hands the player has
        hands = hierarchy.check_hands(player.stats["Hand"], community_cards)

        score = 0

        # Determining the players best hand
        for h in hands:
            if score < rankings[h[-1]]:
                score = rankings[h[-1]]

                player.stats["Hand"] = h

        # Setting their score as the score of their best hand
        player.stats["Score"] = score

    score = 0

    winner = ""

    # Choosing the winner based on the highest score
    for player in playerlist:
        if player.stats["Score"] > score:
            winner = player.stats["Name"]

            score = player.stats["Score"]

        # If the scores are the same, it goes to a tie-breaker
        elif player.stats["Score"] == score:
            winner = hierarchy.tie_breaker([player, playerlist[playerlist.index(player) - 1]])

    print("----------------------------------------------------------------------------\n"
          "The winner is", winner,
          "\n----------------------------------------------------------------------------\n")


def main():
    #  Networking-------------------------------------------------------------------------------------------------------

    #  Poker------------------------------------------------------------------------------------------------------------

    funds = 1000

    playerlist, dealer = lobby(funds)

    d = Deck()

    d.deal(playerlist, 2)

    pot = 0

    for p in playerlist:
        print(p.stats)

    firstplay, minbet = opener(playerlist, funds)

    betting(firstplay, playerlist)

    for p in playerlist:
        p.stats["Cash"] -= p.stats["Bet"]

        pot += p.stats["Bet"]

        p.stats["Bet"] = 0

    print("Betting is now over, now we move onto the flop\n"
          "Our current pot is", str(pot))

    flop(d, dealer)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    print("Here is the turn:\n" +
          str(dealer.stats["Hand"][:4]))

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    print("Here is the river:\n" +
          str(dealer.stats["Hand"][:5]))

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    winning_hand(playerlist, dealer)


main()

# Iron out bugs (lots of ctrl+shift+f10):
# Small blind bet cant not be a number

# line 131, in winning_hand
#     if score < rankings[h[-1]]:
# TypeError: 'NoneType' object is not subscriptable
