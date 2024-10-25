import random

import hierarchy

import json

import socket

import threading

from time import sleep

from deck import Deck

from player import Player

#  Networking Host and Port as well as a message log, client log and set disconnect message and other required variables
HOST = "127.0.0.1"

PORT = 52002

messages = []

clients = {}

disconnect_msg = "/disconnect"

userNo = 1

Round = 1

playerlist = []

dealer = ""


def lobby(funds):
    # Sending out requests for each of the players names

    while True:
        if "4" in clients:  # Allow a maximum of 4 players
            break

    p1 = Player(funds, messages[0]["name"], "1")

    p2 = Player(funds, messages[1]["name"], "2")

    p3 = Player(funds, messages[2]["name"], "3")

    p4 = Player(funds, messages[3]["name"], "4")

    dealer = Player(0, "dler", "0")

    plist = [p1, p2, p3, p4]  # List of all the active players

    return plist, dealer


def opener(playerlist):
    pseudo_dealer = random.choice(playerlist)  # Choosing a random player that will decide who is the big blind and small blind

    smallblind = playerlist[(playerlist.index(pseudo_dealer) + 1) % len(playerlist)]

    bigblind = playerlist[(playerlist.index(pseudo_dealer) + 2) % len(playerlist)]

    network_send_multi((smallblind.stats["Name"], "is the small blind\n"  # Telling all players who is the big blind and small blind
                                                  "And", bigblind.stats["Name"], "is the big blind"),
                       [bigblind,
                        playerlist[(playerlist.index(bigblind) + 1) % len(playerlist)],  # big blind + 1
                        playerlist[(playerlist.index(bigblind) + 2) % len(playerlist)]])  # big blind + 2

    smallblind.stats["SB"] = True

    network_send(smallblind.stats["ID"], "%Small Blind Bet: ")  # Asking the smallblind to make a bet

    wait()

    sb_bet = 10  # In-case there is an unforeseen error, smallblind bet is 10

    while True:
        try:
            sb_bet = int(messages[-1]["msg"])

        except ValueError:
            network_send(smallblind.stats["ID"], "%Please enter an integer...\nSmall Blind Bet: ")  # Making sure its a valid response
            wait()

        if smallblind.stats["Cash"] * 0.1 < sb_bet:
            network_send(smallblind.stats["ID"],
                         ("%Your small blind bet is too big for the players funds. It must be at most 10% of your funds"
                         "(which is", str(int(smallblind.stats["Cash"]*0.1))+")"))
            wait()

        else:
            break

    smallblind.smallblindbet(sb_bet)  # Setting the small blinds bet in their stats

    bigblind.stats["Bet"] = smallblind.stats["Bet"] * 2  # Setting big blind's bet asw double the small blind

    bigblind.stats["Cash"] -= bigblind.stats["Bet"]

    network_send_multi((smallblind.stats["Name"], "put down a small blind bet of", str(smallblind.stats["Bet"]), "\n"
                       "This means the big blind bet is",
                        str(bigblind.stats["Bet"])),
                       playerlist[:])  # Sending a message to all players

    plyr = playerlist[(playerlist.index(bigblind) + 1) % len(playerlist)]

    print(smallblind.stats)
    print(bigblind.stats)

    return plyr, bigblind.stats["Bet"]


