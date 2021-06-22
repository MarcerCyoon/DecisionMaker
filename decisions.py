import random
import defaults

def willSign(signInterest):
    # Sign algorithm is literally a d100 roll, compared to the final interest.
    # Used for both re-signs and to lower randomness in open FA.
    # If randomness is removed, any interest above 50 works.

    check = random.randint(1, 100) if defaults.RANDOMNESS else 50

    defaults.log_output("d100: {}".format(check))
    defaults.log_output("Final Interest: {}".format(signInterest))
    
    if (check <= signInterest):
        return True
    
    else:
        return False

def makeDecision(interests):
    if defaults.RANDOMNESS:
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
            tot += max(0, interests[i])

        for i in range(0, num):
            if tot != 0:
                percents.append((interests[i] / (tot)) * 100)
            else:
                percents.append(0)
        
        defaults.log_output(percents)
        
        check = random.randint(1, 100)

        defaults.log_output("Percents Roll: {}".format(check))
        
        if (check < percents[0]):
            return 0
        else:
            add = percents[0]
            for i in range(1, num):
                bracket = add + percents[i]
                
                if (check < bracket):
                    return i
                
                add += percents[i]
        
        # Fail-Safe: if this function returned -1, something went terribly wrong.
        return -1

    else:
        # If randomness is removed, simply return the highest value.
        high = -999
        high_i = -1

        for i in range(0, len(interests)):
            if high < interests[i]:
                high = interests[i]
                high_i = i

        return high_i