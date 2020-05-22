from emusim.cockpit.abm.producer import Producer


class RegenerativeProducer(Producer):

    # health_profile is of class RegenerativeHealthProfile
    def __init__(self, label, max_lifespan, health_profile):
        super().__init__(label, max_lifespan, health_profile)