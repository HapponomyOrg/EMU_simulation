from emusim.cockpit.abm.producer import Producer
from emusim.cockpit.abm.product import Product

# Finite producers represent finite resource deposits such as mines.
class FiniteProducer(Producer):

    # label: a label for the producer. Can serve as an identifier of sorts.
    # total_capacity: the total production capacity of the producer over its full lifetime..
    # health_profile: determines how much damage the producer can sustain and how damage impacts its capacities.
    def __init__(self, label, total_capacity, health_profile):
        if total_capacity == Product.NO_EXPIRY:
            total_capacity = 0

        super().__init__(label, total_capacity, health_profile)