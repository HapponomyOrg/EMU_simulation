from emusim.cockpit.abm.base.producer import Producer
from emusim.cockpit.abm.base.regenerative_health_profile import RegenerativeHealthProfile


class RegenerativeProducer(Producer):

    def __init__(self, label: str, health_profile: RegenerativeHealthProfile, input, output, ageing_damage: float = 0):
        super().__init__(label, health_profile, input, output, ageing_damage)