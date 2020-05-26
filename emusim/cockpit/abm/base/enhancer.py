from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.health_profile import HealthProfile
from emusim.cockpit.abm.base.product_type import ProductType


class Enhancer(Product):
    """Enhancers can be installed on producers."""

    def __init__(self,
                 subtype: str,
                 health_profile: HealthProfile,
                 ageing_damage: float = 0.0,
                 reduce_required_resources: dict = None,
                 augment_batch: dict = None,
                 increase_capacity: int = 0,
                 increase_over_production_capacity: int = 0,
                 decrease_over_production_damage: float = 0.0,
                 cleanup_waste: dict = None,
                 waste_output: dict = None,
                 decrease_ageing_damage: float = 0.0):
        super().__init__(ProductType.ENHANCER, subtype, health_profile, False, ageing_damage)

        self.reduce_required_resources = reduce_required_resources
        self.augment_batch = augment_batch
        self.increase_capacity = increase_capacity
        self.increase_over_production_capacity = increase_over_production_capacity
        self.decrease_over_production_damage = decrease_over_production_damage
        self.cleanup_waste = cleanup_waste
        self.waste_output = waste_output
        self.decrease_ageing_damage = decrease_ageing_damage

    def get_required_resources(self, required_resources):
        # TODO implement
        pass