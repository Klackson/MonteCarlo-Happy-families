import numpy as np
import game

params = {"selection_method" : "greedy"}

def assume_game_state(player_number, hands, families_scored):
    deck = build_remaining_deck(hands, families_scored, player_number)

    hands, pile = deal_other_hands(player_number, deck, hands)

    return hands, pile

def build_remaining_deck(hands, families_scored, player_number, verbose = game.VERBOSE):
    deck = []

    for family in range(game.params["nb_families"]):
        if families_scored[family,0] != -1: continue # Family already scored
        for person in range(game.params["nb_people_per_family"]):
            card = [family, person]
            if card in hands[player_number]: continue # Card already in hand
            deck.append(card)

    np.random.shuffle(deck)
    if verbose : print("Deck size :", len(deck))
    return deck

def deal_other_hands(player_number, deck, hands):
    newhands = hands.copy()

    for i in range(len(hands)):
        if i == player_number: continue
        hand = hands[i]
        
        for j in range(len(hand)):
            card = deck.pop()
            newhands[i][j] = card
    
    return newhands, deck # Deck is the pile since dealt cards have been popped from it


def choose_random(hands, player_number):
    other_players = [i for i in range(len(hands)) if i != player_number]
    asked_player = np.random.choice(other_players)

    families_in_hand = [card[0] for card in hands[player_number]]
    if params["selection_method"]=="weighted": asked_family = np.random.choice(families_in_hand)
    elif params["selection_method"]=="uniform": asked_family = np.random.choice(np.unique(families_in_hand))
    elif params["selection_method"]=="greedy": 
        unique, counts = np.unique(families_in_hand, return_counts=True)
        index = np.argmax(counts)
        asked_family = unique[index]
    
    unowned_family_cards = [i for i in range(len(game.params["nb_people_per_family"])) if [asked_family, i] not in hands[player_number]] # can be made faster
    asked_card = np.random.choice(unowned_family_cards)

    return asked_player, asked_family, asked_card


def ask_random(hands, pile, player_number):
    asked_player, asked_family, asked_card = choose_random(hands, player_number)

    if game.VERBOSE : print("Player", player_number, "asks player", asked_player, "for family", asked_family, "and card", asked_card)

    asked_hand = hands[asked_player]
    if [asked_family, asked_card] in asked_hand:
        if game.VERBOSE : print("Player", asked_player, "gives", asked_family, asked_card, "to player", player_number)
        hands[player_number].append([asked_family, asked_card])
        hands[asked_player].remove([asked_family, asked_card])
        return True, hands, pile
    
    else:
        if game.VERBOSE : print("Player", asked_player, "says 'Go Fish!'")
        card = pile.pop()
    
    hands[player_number].append(card)

    return (card[0] == asked_family, card[1] == asked_card), hands, pile


def play_simulation_turn(hands, pile, player_number, families_scored, verbose=game.VERBOSE):
    lucky = True
    while lucky:
        print("Your hand :", hands[player_number],"\n")
        lucky, hands, pile = ask_random(hands, pile, player_number)

        score_guy, family_scored = game.is_family_scored(hands)
        if score_guy>=0 : 
            game.score_family(hands, family_scored, score_guy, families_scored)

        if len(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play

        if lucky and verbose : print("Player", player_number, "got lucky and can play again")

    return hands, pile


def play_simulation_game(player_number, hands, families_scored, verbose=game.VERBOSE):
    hands = hands.copy()
    families_scored = families_scored.copy()

    hands, pile = assume_game_state(hands, families_scored, player_number)

    maxturns = 10e5
    turn=0

    while not game.is_game_over(hands) and turn < maxturns:
        for player_number in range(len(hands)):
            turn+=1
            hands, pile = play_simulation_turn(hands, pile, player_number, families_scored)

    scores = game.compute_scores(families_scored)

    return scores