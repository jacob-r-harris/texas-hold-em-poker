from player import Player


values = {"j":"11", "q":"12", "k":"13", "a":"14"}  # Setting the values for the letter cards


def temphand(players_hand, communitycards):  # Creates a list of both the community cards and the players cards
    temp = []

    for card in players_hand:
            temp.append(card)

    for card in communitycards:
            temp.append(card)

    return temp


def top_suit(temp_hand):  # Gets the most common suit in the temp_hand
    t = temp_hand[:]

    suitcount = {"clubs":0, "diamonds":0, "hearts":0, "spades":0}

    for c in t:
        if c[-1] == "c":
            suitcount["clubs"] += 1

        elif c[-1] == "d":
            suitcount["diamonds"] += 1

        elif c[-1] == "h":
            suitcount["hearts"] += 1

        elif c[-1] == "s":
            suitcount["spades"] += 1

    tops = ""

    count = 0

    for i in suitcount:
        if suitcount[i] > count:
            count = suitcount[i]

            tops = i

    return tops


def royal_flush(suit, temp_hand):  # Determines if the Player has a royal flush
    t = []

    rflush = ["10", "j", "q", "k", "a"]

    for c in temp_hand:  # How many cards are in the same suit and are a rflush value
        if c[-1] == suit[0] and c[:-1] in rflush:
            t.append(c)

    hand = t[:]

    if len(t) >= 5:
        return hand+["royalflush"]

    else:
        return False


def straight(temp_hand):  # Determines if the Player has a straight
    t = []

    thand = []

    strt = False

    for c in temp_hand:
        if c[:-1].isalpha():  # Renaming letter cards to their numerical value
            c = values[c[:-1]] + c[-1]

        if int(c[:-1]) not in t:
            t.append(int(c[:-1]))
            thand.append(c)

    t = sorted(t)  # sort the list

    for i in range(0, 3):  # Looping through the list starting at index 0 then 1 then 2
        x = t[i:i + 5]

        sorted_thand = sorted(thand)

        for c in range(0, len(sorted_thand)-1):
            if len(sorted_thand[c][:-1]) > 1:
                sorted_thand.append(sorted_thand[0])
                sorted_thand.pop(0)

        hand = sorted_thand[i:i + 5]  # turning the card into a face value hand

        true_straight = list(range(min(x), max(x)+1))  # Making a straight starting at the smallest value, ending at the largest

        if x == true_straight:  # if the list starting at the current point is the same as the straight
            strt = hand

    if strt:  # if there is a straight
        return strt+["straight"]


def flush(temp_hand, suit):  # Determines if the Player has a flush
    t = []
    try:
        for c in temp_hand:
            if c[-1] == suit[0]:
                t.append(c)

        if len(t) == 5:
            if straight(t):
                return t+["straightflush"]

            return t+["flush"]


    except IndexError:
        return None


def of_a_kind(temp_hand):  # Determines if the Player has a pair, 2pair, or 3/4 of a kind
    t = temp_hand[:]

    hand = []

    ranks = {}

    for c in t:
        if c[:-1] not in ranks:
            ranks[str(c[:-1])] = 1

        else:
            ranks[str(c[:-1])] += 1

    for c in ranks:
        if ranks[c] == 4:
            for cards in t:
                if c in cards:
                    hand.append(cards)

            hand += ["foak"]

        elif ranks[c] == 3:
            if 2 in ranks.values():
                for cards in t:
                    if c in cards:
                        hand.append(cards)

                hand += ["fullhouse"]

            for cards in t:
                if c in cards:
                    hand.append(cards)

            hand += ["toak"]

        elif ranks[c] == 2:
            for i in ranks:
                if ranks[i] == 2 and i != c:
                    for cards in t:
                        if c in cards or i in cards:
                            hand.append(cards)

                    hand += ["2pair"]

            for cards in t:
                if c in cards:
                    hand.append(cards)

            hand += ["pair"]

    formatted_hand = []

    sublist = []

    for ob in hand:
        sublist.append(ob)

        if len(ob) > 3:
            formatted_hand.append(sublist)

            sublist = []

    return formatted_hand


