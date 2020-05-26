from emusim.cockpit.abm.base.producer import Producer
from emusim.cockpit.abm.base.regenerative_health_profile import RegenerativeHealthProfile


class RegenerativeProducer(Producer):

    def __init__(self, subtype: str, health_profile: RegenerativeHealthProfile, input, output, ageing_damage: float = 0):
        super().__init__(subtype, health_profile, input, output, ageing_damage)