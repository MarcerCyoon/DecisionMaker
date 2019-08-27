# Main Body Function
# All the input stuff is handled here.
# Please note that the spreadsheet input is a bit finnicky.

import csv
from faclass import Player
from faclass import teamOffer
import decisions

MIN_SALARY = .9
HARD_CAP = 142

def capSpace(payroll):
	return max(0, 109 - payroll)


# What follows is a bunch of subroutines for check_validity.
def MLE_amount(payroll):
	if payroll <= 109:
		return float(0)
	elif payroll <= 130:
		return 9.5
	elif payroll <= 142:
		return 5.5
	else:
		print("Team is hard capped!")
		return 0

def calculate_minimum_salary(age, ovr):
	# Honestly, you could probably use enums or more likely a matrix for this — but for now,
	# we'll push as is.

	min_offer = 0
	if age <= 25:
		if ovr >= 75:
			min_offer = 35.3
		elif ovr >= 70:
			min_offer = 23.5
		elif ovr >= 65:
			min_offer = 11.8
		elif ovr >= 60:
			min_offer = 5.5
		else:
			min_offer = MIN_SALARY
	elif age <= 29:
		if ovr >= 80:
			min_offer = 35.3
		elif ovr >= 75:
			min_offer = 29.4
		elif ovr >= 70:
			min_offer = 23.5
		elif ovr >= 65:
			min_offer = 11.8
		elif ovr >= 60:
			min_offer = 5.5
		else:
			min_offer = MIN_SALARY
	elif age <= 35:
		if ovr >= 80:
			min_offer = 29.4
		elif ovr >= 75:
			min_offer = 23.5
		elif ovr >= 70:
			min_offer = 14.7
		elif ovr >= 65:
			min_offer = 5.5
		elif ovr >= 60:
			min_offer = 2.9
		else:
			min_offer = MIN_SALARY
	else:
		if ovr >= 80:
			min_offer = 17.6
		elif ovr >= 75:
			min_offer = 8.8
		elif ovr >= 70:
			min_offer = 5.5
		else:
			min_offer = MIN_SALARY
	return min_offer

def check_hardCap(bid):
	if (bid.offerAmount + bid.capSpace <= HARD_CAP):
		return True
	else:
		return False

def check_tiers(age, ovr, offer, powerrank, name):
	min_offer = calculate_minimum_salary(age, ovr)
	if offer >= min_offer:
		return 1
	# check ring-chasers clause
	elif age >= 30 and powerrank <= 6:
		rings = input("Enter the number of rings that {} has won:".format(name))
		# eligible for the ring-chasers clause
		if int(rings) < 2:
			ovr = ovr - 5
			min_offer = calculate_minimum_salary(age, ovr)
			if offer >= min_offer:
				return 1
			else:
				return 0
		# ineligible for the ring-chasers clause
		else:
			return 0
	# otherwise the offer wasn't high enough
	else:
		return 0

# Function that checks if an offer to a player follows:
# 1. The FA tiers,
# and 2. the salary cap rules.
def check_validity(player, bid, isResign):
	if not check_tiers(player.age, player.ovr, bid.offerAmount, bid.powerRank, player.name):
		print("The {}'s offer for {} is too low, and thus violates the FA Tier rules.".format(bid.teamName, player.name))
		return 0

	if not check_hardCap(bid):
		return 0

	if (not isResign):
		if bid.offerAmount <= bid.capSpace or bid.offerAmount == MIN_SALARY or (int(row[5]) == 1 and bid.offerAmount <= MLE_amount(float(row[3]))):
			return 1
		else:
			print("The {} don't have enough cap space to sign {}.\n\n".format(bid.teamName, player.name))
			return 0
	else:
		return 1


auto = input("If you desire Manual Input, type 0. If you are using a spreadsheet/csv of some kind, type 1: ")

