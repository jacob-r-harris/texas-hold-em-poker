import socket
import json
import random
import time
from outs_score import outs


HOST = "127.0.0.1"

PORT = 52002

name = random.choice(["Not A Robot", "Poker Face", "Royally Flushed", "0100000101001001", "Gonch"])

count = 0

funds = 0

community_cards = []

raiseTo = 0


def send(message):
    msg = {"name": name, "msg": message}

    json_msg = json.dumps(msg)

    s.sendall(str.encode(json_msg))


def wait():
    wait()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    if count == 0:
        msg = {"name": name, "msg": "%name%"}

        json_msg = json.dumps(msg)

        s.sendall(str.encode(json_msg))

        count += 1

    while True:
        data = s.recv(1024)

        print("message received")

        # out = json.loads(data.decode())

        # print(out["name"]+": "+out["msg"])

        try:
            server_message = json.loads(data.decode())

        except json.decoder.JSONDecodeError:
            print(data.decode())

        # This is to turn a list into a string that's printable
        if type(server_message) is list:
            temp = ""

            for i in server_message:
                temp = temp + " " + str(i)

            server_message = temp[1:]

        if server_message[0] == " " or server_message[0] == "%":  # Sometimes a message will be given a space at the beginning which affects the "%" marking
            server_message = server_message[1:]  # This removes the space or the "%"

            print(server_message)

            # The AI makes choices based on the message it has received

        if server_message[:15] == "Your funds are:":  # Reading how much money it has
            funds = int(server_message[16:])

        elif server_message == "Small Blind Bet: ":  # Checking if it's the small blind

            time.sleep(random.randint(3, 5))  # wait a random amount of time to seem more human

            pcnt = random.randint(1, 10)  # random percentage of funds to seem more human

            out = round((pcnt / 100) * funds)  # how much money it replies with

            print(out)

            send(str(out))

        elif server_message[:len(name)] == name:  # Seeing if it is being addressed
            if server_message[len(name):len(name)+14] == ", your hand is":  # Checking if it needs to make a move
                cards = False

                my_cards = ""

                for char in server_message:
                    if cards:
                        my_cards += char

                    if char == "[":
                        cards = True

                    elif char == "]":
                        cards = False

                my_cards = (my_cards[:-1].replace("'", "")).split(', ')  # Formatting cards from server message

                print(my_cards)

                my_outs = outs(my_cards, community_cards)

                print(my_outs)

                odds_to_play = random.randint(0, 10)

                if odds_to_play <= my_outs:  # If the odds to play are less than the outs it calls
                    send("c")

                else:
                    bluff_chance = 5

                    if random.randint(0, 10) > bluff_chance:  # Don't Bluff
                        if "(C)heck" in server_message:
                            send("c")

                        else:
                            send("f")

                    else:  # Do Bluff
                        if random.randint(0, 10) > bluff_chance:  # Deciding whether or not it should raise
                            if "(B)et" in server_message:
                                send("b")

                            else:
                                send("r")

                        else:
                            send("c")

        elif server_message[:62] == "You need to raise to at least double the previous players bet ":  # Gaining the previous players bet
            raiseTo = round(int(server_message[63:-1]) * 2)

            send(str(raiseTo))

        elif server_message[:9] == "Raise to:":  # Sending an impossible raise so that the server will say the previous players bet
            send(str(raiseTo))

        elif server_message[:] == "Please enter your bet:":
            hand_strength = outs(my_cards, community_cards)  # Deciding how good its hand is

            rand_num = random.randint(0, hand_strength)  # Choosing a random percentage up until the strength of its hand

            bet = round((rand_num / 10) * funds)  # That percentage of its funds will be its bet

            send(str(bet))

        elif server_message[:12] == "Here is the ":  # Recognising the community cards
            community_cards = server_message.split('[', len(server_message))[1][:-1]  # Extracting just the com cards

            community_cards = (community_cards.replace("'", "")).strip('][').split(', ')  # Formatting to a list

            print(community_cards)

        elif server_message[:15] == "You have folded":  # if its folded
            print("I have decided to fold")


