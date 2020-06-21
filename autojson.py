import json
import csv
import math
import collections
import defaults

# Update an existing export named "export.json" with Free Agency decisions found in a decisionArr.
# This should perfectly emulate actually signing them in the BBGM game.
def updateExport(isResign, decisionArr, export):
	print(decisionArr)

	currentPlayers = []

	for player in export['players']:
		if (player['tid'] != -3 and player['tid'] != -2):
			currentPlayers.append(player)

	# Generate dictionary of each team and their tids
	teamDict = dict()
	for team in export['teams']:
		teamName = team['region'] + " " + team['name']
		teamDict[teamName] = team['tid']

	text = export['meta']['phaseText']
	currentYear = int(text.split(" ")[0])
	phase = text.split(" ")[1]

	for decision in decisionArr:
		player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == decision[0], currentPlayers))[0]
		tid = teamDict[decision[1]]
		player['tid'] = tid
		player['contract']['amount'] = float(decision[2]) * 1000

		# If the current phase of the game is the "Regular Season" or the "Preseason",
		# then signing a contract will include the current year.
		# For example, if Isaiah Thomas signs a 1-year deal in 2020, it will expire at the end of 2020.
		# However, if you sign Isaiah Thomas in a 1-year deal in the 2020 offseason, it will expire at
		# the end of 2021. Thus, a distinction needs to be made depending on the current phase.
		if (phase == "regular" or phase == "preseason"):
			firstYearOfContract = currentYear

		else:
			firstYearOfContract = currentYear + 1

		exp = int(decision[3]) + firstYearOfContract - 1
		player['contract']['exp'] = exp

		# Second, we must also correct every player's salary info and add the new contract amount
		# such that their career earnings are updated.
		for i in range(firstYearOfContract, exp + 1):
			salaryInfo = dict()
			salaryInfo['season'] = i
			salaryInfo['amount'] = float(decision[2]) * 1000
			player['salaries'].append(salaryInfo)

		# To fully emulate the way signings are worked in-game, we must also create a corresponding event
		# in the game's code that tells us that so-and-so signed with such-and-such team. This is important
		# not only for error-identification purposes, but also makes league history and transactions
		# be kept complete.
		event = dict()

		# For some reason, the text for events only necessitates the team code and "label name": we only need
		# Celtics, not Boston Celtics.
		code = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['abbrev']
		labelName = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['name']

		if int(isResign):
			event['type'] = 'reSigned'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> re-signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % float(decision[2]), exp)

		else:
			event['type'] = 'freeAgent'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % float(decision[2]), exp)

		event['pids'] = [player['pid']]
		event['tids'] = [tid]
		event['season'] = currentYear
		# The eid of the current event would have to be the next available eid.
		# That would just be the current amount of events, as each event has a corresponding
		# eid and they start at 0 instead of 1.
		event['eid'] = len(export['events'])

		export['events'].append(event)

		# We must also create a transaction dictionary for the player if it is not a re-signing.
		if not int(isResign):
			gamePhase = list(filter(lambda attribute: attribute['key'] == "phase", export['gameAttributes']))[0]['value']
			transaction = {
				"season": currentYear,
				"phase": gamePhase,
				"tid": tid,
				"type": "freeAgent"
			}

			try:
				player['transactions'].append(transaction)
			except KeyError:
				player['transactions'] = []
				player['transactions'].append(transaction)

	with open("updated.json", "w") as file:
		json.dump(export, file)
		print("New Export Created.")

# Check to see if a player exists by trying to catch an IndexError
def playerExists(name, players):
	try:
		list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == name, players))[0]
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
	try:
		if (player['draft']['round'] != 1):
			return 0
		elif (wasReleased(player, currentYear)):
			return 0
		elif (yearsActive(player, currentYear) != 3 or yearsActive(player, currentYear) != 4):
			return 0
		else:
			return 1
	except IndexError:
		return 0

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
def addContracts(players, releasedPlayers):
	total = 0

	for player in players:
		total += player['contract']['amount']

	for player in releasedPlayers:
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
	payroll = teamPower[3]
	role = row[4]
	option = row[6]

	if (row[5] == "Mid-Level Exception (MLE)"):
		isMLE = 1
	else:
		isMLE = 0

	offerYears = row[3]
	facilitiesRank = min(30, teamData['budget']['facilities']['rank'])

	line = [teamName, offerAmount, powerRank, payroll, role, isMLE, offerYears, facilitiesRank, option]
	writer.writerow(line)