def check_hands(temp_hand, community_cards):  # Goes through to check what hands the player has
    natural_hands = []

    player_hand = []

    # First it will go through the community cards to see what hands occur naturally within them

    tops = top_suit(community_cards)

    if of_a_kind(community_cards):
        natural_hands += of_a_kind(community_cards)

    if straight(community_cards):
        natural_hands.append(straight(community_cards))

    if flush(community_cards, tops):
        natural_hands.append(flush(community_cards, tops))

    if royal_flush(tops, community_cards):
        natural_hands.append(flush(community_cards, tops))

    # Then it goes through the temp hand to see what hands occur in the community cards + the player's cards

    tops = top_suit(temp_hand)

    if of_a_kind(temp_hand):
        player_hand += of_a_kind(temp_hand)

    if straight(temp_hand) and player_hand:
        player_hand.append(straight(temp_hand))

    if flush(temp_hand, tops):
        player_hand.append(flush(temp_hand, tops))

    if royal_flush(tops, temp_hand):
        player_hand.append(royal_flush(tops, temp_hand))

    # If a hand occurs naturally in the community cards and the player has not contributed to those hands, it's removed

    for x in range(2):
        for i in player_hand:
            if i in natural_hands:
                player_hand.remove(i)

    # If the player now has no hands, it will go over to high card

    if len(player_hand) == 0:
        players_hand = []
        for card in temp_hand:
            if card not in community_cards:
                players_hand.append(card)

        for card in players_hand[:1]:
            if card[0].isalpha():
                card_value = values[card[0]] + card[1:]

                players_hand.append(card_value)

                players_hand.remove(card)

        player_hand = sorted(players_hand)[:-1]+["highcard"]

    return player_hand


def tie_breaker(list_of_tied_players):  # Tie breaker decides who wins by who has the highest value card
    highest = 0

    for player in list_of_tied_players:
        thand = player.stats["Hand"][:-1]

        for card in thand:  # Turning cards into their numerical value
            if card[0].isalpha():
                card_value = values[card[0]] + card[1:]

                thand[thand.index(card)] = card_value

                thand = sorted(thand)  # Sorting the cards

        high_card = thand[-1]

        high_card_value = int(high_card[:-1])  # Selects the highest value card

        if high_card_value > highest:
            highest = high_card_value

            winner = player

        elif high_card_value == highest:  # If multiple players have the same hand and high card, they are all winners
            if type(winner) is list:
                winner.append(player)

            else:
                winner = [winner, player]

    return winner


if __name__ == "__main__":
    # (["as", "ks", "qs", "10h", "4d"], [["js", "10s"]])

    #t = temphand(["ad", "10h"], ["js", "ks", "qs", "10s", "as"])

    #tops = top_suit(t)

    p1 = Player(1000, "1", "1")

    hands_dict = {"High": [["ac", "2d"], ["3c", "4h", "6h", "7c", "kc"]],      # High Card
                  "Pair": [["7d", "2d"], ["3c", "4h", "6h", "7c", "kc"]],      # Pair
                  "2pair": [["7d", "2d"], ["2c", "4h", "6h", "7c", "kc"]],     # 2 pair
                  "3oak": [["7d", "2d"], ["3c", "7h", "6h", "7c", "kc"]],      # 3 of a Kind
                  "Straight": [["3c", "2d"], ["3h", "4s", "5h", "6c", "kc"]],  # Straight
                  "Flush": [["3d", "2d"], ["3h", "4d", "5d", "9c", "kd"]],     # Flush
                  "FllHse": [["3c", "2d"], ["3d", "2c", "2h", "6c", "ks"]],    # Full House
                  "4oak": [["3c", "3d"], ["3h", "3s", "5h", "6c", "kc"]],      # 4 of a Kind
                  "StrtFlsh": [["3d", "2d"], ["3h", "4d", "5d", "9c", "6d"]],  # Straight Flush
                  "RylFlsh": [["ad", "kd"], ["3h", "qd", "jd", "6c", "10d"]]   # Royal Flush
                  }

    for x in hands_dict.values():
        p1.stats["Hand"] = x[0]

        community_cards = x[1]

        print(check_hands(temphand(p1.stats["Hand"], community_cards), community_cards))
