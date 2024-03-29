import math
import random
import defaults

# Subroutines – also makes things look nice and easy to find.

# Weighted sigmoid
def get_moneyImportance(age, ovr):
    rnd = random.uniform(-0.05, 0.05) if defaults.RANDOMNESS else 0
    return (.3 + rnd) * (1/(1+math.exp(.13343*(age - 31)))) + (.7 - rnd) * (1/(1+math.exp(-.08673*(ovr - 55))))

# Year Importance was found by finding an exponential fit for [100, 0.4], [30, 0.1], [65, 0.3]
def get_yearImportance(ovr):
    rnd = random.uniform(-0.05, 0.05) if defaults.RANDOMNESS else 0
    return rnd + .0928289 * math.exp(.0149981 * ovr)

# Weighted sigmoid
def get_roleImportance(age, ovr):
    rnd = random.uniform(-0.05, 0.05) if defaults.RANDOMNESS else 0
    return (.7 + rnd) * (.5 / (1 + math.exp(-.05545 * (ovr - 55)))) + (.3 - rnd) * ((-3/1690)*(age**2) + (93/845)*age - (2207/1690))

# Weighted sigmoid
def get_ringImportance(age):
    rnd = random.uniform(-0.05, 0.05) if defaults.RANDOMNESS else 0
    return (.0192308 * age) - .146154 + rnd

# I just made this up, with the pretty reasonable assumption that
# this importance should be the smallest importance, and that
# everyone, regardless of age and ovr, prefer good facilities
# pretty equally.
def get_facilityImportance():
    rnd = random.uniform(-0.05, 0.05) if defaults.RANDOMNESS else 0
    return 0.22 + rnd

# A 3D Gaussian Distribution that is used to figure out the desired year(s) of a player.
# We then convert the Gaussian Distribution into a value between [1, 5], so that's it's actually,
# you know, desired years.
# Sidenote: Tus is a GOAT. Shoutouts to him for all this code.
# Sidenote 2: The constant values were discovered after fitting a Gaussian Distribution to
# sample data, so they are not random.
# If you want more information, read equations.pdf by tus, provided in this repo.
def get_desired_years(age, ovr):
    a = 278603
    b = -8.10721
    mu_age = 25.955128
    mu_ovr = 79.384615
    sigma_age = 1.524766
    sigma_ovr = 4.125377
    
    normalization = 1 / (2 * math.pi * sigma_age * sigma_ovr)
    exponent = -.5 * ((((age - mu_age) / sigma_age) ** 2) + (((ovr - mu_ovr) / sigma_ovr) ** 2))
    years = ((math.log(normalization) + exponent) / b) - math.log(a) / b
    
    if years < 2:
        years = 2
    elif years > 5:
        years = 5

    return years

def calcImportance(age, ovr):
    moneyImportance = get_moneyImportance(age, ovr)
    yearImportance = get_yearImportance(ovr)
    roleImportance = get_roleImportance(age, ovr)
    ringImportance = get_ringImportance(age)
    facilityImportance = get_facilityImportance()
    
    defaults.log_output("Ring Importance: {}".format(ringImportance))
    defaults.log_output("Role Importance: {}".format(roleImportance))
    defaults.log_output("Money Importance: {}".format(moneyImportance))
    defaults.log_output("Year Importance: {}".format(yearImportance))
    defaults.log_output("Facility Importance: {}".format(facilityImportance))

    return (ringImportance, roleImportance, moneyImportance, yearImportance, facilityImportance)

