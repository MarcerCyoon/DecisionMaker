import json
import csv
import math

# Calculate years active by subtracting the player's draft year from the current year
def yearsActive(player):
	return currentYear - int(player['draft']['year'])

# Check to see if a player was released.
# This function works as there are only two ways a player has been released / traded and is ineligible for RFA:
# 1. The player's latest years with team is not equal to the years active
# 2. The player did not play in the latest season.
def wasReleased(player):
	return player['stats'][-1]['yearsWithTeam'] != yearsActive(player) or player['stats'][-1]['season'] != currentYear

# Rules for RFA in Exodus:
# 1. Must be a first round pick
# 2. Must be an expiring rookie (3 or 4 years in the league)
def determineRFA(player):
	if (player['draft']['round'] != 1):
		return 0
	elif (wasReleased(player)):
		return 0
	elif (yearsActive(player) != 3 and yearsActive(player) != 4):
		return 0
	else:
		return 1

def calc_teamRating(players):
	ovrs = []
	for player in players:
		ovrs.append(player['ratings'][-1]['ovr'])

	while (len(ovrs) < 10):
		ovrs.append(0)

	# Formula taken straight out of BBGM code
	predictedMOV = -124.13 +0.4417 * math.exp(-0.1905 * 0) * ovrs[0] +0.4417 * math.exp(-0.1905 * 1) * ovrs[1] +0.4417 * math.exp(-0.1905 * 2) * ovrs[2] + 0.4417 * math.exp(-0.1905 * 3) * ovrs[3] +0.4417 * math.exp(-0.1905 * 4) * ovrs[4] +0.4417 * math.exp(-0.1905 * 5) * ovrs[5] +0.4417 * math.exp(-0.1905 * 6) * ovrs[6] +0.4417 * math.exp(-0.1905 * 7) * ovrs[7] +0.4417 * math.exp(-0.1905 * 8) * ovrs[8] +0.4417 * math.exp(-0.1905 * 9) * ovrs[9]
	rawOVR = (predictedMOV * 50) / 20 + 50

	return max(0, rawOVR)

# Add up all the contracts of a team to find its payroll
def addContracts(players):
	total = 0

	for player in players:
		total += player['contract']['amount']

	return total / 1000

def create_playerLine(player, numContracts, writer):
	name = player['firstName'] + " " + player['lastName']
	age = currentYear - int(player['born']['year'])
	ovr = player['ratings'][-1]['ovr']
	askingAmount = player['contract']['amount'] / 1000
	isRFA = determineRFA(player)

	line = [name, age, ovr, askingAmount, isRFA, numContracts]
	writer.writerow(line)

def create_teamLine(row, teamData, teamPlayers, writer):
	teamName = row[0]
	offerAmount = row[2]
	powerRank = calc_teamRating(teamPlayers) # fix
	payroll = addContracts(teamPlayers) # fix
	role = row[3]

	if (row[4] == "Mid-Level Exception (MLE)"):
		isMLE = 1
	else:
		isMLE = 0

	facilitiesRank = teamData['budget']['facilities']['rank']

	line = [teamName, offerAmount, powerRank, payroll, role, isMLE, facilitiesRank]
	writer.writerow(line)


with open("export.json", "r", encoding='utf-8-sig') as file:
    export = json.load(file)

text = export['meta']['phaseText']
currentYear = int(text.split(" ")[0])

# Generate dictionary of each team and their tids
teamDict = dict()
for team in export['teams']:
		teamName = team['region'] + " " + team['name']
		teamDict[teamName] = team['tid']

# Resets CSV
open("generated.csv", "w").close()

with open("generated.csv", "a+", newline='') as file:
	writer = csv.writer(file, delimiter=",")
	start = ["Name/Team", "Age/Offer", "OVR/Power Ranking", "Asking Amount/Team Payroll", "isRFA (0 or 1)/Player Role", "# of Contracts/Use MLE (0 or 1)", "null spot/Facilities Rank"]
	writer.writerow(start)

	# Columns for offers.csv: Team Name, Player Being Offered, Offer Amount, Role, Exception
	with open("offers.csv", "r") as offers:
		len_reader = csv.reader(offers)
		length = len(list(len_reader)) - 2
		print("Length: " + str(length))

		offers.seek(0)
		reader = csv.reader(offers)
		next(reader)
		row = next(reader)

		while length > 0:
			nameList = row[1].split(" ")[:2]
			player = list(filter(lambda player: player['firstName'].strip() == nameList[0] and player['lastName'].strip() == nameList[1], export['players']))[0]

			offerList = []
			offerList.append(row)
			while True:
				row = next(reader)
				length -= 1
				print("Current Row in While: " + str(row))
				if (row[1] == (player['firstName'].strip() + " " + player["lastName"].strip())):
					offerList.append(row)
					print("Offer List: " + str(offerList))

					if (length == 0):
						break

				else:
					print("those were all the offers!")
					break

			numContracts = len(offerList)
			create_playerLine(player, numContracts, writer)

			for t_row in offerList:
				teamPlayers = []
				for player in export['players']:
				    if(player['tid'] == teamDict[t_row[0]]):
				        teamPlayers.append(player)

				teamData = export['teams'][teamDict[t_row[0]]]
				create_teamLine(t_row, teamData, teamPlayers, writer)