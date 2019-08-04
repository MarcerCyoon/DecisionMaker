# Main Body Function
# All the input stuff is handled here.
# Please note that the spreadsheet input is a bit finnicky.

import pandas as pd
from faclass import Player
from faclass import teamOffer
import decisions

auto = input("If you desire Manual Input, type 0. If you are using a spreadsheet/csv of some kind, type 1: ")

if int(auto):
    # TODO — fix this shit

    name = input("What is the name of the csv file? Include the .csv: ")

    df = pd.read_csv(name)
    df = df.dropna()

    for i in range(0, len(df)):
        player = Player(df['Player'].iloc[i], df['Age'].iloc[i], df['OVR'].iloc[i], df['askingAmount'].iloc[i], df['isRFA'].iloc[i])
        resignOffer = teamOffer(df['Prev Team'].iloc[i], df['resignOffer'].iloc[i], df['powerRank'].iloc[i], df['capSpace'].iloc[i], df['role'].iloc[i])
        
        interest = player.returnInterest(resignOffer)

        if (player.isrfa == 1):
            # RFA Penalty — RFAs are more likely to test the open market.
            resignInterest -= 20
        
        decision = willSign(interest)
        
        if decision:
            print("{} has decided to re-sign with the {}.".format(player.name, resignOffer.teamName))
        else:
            print("{} has decided not to re-sign with the {}.".format(player.name, resignOffer.teamName))


else:
    name = input("Input name: ")
    age = input("Input age: ")
    ovr = input("Input overall in BBGM: ")
    ask = input("Input asking amount (in millions): ")
    isrfa = input("If this player is a UFA, type 0. If this player is an RFA, type 1: ")

    player = Player(name, int(age), int(ovr), float(ask), int(isrfa))

    situation = input("If you are evaluating a re-sign situation, type 1. If this is an Open FA situation, type 2: ")

    if int(situation) == 1:
        teamName = input("Input Re-signing Team Name: ")
        offer = input("Input Offer Amount (in millions): ")
        power = input("Input Power Ranking: ")
        capSpace = input("Input Team Cap Space (excluding player being offered's contract): ")
        role = input("Input Role of the player in the team (0-4): ")
        
        bid = teamOffer(teamName, float(offer), int(power), float(capSpace), int(role))
        
        resignInterest = player.returnInterest(bid)
        
        if (player.isrfa == 1):
            # RFA Penalty — RFAs are more likely to test the open market.
            resignInterest -= 20
        
        resign = decisions.willSign(resignInterest)
        
        if (resign):
            print("{} will re-sign with the {}.".format(player.name, bid.teamName))
        else:
            print("{} will not re-sign with the {}.".format(player.name, bid.teamName))

            
    else:
        run = input("How many contracts being offered to this player? ")

        offers = []

        for i in range(0, int(run)):
            teamName = input("Input Team Name: ")
            offer = input("Input Offer Amount (in millions): ")
            power = input("Input Power Ranking: ")
            capSpace = input("Input Team Cap Space (excluding player being offered's contract): ")
            role = input("Input Role of the player in the team (0-4): ")

            bid = teamOffer(teamName, float(offer), int(power), float(capSpace), int(role))
            offers.append(bid)

        interests = []

        for i in range(0, int(run)):
            interests.append(player.returnInterest(offers[i]))

        while True:
            decisionAns = decisions.makeDecision(interests)
            print("Choice: {}; time to check".format(offers[decisionAns].teamName))
            if (decisions.willSign(interests[decisionAns])):
                break

        decisionTeam = offers[decisionAns].teamName

        print("Final Decision: {} will sign with the {}".format(player.name, decisionTeam))

input("Press ENTER to exit")