import json
import csv
import math
import collections

# Global teamDict, @ me fools
with open("export.json", "r", encoding='utf-8-sig') as file:
		
		# Generate dictionary of each team and their tids
		teamDict = dict()
		for team in json.load(file)['teams']:
				teamName = team['region'] + " " + team['name']
				teamDict[teamName] = team['tid']

# Update an existing export named "export.json" with Free Agency decisions found in a decisionArr.
# This should perfectly emulate actually signing them in the BBGM game.
def updateExport(isResign, decisionArr):
	print(decisionArr)

	with open("export.json", "r", encoding='utf-8-sig') as file:
	    export = json.load(file)

	text = export['meta']['phaseText']
	currentYear = int(text.split(" ")[0])
	phase = text.split(" ")[1]

	for decision in decisionArr:
		player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == decision[0], export['players']))[0]
		tid = teamDict[decision[1]]
		player['tid'] = tid
		player['contract']['amount'] = decision[2] * 1000

		# If the current phase of the game is the "Regular Season" or the "Preseason",
		# then signing a contract will include the current year.
		# For example, if Isaiah Thomas signs a 1-year deal in 2020, it will expire at the end of 2020.
		# However, if you sign Isaiah Thomas in a 1-year deal in the 2020 offseason, it will expire at
		# the end of 2021. Thus, a distinction needs to be made depending on the current phase.
		if (phase == "regular" or phase == "preseason"):
			exp = decision[3] + currentYear - 1
			player['contract']['exp'] = exp
		else:
			exp = decision[3] + currentYear
			player['contract']['exp'] = exp

		# To fully emulate the way signings are worked in-game, we must also create a corresponding event
		# in the game's code that tells us that so-and-so signed with such-and-such team. This is important
		# not only for error-identification purposes, but also makes league history and transactions
		# be kept complete.
		event = dict()

		# For some reason, the text for events only necessitates the team code and "label name": we only need
		# Celtics, not Boston Celtics.
		code = export['teams'][tid]['abbrev']
		labelName = decision[1].split(" ")[-1]
		
		if (not isResign):
			event['type'] = 'reSigned'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> re-signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % decision[2], exp)

		else:
			event['type'] = 'freeAgent'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % decision[2], exp)
		
		event['pids'] = [player['pid']]
		event['tids'] = [tid]
		event['season'] = currentYear
		# The eid of the current event would have to be the next available eid.
		# That would just be the current amount of events, as each event has a corresponding
		# eid and they start at 0 instead of 1.
		event['eid'] = len(export['events'])

		export['events'].append(event)

	with open("updated.json", "w") as file:
		json.dump(export, file)
		print("New Export Created.")

# Check to see if a player exists by trying to catch an IndexError
def playerExists(name, players):
	try:
		check = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == name, players))[0]
	except IndexError:
		return 0

	return 1

# Small helper function I made so that I could find the right list within a list for a team
# More formal definition:
# For a list within a list, this will return the inner list that has the specified value at the index in the inner list
# Fail condition: array of -1
def find_by_inner_value(array, value, index):
	for i in range(0, len(array)):
		if array[i][index] == value:
			return array[i]

	return [-1]

# Calculate years active by subtracting the player's draft year from the current year
def yearsActive(player, currentYear):
	return currentYear - int(player['draft']['year'])

# Check to see if a player was released.
# This function works as there are only two ways a player has been released / traded and is ineligible for RFA:
# 1. The player's latest years with team is not equal to the years active
# 2. The player did not play in the latest season.
def wasReleased(player, currentYear):
	return player['stats'][-1]['yearsWithTeam'] != yearsActive(player, currentYear) or player['stats'][-1]['season'] != currentYear

# Rules for RFA in Exodus:
# 1. Must be a first round pick
# 2. Must be an expiring rookie (3 or 4 years in the league)
def determineRFA(player, currentYear):
	if (player['draft']['round'] != 1):
		return 0
	elif (wasReleased(player, currentYear)):
		return 0
	elif (yearsActive(player, currentYear) != 3 and yearsActive(player, currentYear) != 4):
		return 0
	else:
		return 1

# Formula taken straight out of BBGM code
def calc_teamRating(players):
	ovrs = []
	for player in players:
		ovrs.append(player['ratings'][-1]['ovr'])

	while (len(ovrs) < 10):
		ovrs.append(0)

	predictedMOV = -124.13 +0.4417 * math.exp(-0.1905 * 0) * ovrs[0] +0.4417 * math.exp(-0.1905 * 1) * ovrs[1] +0.4417 * math.exp(-0.1905 * 2) * ovrs[2] + 0.4417 * math.exp(-0.1905 * 3) * ovrs[3] +0.4417 * math.exp(-0.1905 * 4) * ovrs[4] +0.4417 * math.exp(-0.1905 * 5) * ovrs[5] +0.4417 * math.exp(-0.1905 * 6) * ovrs[6] +0.4417 * math.exp(-0.1905 * 7) * ovrs[7] +0.4417 * math.exp(-0.1905 * 8) * ovrs[8] +0.4417 * math.exp(-0.1905 * 9) * ovrs[9]
	rawOVR = (predictedMOV * 50) / 20 + 50

	return max(0, round(rawOVR))