if int(auto):

	name = input("What is the name of the csv file? Include the .csv: ")

	# file is formatted as follows: headers, then next line has player information:
	# Name/Team, Age/Offer, OVR/Power Ranking, Asking Amount/Team Payroll, isRFA (0 or 1)/Player Role, # of Contracts/Use MLE (0 or 1)
	# Player information line
	# contracts
	# next player information line, and so on
	
	isResign = input("Is this concerning Re-signings? If yes, type 1. If not, type 0: ")

	with open(name) as file:
		reader = csv.reader(file)
		next(reader)
		for row in reader:
			player = Player(row[0], int(row[1]), int(row[2]), float(row[3]), int(row[4]))

			if int(row[5]) == 1:
				row = next(reader)
				bid = teamOffer(row[0], float(row[1]), int(row[2]), capSpace(float(row[3])), int(row[4]))
				

				if int(check_validity(player, bid, int(isResign))):
					interest = player.returnInterest(bid)

					if (player.isrfa):
						print("Player is RFA. Reducing interest.")
						interest -= 15

					resign = decisions.willSign(interest - 5)

					if (resign):
						print("{} will sign with the {}.\n\n".format(player.name, bid.teamName))
					else:
						print("{} will not sign with the {}.\n\n".format(player.name, bid.teamName))

			else:
				offers = []
				interests = []
				for i in range(int(row[5])):
					row = next(reader)
					bid = teamOffer(row[0], float(row[1]), int(row[2]), capSpace(float(row[3])), int(row[4]))

					if int(check_validity(player, bid, int(isResign))):
						offers.append(bid)
						interests.append(player.returnInterest(bid))

				numCheck = min(3, len(offers))
				if offers:
					for i in range(0, numCheck):
						decisionAns = decisions.makeDecision(interests)
						print("Choice: {}; time to check".format(offers[decisionAns].teamName))

						if (decisions.willSign(interests[decisionAns])):
							decisionTeam = offers[decisionAns].teamName
							print("Final Decision: {} will sign with the {}\n\n".format(player.name, decisionTeam))
							break

						if (i == numCheck - 1):
							print("Final Decision: {} is unsatisfied with their current offers and will not sign with any teams.".format(player.name))

				else:
					print("There were no valid offers for {}\n\n".format(player.name))

else:
	name = input("Input name: ")
	age = input("Input age: ")
	ovr = input("Input overall in BBGM: ")
	ask = input("Input asking amount (in millions): ")
	isrfa = input("If this player is a UFA, type 0. If this player is an RFA, type 1: ")

	player = Player(name, int(age), int(ovr), float(ask), int(isrfa))

	situation = input("If you are evaluating a re-sign situation or a situation where a player has one offer, type 1. If this is an Open FA situation, type 2: ")

	if int(situation) == 1:
		teamName = input("Input Signing Team Name: ")
		offer = input("Input Offer Amount (in millions): ")
		power = input("Input Power Ranking: ")
		capSpace = input("Input Current Team Payroll (excluding player being offered's contract): ")
		role = input("Input Role of the player in the team (0-4): ")

		bid = teamOffer(teamName, float(offer), int(power), float(capSpace), int(role))
		isResign = True

		if int(check_validity(player, bid, isResign)):
			interest = player.returnInterest(bid)

			if (player.isrfa):
				print("Player is RFA. Reducing interest.")
				interest -= 15

			resign = decisions.willSign(interest - 5)

			if (resign):
				print("{} will sign with the {}.\n\n".format(player.name, bid.teamName))
			else:
				print("{} will not sign with the {}.\n\n".format(player.name, bid.teamName))


	else:
		run = input("How many contracts being offered to this player? ")

		offers = []
		interests = []

		for i in range(0, int(run)):
			teamName = input("Input Team Name: ")
			offer = input("Input Offer Amount (in millions): ")
			power = input("Input Power Ranking: ")
			capSpace = input("Input Team Cap Space (excluding player being offered's contract): ")
			role = input("Input Role of the player in the team (0-4): ")

			bid = teamOffer(teamName, float(offer), int(power), float(capSpace), int(role))
			
			if int(check_validity(player, bid, int(isResign))):
				offers.append(bid)
				interests.append(player.returnInterest(bid))

		numCheck = min(3, len(offers))
		if offers:
			for i in range(0, numCheck):
				decisionAns = decisions.makeDecision(interests)
				print("Choice: {}; time to check".format(offers[decisionAns].teamName))

				if (decisions.willSign(interests[decisionAns])):
					decisionTeam = offers[decisionAns].teamName
					print("Final Decision: {} will sign with the {}\n\n".format(player.name, decisionTeam))
					break

				if (i == numCheck - 1):
					print("Final Decision: {} is unsatisfied with their current offers and will not sign with any teams.".format(player.name))

		else:
			print("There were no valid offers for {}\n\n".format(player.name))

input("Press ENTER to exit")