from emusim.cockpit.abm.base.health_profile import HealthProfile


class MechanicHealthProfile(HealthProfile):

    def __init__(self, damage_thresholds, restore_thresholds):
        super.__init__(damage_thresholds)
        self.set_restorable(True, restore_thresholds)