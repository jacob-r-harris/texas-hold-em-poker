import random

import hierarchy

import json

import socket

import threading

from time import sleep

from deck import Deck

from player import Player

#  Networking Host and Port as well as a message log, client log and set disconnect message
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

    sb_bet = 10  # In-case there is an unforeseen error, smallblind bet is 10 by deafault

    while True:
        try:
            sb_bet = int(messages[-1]["msg"])

        except ValueError:
            network_send(smallblind.stats["ID"], "%Please enter an integer...\nSmall Blind Bet: ")  # Making sure its a valid response
            wait()

        break

    smallblind.smallblindbet(smallblind.stats["Cash"], sb_bet)  # Setting the small blinds bet in their stats

    bigblind.stats["Bet"] = smallblind.stats["Bet"] * 2  # Setting big blind's bet asw double the small blind

    bigblind.stats["Cash"] -= bigblind.stats["Bet"]

    network_send_multi((smallblind.stats["Name"], "put down a small blind bet of", str(smallblind.stats["Bet"]), "\n"
                       "This means the big blind bet is",
                        str(bigblind.stats["Bet"])),
                       playerlist[:])  # Sending message to all players

    plyr = playerlist[(playerlist.index(bigblind) + 1) % len(playerlist)]

    return plyr, bigblind.stats["Bet"]


def betting(player, playerlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    prevplayer = playerlist[(playerlist.index(player) - 1) % len(playerlist)]

    if len(playerlist) == 1:  # If there is one player left, they have won the game.
        winning_hand(playerlist, dealer, pot, Round, clientlist)

    if not player.stats["Hand"]:
        playerlist.remove(player)

        betting(nextplayer, playerlist)

    if player.stats["Cash"] == 0:
        network_send(player.stats["ID"], "You're all in")

        betting(nextplayer, playerlist)

    network_send(player.stats["ID"],
                 ("%" + player.stats["Name"] + ", your hand is", str(player.stats["Hand"]) + ", do you wish to:\n"
                                                                                             "(F)old\n"
                                                                                             "(C)all\n"
                                                                                             "(R)aise"))

    wait()

    i = messages[-1]["msg"]

    if i.lower().startswith("f"):
        player.fold()

        playerlist.remove(player)

        network_send(player.stats["ID"], "You have folded for this round")

        network_send_multi((player.stats["Name"] + "has folded"),  # All players other than the one in play
                           [prevplayer, nextplayer, playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])

    elif i.lower().startswith("c"):
        player.call(prevplayer)

        network_send(player.stats["ID"], ("Your bet is now", player.stats["Bet"]))

        network_send_multi((player.stats["Name"] + "has called"),  # All players other than the one in play
                           [prevplayer, nextplayer, playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])

    elif i.lower().startswith("r"):
        if player.stats["Cash"] < prevplayer.stats["Bet"]*2:
            network_send(player.stats["ID"], "You do not have enough funds to raise")

            betting(player, playerlist)

        while True:
            network_send(player.stats["ID"], "%Raise to:")

            wait()

            raiseTo = messages[-1]["msg"]

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
                           # All players other than the one in play
                           [prevplayer, nextplayer, playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])

    else:
        network_send(player.stats["ID"], '"' + messages[-1]["msg"] + '" is not a valid input')

        betting(player, playerlist)

    for p in playerlist:
        if playerlist[(playerlist.index(p) + 1) % len(playerlist)].stats["Bet"] != p.stats["Bet"]:
            betting(nextplayer, playerlist)


def flop(deck, dealer, plist):
    deck.deal([dealer], 5)

    network_send_multi("Here is the flop:\n"
                       "" + str(dealer.stats["Hand"][:3]), plist)