class Player:
    def __init__(self, name, age, ovr, askingAmount, isrfa, birdRights):
        self._name = name
        self._age = age

        # OVR Rating in BBGM
        self._ovr = ovr
        
        # Asking Amount, in Millions
        self._askingAmount = askingAmount
        
        # Whether the player is an RFA or not
        self._isrfa = isrfa

        if birdRights.lower() == "none":
            self._birdRights = None
        else:
            self._birdRights = birdRights

        self._ringImportance, self._roleImportance, self._moneyImportance, self._yearImportance, self._facilityImportance = calcImportance(self._age, self._ovr)
    
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

    @property
    def birdRights(self):
        return self._birdRights
    
    
    def returnInterest(self, teamOffer):
        # Contract Interest calculation is a bit wonky.
        # To accomodate for some of BBGM's fuzzing, we set our own maximum and minimum based off the amount
        # offered by BBGM.
        stddev = self._askingAmount / 4

        if (teamOffer.offerAmount == defaults.MAX_SALARY):
            stddev2 = 0
        else:
            stddev2 = self._askingAmount / 5

        # The high offer is set to the askingAmount + a fifth of the askingAmount. If you offer the high,
        # the contract interest will be equal to a 100.
        # On the other hand, the low offer is set to the askingAmount - a fourth of the askingAmount. If you
        # offer the low, the contract interest will be equal to 0.
        low = self._askingAmount - stddev
        high = self._askingAmount + stddev2

        interestVar = teamOffer.offerAmount - low
        comp = high - low
        
        # Contract Interest is ultimately calculated linearly.
        # Might change this.
        contractInterest = (interestVar / comp) * 100

        # Add Options modifier
        # Team Options subtract 5 interest, Player Options add 5 interest.
        if (teamOffer.option == "TO"):
            contractInterest -= 5
        elif (teamOffer.option == "PO"):
            contractInterest += 5
        
        defaults.log_output("Contract Interest: {}".format(contractInterest))

        if (teamOffer.option == "PO"):
            # If PO is offered, it counts as an year as it is guaranteed on the player's end
            trueOfferYears = teamOffer.offerYears + 1
        else:
            trueOfferYears = teamOffer.offerYears

        if (trueOfferYears == 1):
            yearInterest = 0
        else:
            # Tus is the GOAT and you can't tell me otherwise
            desiredYears = get_desired_years(self._age, self._ovr)
            yearDifference = abs(desiredYears - trueOfferYears)

            # This polynomial fit was created such that:
            # if yearDifference = 0, interest = 100
            # if yearDifference = 1, interest = 80
            # if yearDifference = 2, interest = 50
            # if yearDifference = 3, interest = 10
            # if yearDifference = 4, interest = 0
            yearInterest = max(0, -5 * (yearDifference ** 2) - 15 * yearDifference + 100)

        defaults.log_output("Year Interest: {}".format(yearInterest))

        # Flip Power Ranking such that a better power ranking has a higher number; for example,
        # if you are #1 in PR your powerScore should be 36.
        powerScore = 37 - teamOffer.powerRank

        # Strength Interest is calculated as a function with an exponent a such that 36^a / 3 = 100.
        # This graph grows slightly more exponentially than if 36^a = 100, which makes sense
        # as really any NBA team that is bottom 15 is about equal, and there is a rapid increase
        # as we start to hit contenders.
        strengthInterest = (powerScore ** 1.59167080532) / 3
        
        defaults.log_output("Strength Interest: {}".format(strengthInterest))
        
        # Role Interest is a linear function using the role value of the player. See details about that
        # in the constructor for teamOffer.
        roleInterest = 25 * teamOffer.role
        
        defaults.log_output("Role Interest: {}".format(roleInterest))

        # facilityScore rationale same as powerScore rationale.
        facilityScore = 37 - teamOffer.facility

        # Facility Interest is calculated as a power function where the exponent is such that 36^a = 100. (shoutouts to Desmos)
        facilityInterest = facilityScore ** 1.28509720894

        defaults.log_output("Facility Interest: {}".format(facilityInterest))
        
        # Final interest is a weighted average of the three interests.
        sigma = (contractInterest * self._moneyImportance) + (yearInterest * self._yearImportance) + (strengthInterest * self._ringImportance) + (roleInterest * self._roleImportance) + (facilityInterest * self._facilityImportance)
        interest = int(sigma / (self._ringImportance + self._moneyImportance + self._yearImportance + self._roleImportance + self._facilityImportance))

        if bool(self._isrfa):
            interest *= 1.15

        # Fuzz adds a bit of "fuzz" to the interest so that there are no guarantees, ever.
        fuzz = random.randint(-3, 3) if defaults.RANDOMNESS else 0
        interest += fuzz

        defaults.log_output("Final Interest for {}: {}".format(teamOffer.teamName, interest))
        
        return interest
        
class teamOffer:
    def __init__(self, teamName, offerAmount, powerRank, capSpace, role, exception, offerYears, facility, option=None):
        # Team Name
        self._teamName = teamName

        # The Contract Offered by the Team
        self._offerAmount = offerAmount
        
        # The Power Ranking of the Team (out of 30)
        self._powerRank = powerRank
        
        # Team's Cap Space
        self._capSpace = capSpace
        
        # The Role the Player will have on the team. (0 — Cap Room, 1 — Expendable, 2 — Bench, 3 — Starter, 4 - Star)
        self._role = role

        # The Exception the contract uses to sign the player
        self._exception = exception

        # Offered Contract Years
        self._offerYears = offerYears

        # The Facilities Rank of the Team
        self._facility = facility

        # Whether it is a team, player, or no option
        self._option = option
        
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

    @property
    def exception(self):
        return self._exception
    
    @property
    def offerYears(self):
        return self._offerYears
        
    @property
    def facility(self):
        return self._facility
    
    @property
    def option(self):
        return self._option