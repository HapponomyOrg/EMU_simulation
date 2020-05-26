from emusim.cockpit.abm.base.producer import Producer
from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.health_profile import HealthProfile

# Finite producers represent finite resource deposits such as mines.
class FiniteProducer(Producer):

    # subtype: a subtype for the producer. Can serve as an identifier of sorts.
    # total_capacity: the total production capacity of the producer over its full lifetime. Must be > 0.
    # health_profile: determines how much damage the producer can sustain and how damage impacts its capacities.
    def __init__(self, subtype, total_capacity: int, health_profile: HealthProfile):
        if total_capacity == Product.NO_EXPIRY:
            total_capacity = 0

        super().__init__(subtype, total_capacity, health_profile)