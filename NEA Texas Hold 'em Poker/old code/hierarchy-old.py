values = {"j":"11", "q":"12", "k":"13", "a":"14"}

from player import Player

def temphand(players_hand, communitycards):
    temp = []

    for card in players_hand:
            temp.append(card)

    for card in communitycards:
            temp.append(card)

    return temp


def top_suit(temp_hand):
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


def royal_flush(suit, temp_hand):
    t = []

    rflush = ["10", "j", "q", "k", "a"]

    for c in temp_hand:
        if c[-1] == suit[0]:
            t.append(c)

    hand = t[:]

    for v in rflush:
        if v + suit[0] in t:
            t.remove(v + suit[0])

    if not t:
        return hand+["royalflush"]

    else:
        return False


def straight(temp_hand):
    t = []

    thand = []

    strt = False

    for c in temp_hand:
        if c[:-1].isalpha():
            c = values[c[:-1]] + c[-1]

        t.append(int(c[:-1]))
        thand.append(c)

    t = sorted(t)

    for i in range(0, 3):
        x = t[i:i + 5]

        hand = sorted(thand)[i:i + 5]

        true_straight = list(range(min(x), max(x)+1))

        if x == true_straight:
            strt = hand

    if strt:
        return strt+["straight"]


def flush(temp_hand, suit):
    t = []
    try:
        for c in temp_hand:
            if c[-1] == suit[0]:
                t.append(c)

        if len(t) == 5:
            return t+["flush"]

    except IndexError:
        return None


def of_a_kind(temp_hand):
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

            return hand+["foak"]

        elif ranks[c] == 3:
            if 2 in ranks.values():
                for cards in t:
                    if c in cards:
                        hand.append(cards)

                return hand+["fullhouse"]

            for cards in t:
                if c in cards:
                    hand.append(cards)

            return hand+["toak"]

        elif ranks[c] == 2:
            for i in ranks:
                if ranks[i] == 2 and i != c:
                    for cards in t:
                        if c in cards or i in cards:
                            hand.append(cards)

                    return hand+["2pair"]

            for cards in t:
                if c in cards:
                    hand.append(cards)

            return hand+["pair"]


def check_hands(temp_hand, community_cards):
    natural_hands = []

    player_hand = []

    tops = top_suit(community_cards)

    if of_a_kind(community_cards):
        natural_hands.append(of_a_kind(community_cards))

    if straight(community_cards):
        natural_hands.append(straight(community_cards))

    if flush(community_cards, tops):
        natural_hands.append(flush(community_cards, tops))

    if royal_flush(tops, community_cards):
        natural_hands.append(flush(community_cards, tops))

    tops = top_suit(temp_hand)

    if of_a_kind(temp_hand):
        player_hand.append(of_a_kind(temp_hand))

    if straight(temp_hand) and player_hand:
        player_hand.append(straight(temp_hand))

    if flush(temp_hand, tops):
        player_hand.append(flush(temp_hand, tops))

    if royal_flush(tops, temp_hand):
        player_hand.append(royal_flush(temp_hand, tops))

    for x in range(2):
        for i in player_hand:
            if i in natural_hands:
                player_hand.remove(i)

    if player_hand is None:
        for card in temp_hand[:1]:
            if card[0].isalpha():
                card_value = values[card[0]] + card[1:]

                temp_hand.append(card_value)

                temp_hand.remove(card)

        player_hand = sorted(temp_hand)[-1]+["highcard"]

    return player_hand


def tie_breaker(list_of_tied_players):
    highest = 0

    for player in list_of_tied_players:
        thand = player.stats["Hand"][:-1]

        for card in thand:
            if card[0].isalpha():
                card_value = values[card[0]] + card[1:]

                thand[thand.index(card)] = card_value

                thand = sorted(thand)

        high_card = thand[-1]

        high_card_value = int(high_card[:-1])

        if high_card_value > highest:
            highest = high_card_value

            winner = player

    return winner


if __name__ == "__main__":
    # (["as", "ks", "qs", "10h", "4d"], [["js", "10s"]])

    #t = temphand(["ad", "10h"], ["js", "ks", "qs", "10s", "as"])

    #tops = top_suit(t)

    p1 = Player(1000, "1", "1")

    p2 = Player(1000, "2", "2")

    p1.stats["Hand"] = ["ac", "kc", "qc", "jc", "10c"]

    p2.stats["Hand"] = ["ac", "ah", "ad", "as"]

    playerlist = [p1, p2]

    community_cards = ["5d", "4s", "3h"]

    rankings = {"royalflush": 10, "straightflush": 9, "foak": 8, "fullhouse": 7, "flush": 6, "straight": 5, "toak": 4,
                "2pair": 3, "pair": 2, "highcard": 1}

    for player in playerlist:
        player.stats["Hand"] = temphand(player.stats["Hand"], community_cards)

        hands = check_hands(player.stats["Hand"], community_cards)

        print(hands)

        score = 0

        for h in hands:
            if score < rankings[h[-1]]:
                score = rankings[h[-1]]

                player.stats["Hand"] = h

        player.stats["Score"] = score

    score = 0

    winner = ""

    for player in playerlist:
        if player.stats["Score"] > score:
            winner = player.stats["Name"]

            score = player.stats["Score"]

        elif player.stats["Score"] == score:
            winner = tie_breaker([player, playerlist[playerlist.index(player) - 1]])

    print("----------------------------------------------------------------------------\n"
          "The winner is", winner,
          "\n----------------------------------------------------------------------------\n")

    #print(tie_breaker([p1, p2]))

   #print(tops)

   #r = royal_flush(tops, t)

   #print(t)

   #print(r)

   #print(straight(t))

   #print(flush(t, tops))

   #print(of_a_kind(t))

   #print("\n-------------------------------------------------------------------------------------------------------\n")

   #print(check_hands(t, ["js", "ks", "qs", "10s", "as"]))
