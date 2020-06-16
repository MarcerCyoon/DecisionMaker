# Main Body Function
# All the input stuff is handled here.
# Please note that the spreadsheet input is a bit finnicky.

# If being used as a module, set sys.path correctly.
if not __name__ == "__main__":
	import sys
	import os
	sys.path.append(os.getcwd() + "\\DecisionMaker")

import csv
import json
from faclass import Player
from faclass import teamOffer
import decisions
import autojson
import defaults

def calc_capSpace(payroll):
	# This multiply-by-ten fix is done to avoid floating point errors. Basically, we multiple
	# by ten to make them natural numbers, perform arithmetic, then divide the number by ten
	# and return it as a decimal.

	fix = max(0, defaults.SOFT_CAP * 10 - payroll * 10)
	return (fix / 10)

# What follows is a bunch of subroutines for check_validity.
def MLE_amount(payroll):
    if payroll <= defaults.APRON_CAP:
        return 9.5
    elif payroll < defaults.HARD_CAP:
        return min(5.5, defaults.HARD_CAP - payroll)
    else:
        print("Team is hard capped!")
        return 0

def check_hardCap(bid):
	if bid.offerAmount + bid.capSpace <= defaults.HARD_CAP:
		return True
	else:
		return False

# Function that checks if an offer is valid with salary cap rules.
def check_validity(player, bid, isResign, isMLE, payroll):
	print(defaults.HARD_CAP)
	if bid.offerAmount > defaults.MAX_SALARY:
		return 0

	if not check_hardCap(bid):
		return 0

	if not isResign:
		if bid.offerAmount <= bid.capSpace or bid.offerAmount == defaults.MIN_SALARY or (isMLE == 1 and bid.offerAmount <= MLE_amount(payroll)):
			return 1
		else:
			violation = "The {} don't have enough cap space to sign {}.\n".format(bid.teamName, player.name)
			print(violation)

			with open("list.txt", "a+") as file:
				file.write(violation)

			return 0
	else:
		return 1

# Boiler-plate code that uses the CSV to make decisions. Most of the credit for this code goes to Tus.
def csvToDecisions(isResign, name):
	# Decision Array that stores all decision results. This will be returned so that the export can be updated.
	decisionArr = []

	with open(name) as file:
		reader = csv.reader(file)
		next(reader)
		for row in reader:
			player = Player(row[0], int(row[1]), int(row[2]), float(row[3]), int(row[4]))

			if int(row[5]) == 1:
				row = next(reader)
				bid = teamOffer(row[0], float(row[1]), int(row[2]), calc_capSpace(float(row[3])), int(row[4]), int(row[6]), int(row[7]), row[8])

				if int(check_validity(player, bid, int(isResign), int(row[5]), float(row[3]))):
					interest = player.returnInterest(bid)

					if player.isrfa:
						print("Player is RFA. Reducing interest.")
						interest -= 15

					resign = decisions.willSign(interest - 5)

					if (resign):
						result = "Final Decision: {} will sign with the {} on a ${}M contract for {} year{}.\n\n".format(player.name, bid.teamName, "%0.2f" % bid.offerAmount, bid.offerYears, ("" if bid.offerYears == 1 else "s"))
						decisionArr.append([player.name, bid.teamName, bid.offerAmount, bid.offerYears])

					else:
						result = "Final Decision: {} will not sign with the {}.\n\n".format(player.name, bid.teamName)

					print(result)

					# list.txt is a text file that holds all decisions only for easy access
					with open("list.txt", "a+") as file:
						file.write(result)

			else:
				offers = []
				interests = []
				for i in range(int(row[5])):
					row = next(reader)
					bid = teamOffer(row[0], float(row[1]), int(row[2]), calc_capSpace(float(row[3])), int(row[4]), int(row[6]), int(row[7]), row[8])

					if int(check_validity(player, bid, int(isResign), int(row[5]), float(row[3]))):
						offers.append(bid)
						interests.append(player.returnInterest(bid))

				numCheck = min(3, len(offers))
				if offers:
					for i in range(0, numCheck):
						decisionAns = decisions.makeDecision(interests)
						print("Choice: {}; time to check".format(offers[decisionAns].teamName))

						if (decisions.willSign(interests[decisionAns])):
							decisionTeam = offers[decisionAns].teamName
							decisionAmount = offers[decisionAns].offerAmount
							decisionYears = offers[decisionAns].offerYears

							result = "Final Decision: {} will sign with the {} on a ${}M contract for {} year{}.\n\n".format(player.name, decisionTeam, "%0.2f" % decisionAmount, decisionYears, ("" if decisionYears == 1 else "s"))
							decisionArr.append([player.name, decisionTeam, decisionAmount, decisionYears])
							print(result)

							with open("list.txt", "a+") as file:
								file.write(result)

							break

						if (i == numCheck - 1):
							result = "Final Decision: {} is unsatisfied with their current offers and will not sign with any teams.\n\n".format(player.name)
							print(result)

							with open("list.txt", "a+") as file:
								file.write(result)

				else:
					print("There were no valid offers for {}\n\n".format(player.name))

	with open("decisionMatrix.csv", "w", newline='', encoding="utf-8-sig") as file:
		writer = csv.writer(file)

		writer.writerow(["Name", "Signed With:", "AAV", "Years"])
		for decision in decisionArr:
			writer.writerow(decision)

	return decisionArr

