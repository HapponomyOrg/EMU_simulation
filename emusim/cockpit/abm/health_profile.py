class HealthProfile:
    # health expressed in percentages
    MAX_HEALTH = 100

    # thresholds: a list of tuples consisting of a health percentage and damage multiplier.
    #  When the health falls below the percentage indicated, damage is multiplied by the multiplier.
    #  This simulates the fragility of already damaged Producers.
    def __init__(self, thresholds):
        self.thresholds = thresholds

    # Default HealthProfile where all damage is 1 to 1.
    def __init__(self):
        self.__init__({(self.MAX_HEALTH, 1)})