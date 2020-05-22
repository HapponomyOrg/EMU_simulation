from emusim.cockpit.abm.regenerative_producer import RegenerativeProducer
from emusim.cockpit.abm.regenerative_health_profile import RegenerativeHealthProfile


class Person(RegenerativeProducer):

    def __init__(self, name):
        super().__init__(name, self.determine_max_age(), self.determine_health_profile())

    def determine_max_age(self):
        return 85

    def determine_health_profile(self):
        return RegenerativeHealthProfile()
