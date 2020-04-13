from emusim.cockpit.abm.product import Product
from emusim.cockpit.abm.product_type import ProductType

class Producer(Product):
    max_production = 1
    over_production_capacity = 0
    damage_per_unit = 0

    # Health profile: determines how much damage the producer can sustain and how damage impacts its capacities.
    def __init__(self, label, product_expiration, health_profile):
        super(Producer, self).__init__(label, ProductType.PRODUCER, product_expiration)

        self.health_profile = health_profile

    # Sets the maximum units that can be produced in one cycle without causing damage
    def set_max_production_units(self, max_production):
        self.max_production = max_production

    # Sets the maximum over production capacity, expressed in extra units
    # Every unit that is produced above normal capacity results in an amount of damage. This damage is cumulative.
    def set_over_production_capacity(self, over_production_capacity, damage_per_unit):
        self.over_production_capacity = over_production_capacity
        self.damage_per_unit = damage_per_unit

    def produce(self, num_units):
        self.health_profile.damage(self.calculate_damage(num_units))

        # produce units and deplete required resources, return produced units

    def calculate_damage(self, production_demand):
        production_demand = self.trim_production(production_demand)

        if production_demand > self.max_production:
            return self.damage_per_unit * (production_demand - self.max_production)
        else:
            return 0

    def trim_production(self, production_demand):
        # check available resources and adjust production demand accordingly
        if production_demand > self.max_production + self.over_production_capacity:
            return self.max_production + self.over_production_capacity
        else:
            return production_demand