def post_flop_bets(player, minbet, playerlist):
    nextplayer = playerlist[(playerlist.index(player) + 1) % len(playerlist)]

    sleep(1)  # Added a sleep time to prevent code from trying to send multiple messages at once which breaks the client code

    network_send(player.stats["ID"], ("%" + player.stats["Name"] + ", your hand is", str(player.stats["Hand"]) +
                                      ", do you wish to:\n"
                                      "(C)heck\n"
                                      "(B)et"))

    wait()

    i = messages[-1]["msg"]

    if i.lower().startswith("b"):
        bet(player, minbet)

        network_send_multi((player.stats["Name"], "has bet", str(player.stats["Bet"])),
                           [playerlist[(playerlist.index(player) - 1) % len(playerlist)],
                            nextplayer,
                            playerlist[(playerlist.index(nextplayer) + 1) % len(playerlist)]])

        betting(nextplayer, playerlist)


def bet(player, minbet):
    b = minbet

    print(player)

    network_send(player.stats["ID"], "%Please enter your bet:")

    wait()

    try:
        b = int(messages[-1]["msg"])

    except ValueError:
        network_send(player.stats["ID"], "Please enter an integer")

        bet(player, minbet)

    if b < minbet:
        network_send(player.stats["ID"], ("Invalid amount\n"
                                          "Minimum bet is", str(minbet)))

        bet(player, minbet)

    else:
        player.stats["Bet"] = b


def winning_hand(playerlist, dealer, pot):
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
            winner = player

            score = player.stats["Score"]

        # If the scores are the same, it goes to a tie-breaker
        elif player.stats["Score"] == score:
            winner = hierarchy.tie_breaker([player, playerlist[playerlist.index(player) - 1]])

        if type(winner) is list:  # If there are multiple winners
            winners = ""

            for p in winner:
                winners = winners + p.stats["Name"]+", "

            network_send_multi(
                ("----------------------------------------------------------------------------\n"
                 "The winners are", winners,
                 "\n----------------------------------------------------------------------------\n"),
                playerlist)

            print(pot)

            winner[0].stats["Cash"] += round(pot / 2)
            winner[1].stats["Cash"] += round(pot / 2)

        else:  # If there is 1 winner
            network_send_multi(
                ("----------------------------------------------------------------------------\n"
                 "The winner is", winner.stats["Name"],
                 "\n----------------------------------------------------------------------------\n"),
                playerlist)

            print(pot)

            winner.stats["Cash"] += pot


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
                # do something if we have some data
                print(msg)

        conn.close()


def network_send(recipient, msg):
    sleep(0.1)

    out_msg = {"to": recipient, "msg": msg}
    j_msg = json.dumps(out_msg["msg"])
    print(out_msg)
    data = j_msg.encode()
    clients[out_msg["to"]].sendall(data)


def network_send_multi(msg, recipients):
    for p in recipients:
        network_send(p.stats["ID"], msg)


def wait():
    current_messages = messages[:]

    while True:
        if current_messages != messages:
            break

    return True


def main(Round, playerlist, dealer):
    #  Poker------------------------------------------------------------------------------------------------------------

    if Round == 1:
        funds = 1000

        playerlist, dealer = lobby(funds)

    clientlist = playerlist[:]

    for p in playerlist:
        network_send(p.stats["ID"], ("Your funds are:", str(p.stats["Cash"])))

    d = Deck()

    d.deal(playerlist, 2)

    pot = 0

    for p in playerlist:
        print(p.stats)

    firstplay, minbet, = opener(playerlist)

    betting(firstplay, playerlist)

    #for p in playerlist:
#
    #    p.stats["Bet"] = 0

    network_send_multi("Betting is now over, now we move onto the flop", playerlist)

    flop(d, dealer, playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    network_send_multi(("Here is the turn:\n" +
                        str(dealer.stats["Hand"][:4])), playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    network_send_multi(("Here is the river:\n" +
                        str(dealer.stats["Hand"][:5])), playerlist)

    for p in playerlist:
        post_flop_bets(p, minbet, playerlist)

    for p in playerlist:
        pot += p.stats["Bet"]

    winning_hand(playerlist, dealer, pot)

    Round += 1

    for p in playerlist:
        p.stats["Bet"] = 0

    main(Round, clientlist, dealer)


#  Networking-------------------------------------------------------------------------------------------------------

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()

        # This if statement ensure that the main game goes does not run for all 4 players
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