def main():
	auto = input("If you desire Manual Input, type 0. If you are using a spreadsheet/csv of some kind, type 1. If you want to auto-create a csv and automate most of the process, type 2: ")

	# Resets the list.txt file
	open("list.txt", "w").close()

	if int(auto) == 2:
		with open("export.json", "r", encoding='utf-8-sig') as file:
			export = json.load(file)

		autojson.autocreate(export)
		isResign = input("Is this concerning Re-signings? If yes, type 1. If not, type 0: ")
		decisionArr = csvToDecisions(isResign, name="generated.csv")

		update = input("Type 1 if you want to automate ALL above signings. If there are errors or priority conflicts, type 0 to not auto: ")

		if int(update):
			autojson.updateExport(isResign, decisionArr, export)

	elif int(auto) == 1:
		name = input("What is the name of the csv file? Include the .csv: ")
		# file is formatted as follows: headers, then next line has player information:
		# Name/Team, Age/Offer, OVR/Power Ranking, Asking Amount/Team Payroll, isRFA (0 or 1)/Player Role, # of Contracts/Use MLE (0 or 1), null spot/Offer Years, null spot/Facilities Rank, null spot/Options
		# Player information line
		# contracts
		# next player information line, and so on
		isResign = input("Is this concerning Re-signings? If yes, type 1. If not, type 0: ")
		decisionArr = csvToDecisions(isResign, name=name)

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
			years = input("Input Offer Years: ")
			option = input("Type TO for TO, PO for PO, and None for No Option: ")
			power = input("Input Power Ranking: ")
			facility = input("Input Facilities Rank: ")
			capSpace = input("Input Current Team Payroll (excluding player being offered's contract): ")
			role = input("Input Role of the player in the team (0-4): ")

			bid = teamOffer(teamName, float(offer), int(power), calc_capSpace(float(capSpace)), int(role), int(years), int(facility), option)
			isResign = True

			if int(check_validity(player, bid, isResign, 1, capSpace)):
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
			run = input("Number of contracts being offered to this player: ")

			offers = []
			interests = []

			for i in range(0, int(run)):
				teamName = input("Input Team Name: ")
				offer = input("Input Offer Amount (in millions): ")
				years = input("Input Offer Years: ")
				option = input("Type TO for TO, PO for PO, and None for No Option: ")
				power = input("Input Power Ranking: ")
				facility = input("Input Facilities Rank: ")
				capSpace = input("Input Current Team Payroll (excluding player being offered's contract): ")
				role = input("Input Role of the player in the team (0-4): ")

				bid = teamOffer(teamName, float(offer), int(power), calc_capSpace(float(capSpace)), int(role), int(years), int(facility), option)

				if int(check_validity(player, bid, 0, 1, capSpace)):
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

if __name__ == "__main__":
	main()