# Formula also taken straight out of BBGM code
def calc_score(teamRating, team):
	gp = team['stats'][-1]['gp']

	if (gp > 0):
		mov = round(((team['stats'][-1]['pts'] - team['stats'][-1]['oppPts']) / gp) * 10) / 10
		score = (mov * gp) / 82
	else:
		score = 0

	estimated_mov = teamRating * 0.6 - 30
	score += estimated_mov

	last_ten = collections.Counter(team['seasons'][-1]['lastTen'])[1]

	score += -10 + (2 * last_ten)

	return score

# Add up all the contracts of a team to find its payroll
def addContracts(players):
	total = 0

	for player in players:
		total += player['contract']['amount']

	return total / 1000

def create_playerLine(player, numContracts, currentYear, writer):
	name = player['firstName'].strip() + " " + player['lastName'].strip()
	age = currentYear - int(player['born']['year'])
	ovr = player['ratings'][-1]['ovr']
	askingAmount = player['contract']['amount'] / 1000
	isRFA = determineRFA(player, currentYear)

	line = [name, age, ovr, askingAmount, isRFA, numContracts]
	writer.writerow(line)

def create_teamLine(row, teamData, teamPower, writer):
	teamName = row[0].strip()
	offerAmount = row[2]
	powerRank = teamPower[4]
	payroll = teamPower[3] # need to fix to account for released player cap hits
	role = row[4]

	if (row[5] == "Mid-Level Exception (MLE)"):
		isMLE = 1
	else:
		isMLE = 0

	offerYears = row[3]
	facilitiesRank = teamData['budget']['facilities']['rank']

	line = [teamName, offerAmount, powerRank, payroll, role, isMLE, offerYears, facilitiesRank]
	writer.writerow(line)

# Auto-create a working FA CSV.
def autocreate():
	with open("export.json", "r", encoding='utf-8-sig') as file:
	    export = json.load(file)

	text = export['meta']['phaseText']
	currentYear = int(text.split(" ")[0])

	# Generate array that contains each teams score, rating, payroll, and PR
	powerArr = []

	for team in export['teams']:
		tid = team['tid']
		teamPlayers = []
		for player in export['players']:
		    if(player['tid'] == tid):
		        teamPlayers.append(player)

		# Sort in terms of OVR       
		teamPlayers = sorted(teamPlayers, key=lambda i:i['ratings'][-1]['ovr'], reverse=True)

		name = team['region'] + " " + team['name']
		rating = calc_teamRating(teamPlayers)
		score = calc_score(rating, team)
		payroll = addContracts(teamPlayers)
		powerArr.append([name, score, rating, payroll, -1])

	powerArr = sorted(powerArr, key=lambda i:i[1], reverse=True)
	
	for i in range(0, len(powerArr)):
		# Doing min(i + 1, 30) because the PR value can only go from 1-30
		powerArr[i][4] = min(i + 1, 30)

	# Resets CSV
	open("generated.csv", "w").close()

	with open("generated.csv", "a+", newline='') as file:
		writer = csv.writer(file, delimiter=",")
		start = ["Name/Team", "Age/Offer", "OVR/Power Ranking", "Asking Amount/Team Payroll", "isRFA (0 or 1)/Player Role", "# of Contracts/Use MLE (0 or 1)", "null spot/Facilities Rank"]
		writer.writerow(start)

		# Columns for offers.csv: Team Name, Player Being Offered, Offer Amount, Offer Years, Role, Exception
		with open("offers.csv", "r") as offers:
			len_reader = csv.reader(offers)
			length = len(list(len_reader)) - 2

			offers.seek(0)
			reader = csv.reader(offers)
			next(reader)
			row = next(reader)

			while length > 0:
				name = row[1].strip()

				if (playerExists(name, export['players'])):
					# This filters the entire list for the player we want (the one that has the same name.)
					player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == name, export['players']))[0]

				else:
					print("{} does not exist!".format(name))
					break

				offerList = []
				offerList.append(row)
				while True:
					row = next(reader)
					# We use our own iterator, 'length', as doing any sort of check on 'reader' causes things to break (forces it to iterate).
					length -= 1
					if (row[1].strip() == (player['firstName'].strip() + " " + player["lastName"].strip())):
						offerList.append(row)

						if (length == 0):
							break

					else:
						print("Those were all the offers!")
						break

				numContracts = len(offerList)
				create_playerLine(player, numContracts, currentYear, writer)

				for t_row in offerList:
					teamName = t_row[0].strip()
					teamData = export['teams'][teamDict[teamName]]
					teamPower = find_by_inner_value(powerArr, teamName, 0)

					create_teamLine(t_row, teamData, teamPower, writer)