def betting(player, playerlist, pot, dealer, clientlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    prevplayer = playerlist[(playerlist.index(player) - 1) % len(playerlist)]

    if len(playerlist) == 1:  # If there is one player left, they have won the game.
        winning_hand(playerlist, dealer, pot, Round, clientlist)

    if not player.stats["Hand"]:
        playerlist.remove(player)

        betting(nextplayer, playerlist, pot, dealer, clientlist)

    if player.stats["Cash"] == 0:  # If a player has no money and is still in the game, this must mean they're all in
        network_send(player.stats["ID"], "You're all in")

        betting(nextplayer, playerlist, pot, dealer, clientlist)

    network_send(player.stats["ID"],
                 ("%" + player.stats["Name"] + ", your hand is", str(player.stats["Hand"]) + ", do you wish to:\n"
                                                                                             "(F)old\n"
                                                                                             "(C)all\n"
                                                                                             "(R)aise"))

    wait()

    i = messages[-1]["msg"]

    if i.lower().startswith("f"):  # Folding
        player.fold()

        playerlist.remove(player)

        network_send(player.stats["ID"], "You have folded for this round")

        network_send_multi((player.stats["Name"] + "has folded"),
                           playerlist)  # All players

    elif i.lower().startswith("c"):  # Calling
        player.call(prevplayer)

        network_send(player.stats["ID"], ("Your bet is now", player.stats["Bet"]))

        network_send_multi((player.stats["Name"] + "has called"),  # All players other than the one in play
                           [prevplayer, nextplayer, playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])

    elif i.lower().startswith("r"):  # Raising
        if player.stats["Cash"] < prevplayer.stats["Bet"]*2:  # If they don't have enough money to raise
            network_send(player.stats["ID"], "You do not have enough funds to raise")

            betting(player, playerlist, pot, dealer, clientlist)

        while True:  # While loop to prevent the user going through the betting stage if they input something invalid
            network_send(player.stats["ID"], "%Raise to:")

            wait()

            raiseTo = messages[-1]["msg"]

            print(raiseTo)

            raiseReturn = player.pokerRaise(prevplayer, raiseTo)

            if raiseReturn == "<":
                network_send(player.stats["ID"], ("You need to raise to at least double the previous players bet "
                                                  + "(" + str(prevplayer.stats["Bet"]) + ")"))

            elif raiseReturn == ">":
                network_send(player.stats["ID"], ("You can't bet more money than you have "
                             + "(" + str(player.stats["Cash"]) + ")"))

            else:
                break

        network_send(player.stats["ID"], ("Your bet is now", str(player.stats["Bet"])))

        network_send_multi((player.stats["Name"] + "has raised to" + str(player.stats["Bet"])),
                           [prevplayer, nextplayer, playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])
        # All players other than the one in play

    else:
        network_send(player.stats["ID"], ("'"+i+"'", "is not a valid input"))
        betting(player, playerlist, pot, dealer, clientlist)

    for p in playerlist:
        if playerlist[(playerlist.index(p) + 1) % len(playerlist)].stats["Bet"] != p.stats["Bet"]:
            #  If all players bets are not the same, continue betting
            betting(nextplayer, playerlist, pot, dealer, clientlist)


def flop(deck, dealer, plist):
    deck.deal([dealer], 5)  # Give the dealer five cards

    network_send_multi("Here is the flop:\n"
                       "" + str(dealer.stats["Hand"][:3]), plist)  # Show the first 3 community cards


def post_flop_bets(player, minbet, playerlist, pot, dealer, clientlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    if len(playerlist) == 1:
        winning_hand(playerlist, dealer, pot, Round, clientlist)

    sleep(1)  # Added a sleep time to prevent code from trying to send multiple messages at once which breaks the client code

    network_send(player.stats["ID"], ("%" + player.stats["Name"] + ", your hand is", str(player.stats["Hand"]) +
                                      ", do you wish to:\n"
                                      "(C)heck\n"
                                      "(B)et"))

    wait()

    i = messages[-1]["msg"]

    if i.lower().startswith("b"):  # If they decide to bet
        bet(player, minbet)

        # Sending how much they bet to the rest of the players

        network_send_multi((player.stats["Name"], "has bet", str(player.stats["Bet"])),
                           [playerlist[(playerlist.index(player) - 1) % len(playerlist)],
                            nextplayer,
                            playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])


        betting(nextplayer, playerlist, pot, dealer, clientlist)

    elif not i.lower().startswith("b") and not i.lower().startswith("c"):
        network_send(player, "Invalid input")

    #  If a player checks the code will just continue to run


def bet(player, minbet):
    b = minbet

    print(player)

    network_send(player.stats["ID"], "%Please enter your bet:")

    wait()

    try:
        b = float(messages[-1]["msg"])

        print(b)

        b = int(b)

    except ValueError:
        network_send(player.stats["ID"], "Please enter an integer")

        bet(player, minbet)

    if b < minbet:
        network_send(player.stats["ID"], ("Invalid amount\n"
                                          "Minimum bet is", str(minbet)))

        bet(player, minbet)

    else:
        player.stats["Bet"] = b


def winning_hand(playerlist, dealer, pot, Round, clientlist):
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
            print(hands)

            try:
                if score < rankings[h[-1]]:
                    score = rankings[h[-1]]

                    player.stats["Hand"] = h

            except KeyError:
                if score < rankings[hands[-1]]:
                    score = rankings[hands[-1]]

                    player.stats["Hand"] = hands

        # Setting their score as the score of their best hand
        player.stats["Score"] = score

    score = 0

    winner = ""

    tied = []

    # Choosing the winner based on the highest score
    for player in playerlist:
        if player.stats["Score"] > score:
            winner = player

            score = player.stats["Score"]

            tied = [player]

        # If the scores are the same, it goes to a tie-breaker
        elif player.stats["Score"] == score:
            tied.append(player)

    if len(tied) > 1:
        winner = hierarchy.tie_breaker(tied)

    if type(winner) is list:  # If there are multiple winners
        winners = ""

        for p in winner:
            winners = winners + p.stats["Name"]+", "

        network_send_multi(
            ("----------------------------------------------------------------------------\n"
             "The winners are", str(winners),
             "\n----------------------------------------------------------------------------\n"),
            clientlist)

        print(pot)

        for p in winner:
            p.stats["Cash"] += int(round(pot/len(winner)))

    else:  # If there is 1 winner
        network_send_multi(
            ("----------------------------------------------------------------------------\n"
             "The winner is", winner.stats["Name"],
             "\n----------------------------------------------------------------------------\n"),
            clientlist)

        print(pot)

        winner.stats["Cash"] += pot

    for p in playerlist:
        if p.stats["SB"]:
            p.stats["SB"] = ""

    main(Round+1, clientlist, dealer)  # Moves onto the next round


def network_receive(conn, userNo):
    with conn:
        print("Connected by", addr)

        while True:

            try:
                json_msg = conn.recv(1024)

            # Displays a message if a player has closed their window
            except ConnectionResetError:
                print("A player has closed their game window")
                break

            msg = {"msg": ""}

            if json_msg:
                msg = json.loads(json_msg)

                clients[str(userNo)] = conn

            if msg["msg"] == disconnect_msg:
                print(msg["name"], "has disconnected")
                break

            elif msg["msg"]:
                messages.append(msg)

            elif msg:
                # If the message does not have any message data, ask for a valid input
                network_send(str(userNo), "%Please enter a valid input")
                print(msg)
                network_receive(conn, userNo)

        conn.close()


def network_send(recipient, msg):
    sleep(0.1)  # To prevent multiple messages being sent at once

    out_msg = {"to": recipient, "msg": msg}
    j_msg = json.dumps(out_msg["msg"])
    print(out_msg)
    data = j_msg.encode()
    try:
        if out_msg["to"] and out_msg["msg"]:
            clients[out_msg["to"]].sendall(data)

    except:
        print("Error sending message")


def network_send_multi(msg, recipients):
    for p in recipients:  # To make it easier to send to multiple clients
        network_send(p.stats["ID"], msg)


def wait():  # This is to ensure the game does not continue until the server has gained a response
    current_messages = messages[:]

    while True:
        if current_messages != messages:
            break

    return True


def main(Round, playerlist, dealer):
    #  Poker------------------------------------------------------------------------------------------------------------

    if Round == 1:
        funds = 100  # Sets the starting amount of money

        playerlist, dealer = lobby(funds)

    clientlist = playerlist[:]  # A list of all players, including ones out of the game

    initfund = {}

    for p in playerlist:
        if p.stats["Cash"] <= 0:
            network_send(p.stats["ID"], "You're out of the game")

            playerlist.remove(p)

        else:
            network_send(p.stats["ID"], ("Your funds are:", str(p.stats["Cash"])))

        initfund[p.stats["ID"]] = p.stats["Cash"]

    if len(playerlist) == 1:
        network_send_multi((playerlist[1].stats["Name"], "has won this game of poker, congratz!"), clientlist)

        network_send_multi("Type /disconnect to leave the game", clientlist)

        wait()

    d = Deck()

    d.deal(playerlist, 2)  # Deal 2 cards to each player

    pot = 0

    for p in playerlist:
        print(p.stats)

    firstplay, minbet, = opener(playerlist)

    betting(firstplay, playerlist, pot, dealer, clientlist)

    network_send_multi("Betting is now over, now we move onto the flop", playerlist)

    flop(d, dealer, playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist, pot, dealer, clientlist)

        print(p.stats)

    network_send_multi(("Here is the turn:\n" +
                        str(dealer.stats["Hand"][:4])), playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist, pot, dealer, clientlist)

        print(p.stats)

    network_send_multi(("Here is the river:\n" +
                        str(dealer.stats["Hand"][:5])), playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist, pot, dealer, clientlist)

        print(p.stats)

    for p in playerlist:
        pot += p.stats["Bet"]

        if initfund[p.stats["ID"]] == p.stats["Cash"]:
            p.stats["Cash"] -= p.stats["Bet"]

    winning_hand(playerlist, dealer, pot, Round, clientlist)


#  Networking-------------------------------------------------------------------------------------------------------

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()

        # This if statement ensure that the main game code does not run for all 4 players
        if userNo > 1:
            threading.Thread(target=network_receive, args=(conn, userNo)).start()
            userNo += 1

        else:
            send_thread = threading.Thread(target=main, args=(Round, playerlist, dealer,))
            send_thread.start()
            threading.Thread(target=network_receive, args=(conn, userNo)).start()
            userNo += 1

# Iron out bugs (lots of ctrl+shift+f10):
# Small blind bet cant not be a number

# line 131, in winning_hand
#     if score < rankings[h[-1]]:
# TypeError: 'NoneType' object is not subscriptable

#  line 213, in network_receive
#     with conn:
# AttributeError: __enter__

# message to all doesnt work
# Figure out to send a message with small blind notif