# Auto-create a working FA CSV.
def autocreate(export):
	text = export['meta']['phaseText']
	currentYear = int(text.split(" ")[0])

	# Set default values based on export's values
	defaults.SOFT_CAP = list(filter(lambda attribute: attribute['key'] == "salaryCap", export['gameAttributes']))[0]['value'] / 1000
	defaults.HARD_CAP = list(filter(lambda attribute: attribute['key'] == "luxuryPayroll", export['gameAttributes']))[0]['value'] / 1000
	defaults.MAX_SALARY = list(filter(lambda attribute: attribute['key'] == "maxContract", export['gameAttributes']))[0]['value'] / 1000
	defaults.MIN_SALARY = list(filter(lambda attribute: attribute['key'] == "minContract", export['gameAttributes']))[0]['value'] / 1000

	# Since there are only two caps held in the export, calculated the third cap (apron/luxury) with *math*
	# This equation was found in the laziest, hackiest way possible:
	# a linear fit to (33, 130) and (38, 156) since those are the corresponding x and y values for
	# the Exodus League and NBA Chat League.
	defaults.APRON_CAP = 5.2 * (defaults.HARD_CAP - defaults.SOFT_CAP) - 41.6

	# Generate dictionary of each team and their tids
	teamDict = dict()
	for team in export['teams']:
		teamName = team['region'] + " " + team['name']
		teamDict[teamName] = team['tid']

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

		# Get released players, as they count against the cap
		releasedPlayers = list(filter(lambda release: release['tid'] == tid, export['releasedPlayers']))

		name = team['region'] + " " + team['name']
		rating = calc_teamRating(teamPlayers)
		score = calc_score(rating, team)
		payroll = addContracts(teamPlayers, releasedPlayers)
		powerArr.append([name, score, rating, payroll, -1])

	powerArr = sorted(powerArr, key=lambda i:i[1], reverse=True)

	for i in range(0, len(powerArr)):
		# Doing min(i + 1, 30) because the PR value can only go from 1-30
		powerArr[i][4] = min(i + 1, 30)

	# Resets CSV
	open("generated.csv", "w").close()

	currentPlayers = []

	for player in export['players']:
		if (player['tid'] != -3 and player['tid'] != -2):
			currentPlayers.append(player)

	with open("generated.csv", "a+", newline='', encoding="utf-8-sig") as file:
		writer = csv.writer(file, delimiter=",")
		start = ["Name/Team", "Age/Offer", "OVR/Power Ranking", "Asking Amount/Team Payroll", "isRFA (0 or 1)/Player Role", "# of Contracts/Use MLE (0 or 1)", "null spot/Offer Years", "null spot/Facilities Rank", "null spot/Option Type"]
		writer.writerow(start)

		# Columns for offers.csv: Team Name, Player Being Offered, Offer Amount, Offer Years, Role, Exception, Option
		with open("offers.csv", "r", encoding="utf-8-sig") as offers:
			reader = csv.reader(offers)
			# Using an array as it's easier to use than the reader
			# The most notable advantage is being able to check/access values that have already been "read"
			csvData = []
			for row in reader:
				csvData.append(row)


			i = 0
			while i < len(csvData) - 1:
				# Start at 1 since row 0 has headers
				i += 1
				print(csvData[i])
				name = csvData[i][1].strip()

				if (playerExists(name, currentPlayers)):
					# This filters the entire list for the player we want (the one that has the same name.)
					player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == name, currentPlayers))[0]

				else:
					print("{} does not exist!".format(name))
					break

				offerList = []
				offerList.append(csvData[i])

				# We assume the CSV is sorted by player such that the same player's offers come in succession.
				while i < len(csvData) - 1:
					i += 1
					print(csvData[i])

					# We check if the name of the current row's player is the same as the player.
					# If this is true, we add the row to one of the player's offers and then check if that was the last offer overall.
					# If it is false, that must mean that the previous row was the last offer and we can move onto writing lines
					# for this player and his offers.
					if (csvData[i][1].strip() == (player["firstName"].strip() + " " + player["lastName"].strip())):
						offerList.append(csvData[i])

						if (i == len(csvData)):
							break

					else:
						print("Those were all the offers!")
						# We also move back one here so that when we add right after the start of the while, we will end up
						# with the same row.
						i -= 1
						break

				numContracts = len(offerList)
				create_playerLine(player, numContracts, currentYear, writer)

				for t_row in offerList:
					teamName = t_row[0].strip()
					teamData =  list(filter(lambda team: team['tid'] == teamDict[teamName], export['teams']))[0]
					teamPower = find_by_inner_value(powerArr, teamName, 0)

					create_teamLine(t_row, teamData, teamPower, writer)
