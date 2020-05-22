from emusim.cockpit.abm.product import Product
from emusim.cockpit.abm.product_type import ProductType


# A store can store other products.
class Storage(Product):

    def __init__(self, label, product_expiration, types, capacity, storage_health_profile):
        super().__init__(label, ProductType.STORAGE, product_expiration)
        self.health_profile = storage_health_profile
