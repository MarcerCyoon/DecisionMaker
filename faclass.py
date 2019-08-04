import math
import random

# Subroutines – also makes things look nice and easy to find.

def get_moneyImportance(age, ovr):
    rnd = random.uniform(-.15, .15)
    return (.3 + rnd) * (1/(1+math.exp(.13343*(age - 31)))) + (.7 - rnd) * (1/(1+math.exp(-.08673*(ovr - 55))))

def get_roleImportance(age, ovr):
    rnd = random.uniform(-.15, .15)
    return (.7 + rnd) * (.5 / (1 + math.exp(-.05545 * (ovr - 55)))) + (.3 - rnd) * ((-3/1690)*(age**2) + (93/845)*age - (2207/1690))

def get_ringImportance(age):
    rnd = random.uniform(-.1, .1)
    return (.0192308 * age) - .146154 + rnd


def calcImportance(age, ovr):
    moneyImportance = get_moneyImportance(age, ovr)
    roleImportance = get_roleImportance(age, ovr)
    ringImportance = get_ringImportance(age)
    
    print("Ring Importance: {}".format(ringImportance))
    print("Role Importance: {}".format(roleImportance))
    print("Money Importance: {}".format(moneyImportance))

    return (ringImportance, roleImportance, moneyImportance)

class Player:
    def __init__(self, name, age, ovr, askingAmount, isrfa):
        self._name = name
        self._age = age

        # OVR Rating in BBGM
        self._ovr = ovr
        
        # Asking Amount, in Millions
        self._askingAmount = askingAmount
        
        # Whether the player is an RFA or not
        self._isrfa = isrfa

        self._ringImportance, self._roleImportance, self._moneyImportance = calcImportance(self._age, self._ovr)
    
    @property
    def name(self):
        return self._name
    
    @property
    def age(self):
        return self._age

    @property
    def ovr(self):
        return self._ovr
    
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
        sigma = (contractInterest * self._moneyImportance) + (strengthInterest * self._ringImportance) + (roleInterest * self._roleImportance)
        interest = int(sigma / (self._ringImportance + self._moneyImportance + self._roleImportance))

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
        