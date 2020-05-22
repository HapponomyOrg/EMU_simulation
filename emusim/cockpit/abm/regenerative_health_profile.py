from emusim.cockpit.abm.health_profile import HealthProfile


class RegenerativeHealthProfile(HealthProfile):

    # health_thresholds: see HealthProfile
    # regeneration_thesholds: a list of tuples with a health percentage and a regeneration percentage.
    # When health >= health percentage, an amount, equal to the regeneration percentage, is recovered
    # when no production is executed during one cycle.
    # This simulates slow recovery of heavily damaged Producers.
    def __init__(self, health_thresholds, regeneration_thresholds):
        super.__init__(health_thresholds)

        self.regeneration_thresholds = regeneration_thresholds

    # Default RegenerativeHealthProfile where each cycle of non production regenerates 10% damage.
    def __init__(self):
        super(RegenerativeHealthProfile, self).__init__()

        self.regeneration_thresholds = {(0, 10)}

    def regenerate(self):
        self.set_health(min(self.MAX_HEALTH, self.get_health() + self.get_value_for_health(self.regeneration_thresholds)))