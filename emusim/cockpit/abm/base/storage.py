from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.product_type import ProductType


class Storage(Product):
    """Storage stores a limited amount of Products of specific type(s).

    """

    def __init__(self, subtype: str, types, capacity: int, storage_health_profile, ageing_damage: float = 0):
        super().__init__(ProductType.STORAGE, subtype, storage_health_profile, False, ageing_damage)
        self.health_profile = storage_health_profile
