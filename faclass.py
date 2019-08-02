import math
import random

def calcImportance(age):
    # Don't know why I have to do this but I'm too lazy and don't want too many parantheses lol
    # Determines the importance of rings and contention through a logistic function based on age.
    # The higher the age, the more important winning matters.
    # The importance of winning caps out at 85% and the low is 15%.
    # The mid-point is 31, where your winning importance is at 55%.
    # I've also added a noise variable so that the mid-point can be adjusted. Adds some realism.
    noise = random.randint(-20, 20) / 10
    huh = 1 + math.exp(-1 * (age) + (31 + noise))
    ringImportance = (0.70 / huh) + 0.15

    # Role Importance and Money Importance feel like they are closely correlated, so they take
    # what's left of the pie after the winning importance.
    # Role Importance is simply a third of the remainder while money importance is two-thirds.
    roleImportance = (1 - ringImportance) / 3
    moneyImportance = (1 - ringImportance) - roleImportance
    
    print("Ring Importance: {}".format(ringImportance))
    print("Role Importance: {}".format(roleImportance))
    print("Money Importance: {}".format(moneyImportance))

    return (ringImportance, roleImportance, moneyImportance)

class Player:
    def __init__(self, name, age, askingAmount, isrfa):
        self._name = name
        self._age = age
        
        # Asking Amount, in Millions
        self._askingAmount = askingAmount
        
        # Whether the player is an RFA or not
        self._isrfa = isrfa

        self._ringImportance, self._roleImportance, self._moneyImportance = calcImportance(self._age)
    
    @property
    def name(self):
        return self._name
    
    @property
    def age(self):
        return self._age
    
    @property
    def askingAmount(self):
        return self._askingAmount
    
    @property
    def isrfa(self):
        return self._isrfa
    
    def returnInterest(self, teamOffer):
        # Contract Interest calculation is a bit wonky.
        # To accomodate for some of BBGM's fuzzing, we set our own maximum and minimum based off the amount
        # offered by BBGM.
        stddev = self._askingAmount / 3
        stddev2 = self._askingAmount / 5

        # The high offer is set to the askingAmount + a fifth of the askingAmount. If you offer the high,
        # the contract interest will be equal to a 100.
        # On the other hand, the low offer is set to the askingAmount - a third of the askingAmount. If you
        # offer the low, the contract interest will be equal to 0.
        # If you go lower than the low it defaults to 0; if you go higher than the high it defaults to 100.
        low = self._askingAmount - stddev
        high = self._askingAmount + stddev2

        interestVar = teamOffer.offerAmount - low
        comp = high - low
        
        # Contract Interest is ultimately calculated linearly.
        # Might change this.
        contractInterest = (interestVar / comp) * 100

        if (contractInterest < 0):
            contractInterest = 0
        elif (contractInterest > 100):
            contractInterest = 100
        
        print("Contract Interest: {}".format(contractInterest))

        # Power Tier of 1 means you're in the Top 5, Power Tier of 6 mean's you're in the Bottom 5.
        powerTier = int(math.ceil(int(teamOffer.powerRank / 5)))

        print("Power Tier: {}".format(powerTier))

        # If you have 30M+ in cap space after signing the guy, you get a -2 bonus.
        # If you have 15M+ in cap space after signing the guy, you get a -1 bonus.
        # Otherwise, 0.
        capTier = int(math.floor(int(teamOffer.capSpace / 15)))

        print("Cap Tier: {}".format(capTier))

        finalTier = powerTier - capTier

        print("Final Tier: {}".format(finalTier))

        # If there are any shenanigans involving having too high/low a tier, this checks for it.
        if (finalTier > 6):
            finalTier = 6
        elif (finalTier < 1):
            finalTier = 1
        
        # Strength Interest is ultimately calculated linearly.
        strengthInterest = 120 - (20 * finalTier)
        
        print("Strength Interest: {}".format(strengthInterest))
        
        # Role Interest is a linear function using the role value of the player. See details about that
        # in the constructor for teamOffer.
        roleInterest = 25 * teamOffer.role
        
        print("Role Interest: {}".format(roleInterest))
        
        # Final interest is a weighted average of the three interests.
        interest = int((contractInterest * self._moneyImportance) + (strengthInterest * self._ringImportance) + (roleInterest * self._roleImportance))

        # Fuzz adds a bit of "fuzz" to the interest so that there are no guarantees, ever.
        fuzz = random.randint(-5, 5)

        interest += fuzz

        print("Final Interest: {}".format(interest))
        
        return interest
        
class teamOffer:
    def __init__(self, teamName, offerAmount, powerRank, capSpace, role):
        # Team Name
        self._teamName = teamName
        
        # The Contract Offered by the Team
        self._offerAmount = offerAmount
        
        # The Power Ranking of the Team (out of 30)
        self._powerRank = powerRank
        
        # Team's Cap Space (including player's contract if they sign)
        if (capSpace - offerAmount < 0):
        	self._capSpace = 0
        else:
        	self._capSpace = capSpace - offerAmount
        
        # The Role the Player will have on the team. (0 — Cap Room, 1 — Expendable, 2 — Bench, 3 — Starter, 4 - Star)
        self._role = role
        
    @property
    def teamName(self):
        return self._teamName
    
    @property
    def offerAmount(self):
        return self._offerAmount
    
    @property
    def powerRank(self):
        return self._powerRank
    
    @property
    def capSpace(self):
        return self._capSpace
    
    @property
    def role(self):
        return self._role  
        