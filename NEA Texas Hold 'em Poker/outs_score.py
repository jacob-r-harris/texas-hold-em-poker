import random

import hierarchy


def outs(players_cards, com_cards):  # This calculates the amount of cards left in the deck that could make a hand and ranks them
    known_cards = players_cards + com_cards

    potential_hands = ["royal flush", "straight flush", "foak", "full house", "flush", "straight", "toak", "2pair",
                       "pair", "high card"]

    card_values = {"j": "11", "q": "12", "k": "13", "a": "14"}

    remove_list = []

    # Checking if any kind of flush is possible ----------------------------------------------------------------------------

    other_known_cards = known_cards[:]

    count = 1

    most_likely_flush = 0

    for card in known_cards:
        other_known_cards.remove(card)

        for other_card in other_known_cards:
            if other_card[-1] == card[-1]:  # If the suit is the same: +1 to count
                count += 1

        if count > most_likely_flush:  # To see if this next potential flush is longer than the previous longest
            most_likely_flush = count

        count = 1

    cards_needed = 5 - most_likely_flush

    unseen_cards = 7 - len(known_cards)

    tops = hierarchy.top_suit(known_cards)[0]

    royal_flush = ["a" + tops, "k" + tops, "q" + tops, "j" + tops, "10" + tops]

    count = 0

    for card in royal_flush:  # seeing if there is a royal flush
        if card in known_cards:
            count += 1

    if 5 - count > unseen_cards:
        remove_list.append("royal flush")

    if cards_needed > unseen_cards:  # If the amount of cards needed exceeds the poential cards to come, the hand is not possible
        for hand in potential_hands:
            if "flush" in hand and hand != "royal flush":
                remove_list.append(hand)

    # Checking if any kind of straight is possible -------------------------------------------------------------------------

    known_cards_num = []

    for card in known_cards:  # If card is picture card it will change it to its numerical value
        try:
            int(card[:-1])  # Tries to make it an int

            known_cards_num.append(int(card[:-1]))  # If it can its a number

        except ValueError:  # If it cant it must be a letter and thus changes the letter to the numerical value
            value_card = card_values[card[:-1]]

            known_cards_num.append(int(value_card))

        known_cards_num = sorted(known_cards_num)

    # Once we have the cards numerical values we can see how far away we are from a straight

    consec_num_list = []

    straight_hands = []

    longest = []

    list_mid_needed = 5

    list_ends_needed = 5

    straight_found = False

    for num in known_cards_num:
        if known_cards_num[(known_cards_num.index(num) + 1) % len(known_cards_num)] - num == 1:  # Next num - current num
            consec_num_list.append(num)

        else:
            consec_num_list.append(num)

            straight_hands.append(consec_num_list)

            consec_num_list = []

    for list in straight_hands:
        if len(list) >= len(longest):  # If the length of the list > length of the prev list
            longest = list

    if 5 - len(longest) <= 0:
        straight_found = True

    else:
        list_ends_needed = 5 - len(longest)

    for list in straight_hands:
        if list != longest:
            if longest[0] > list[-1] and len(longest) + len(list) >= 5 - unseen_cards:
                if list_mid_needed > longest[0] - list[-1]:
                    list_mid_needed = longest[0] - list[-1] - 1

            elif list[0] > longest[-1] and len(longest) + len(list) >= 5 - unseen_cards:
                if list_mid_needed > list[0] - longest[-1]:
                    list_mid_needed = list[0] - longest[-1] - 1

    if straight_found:
        cards_needed = 0

    elif list_ends_needed < list_mid_needed:
        cards_needed = list_ends_needed

    else:
        cards_needed = list_mid_needed


    if cards_needed > unseen_cards:
        for hand in potential_hands:
            if "straight" in hand:
                remove_list.append(hand)

    # Checking if there is any kind of pair/of a kind/full house -----------------------------------------------------------

    other_known_cards = known_cards[:]

    pairs_list = []

    hands_considered_pairs = ['foak', 'full house', 'toak', '2pair', 'pair']

    pair_dict = {}

    for card in known_cards:
        other_known_cards.remove(card)

        pair = [card]

        for other_card in other_known_cards:
            if other_card[:-1] == card[:-1]:  # If the values are the same: +1 to count
                pair.append(other_card)

        if len(pair) > 1:  # If it's a pair, add it to the pairs list
            pairs_list.append(pair)

    for pair in pairs_list: # Checking for ecisting pairs
        if len(pair) > 2:
            if len(pair) > 3:
                pair_dict["foak"] = pair
            else:
                pair_dict["toak"] = pair
        else:
            if "pair" in pair_dict:  # If there is already a pair that means there is a 2pair
                pair_dict["2pair"] = pair_dict["pair"] + pair

            else:
                pair_dict["pair"] = pair

    if unseen_cards > 2 or \
            unseen_cards > 1 and "pair" in pair_dict.keys():
        pair_dict["foak"] = "possible"
        pair_dict["toak"] = "possible"
        pair_dict["2pair"] = "possible"
        pair_dict["pair"] = "possible"

    elif unseen_cards > 1 or unseen_cards > 0 and "pair" in pair_dict.keys():
        pair_dict["toak"] = "possible"
        pair_dict["2pair"] = "possible"
        pair_dict["pair"] = "possible"

    elif unseen_cards > 0 and "toak" in pair_dict.keys():
        pair_dict["foak"] = "possible"

    elif unseen_cards > 0:
        pair_dict["pair"] = "possible"

    if "pair" in pair_dict and "toak" in pair_dict:  # Checking if there is a full house
        if pair_dict["pair"][1][-1] != pair_dict["toak"][1][-1]:  # If the suits are different there is a full house
            pair_dict["full house"] = pair_dict["pair"] + pair_dict["toak"]

    for hand in hands_considered_pairs:
        if hand not in pair_dict.keys():
            remove_list.append(hand)



    for hand in remove_list:
        if hand in potential_hands:
            potential_hands.remove(hand)

    # Calculating the probability of this hand winning ---------------------------------------------------------------------

    hand_scores = {"royal flush": 10, "straight flush": 9, "foak": 8, "full house": 7, "flush": 6, "straight": 5,
                   "toak": 4, "2pair": 3, "pair": 2, "high card": 1}

    out_score = 1

    for hand in potential_hands:
        if hand in hand_scores.keys():
            out_score = hand_scores[hand]

            break  # Because the potential_hands list is in order of score, the first one in the list will be the highest scoring hand

    print(potential_hands)

    if type(out_score) is not int:
        out_score = hand_scores[out_score[1]]

    return out_score


if __name__ == "__main__":
    deck = ['as', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', '10s', 'js', 'qs', 'ks', 'ac', '2c', '3c', '4c', '5c',
            '6c', '7c', '8c', '9c', '10c', 'jc', 'qc', 'kc', 'ah', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h',
            'jh', 'qh', 'kh', 'ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', '10d', 'jd', 'qd', 'kd']

    x = []

    y = []

    for i in range(2):
        x.append(deck.pop(random.choice(range(len(deck)))))

    for i in range(random.choice(range(5))):
        y.append(deck.pop(random.choice(range(len(deck)))))

    print(x, "\n", y)

    print(outs(x, y))
