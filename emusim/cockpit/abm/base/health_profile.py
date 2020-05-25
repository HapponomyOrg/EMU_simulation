class HealthProfile:
    # Maximum possible health. Expressed in percentages.
    MAX_HEALTH = 100

    # Constant for an infinite amount of cycles.
    INFINITE_CYCLES = -1

    max_health = MAX_HEALTH # in some circumstances, due to ageing or sustained damage, it might be possible that
                            # the maximum health to which a Producer can get is reduced.
    health = MAX_HEALTH
    restorable = False


    # damage_thresholds: a list of tuples consisting of a health percentage and damage multiplier.
    # health_thersholds: a list of tuples consisting of a health threshold and the maximum health
    #                    of the producer once health falls below the threshold.
    #  When the health falls below the percentage indicated, damage is multiplied by the multiplier.
    #  This simulates the fragility of already damaged Producers.
    #
    # By default, restorable is set to False
    def __init__(self, damage_thresholds, health_thresholds):
        self.damage_thresholds = damage_thresholds
        self.health_thersholds = health_thresholds

    # Default HealthProfile where all damage is 1 to 1 and max_health is always MAX_HEALTH.
    def __init__(self):
        self.__init__({(self.MAX_HEALTH, 1)}, {(self.MAX_HEALTH, self.MAX_HEALTH)})

    def set_health(self, health):
        self.health = health

    def get_health(self):
        return self.health

    # Calculates the remaining cycles if each cycle causes a specific amount of damage.
    # damage: the damage done per cycle.
    def calculate_cycles(self, damage):
        if damage == 0 and self.get_health() > 0:
            return self.INFINITE_CYCLES
        else:
            # TODO: implement
            return self.INFINITE_CYCLES

    # Inflict damage
    # damage: the amount of damage to inflict
    # Returns the new health percentage.
    # The actual damage which is inflicted can differ depending on the damage_thersholds
    def do_damage(self, damage):
        self.set_health(max(0, self.get_health() - self.get_value_for_health(self.damage_thresholds, False) * damage))
        self.max_health = self.get_value_for_health(self.health_thersholds, True)

        return self.get_health()

    # Set the restorability. A restorable health profile can recover from damage.
    # restorable: True or False
    # restore_thresholds: a list of tuples with a health percentage and a restoration multiplier.
    # Heavily damaged Producers might either be unrestorable (when the multiplier is set to 0) or
    # require more effort to be repaired (when the multiplier is set < 1) while others are more easily
    # repaired (multiplier > 1), depending in the amoount of damage they have already suffered.
    def set_restorable(self, restorable, restore_thresholds):
        self.restorable = restorable
        self.restore_thresholds = restore_thresholds

    # Restore an amount of damage.
    # restore_effort: the percentage of damage that is attempted to be restored.
    # Returns the new health percentage. This can be lower than expected, depending in the restoration_thresholds.
    def restore_health(self, restore_effort):
        if self.restorable:
            self.set_health(min(self.MAX_HEALTH, self.health + self.get_value_for_health(self.restore_thresholds, True)))

        return self.get_health()

    # thresholds: the list of thresholds.
    # maximize: True for retrieving the highest matching value, False for retrieving the lowest matching value.
    def get_value_for_health(self, thresholds, maximise):
        if maximise:
            value = 0
        else:
            value = float('inf')

        for threshold in self.thresholds:
            if self.get_health() <= threshold[0]:
                if maximise:
                    value = max(value, threshold[1])
                else:
                    value = min(value, threshold[1])

        return value
