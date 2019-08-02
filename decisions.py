import random

def willResign(resignInterest):
    check = random.randint(1, 100)

    # Re-sign algorithm is literally a d100 roll, compared to the final interest.

    print("d100: {}".format(check))
    print("Final Interest: {}".format(resignInterest))
    
    if (check <= resignInterest):
        return True
    
    else:
        return False

def makeDecision(interests):
	# Open FA / mid-season FA decisions are made through a kind of average system.
	# In essence, each team's interest are added up to create a sum.
	# Then, each team's interest percentage is calculated by dividing the interest from the sum.
	# This calculates how the player feels about each team, relatively.
	# For example, a 100 interest offer is appealing, but if you have multiple 100 interest offers,
	# the player views them all equally.
	# After this percentage calculation, a d100 is rolled.
	# Whichever percent bracket the d100 falls into is the ultimate winner.

    num = len(interests)
    tot = 0
    
    percents = []
    
    for i in range(0, num):
        tot += interests[i]
        
        
    for i in range(0, num):
        percents.append(interests[i] / (tot * 100))
        
    check = random.randint(1, 100)
    
    if (check < percents[0]):
        return 0
    else:
        add = percents[0]
        for i in range(1, num):
            bracket = add + percents[i]
            
            if (check < bracket):
                return i
            
            add += percents[i]
    
    # Fail-Safe: if this function returned -1, something is terribly wrong.
    return -1