from emusim.cockpit.abm.base.health_profile import HealthProfile
from emusim.cockpit.abm.base.product_type import ProductType
from uuid import uuid4

class Product:
    # type_id: the unique id for the collection of instances of a specific type of product.
    # id: the unique id of the product.
    # label: a label for the product. For display and type identification purposes.
    # type: the type of the Product. See ProductType.
    # health_profile: # health_profile of the product.
    # ageing_damage: the damage one cycle of ageing does to the product. Depending on the health_profile older products
    #                might age faster due to multiplier effects. If this is set to 0, the product does not age.
    def __init__(self, label: str, type: ProductType, health_profile: HealthProfile, ageing_damage: float = 0):
        self.type_id = str(type) + "-" + str(label)
        self.id = uuid4()
        self.label = label
        self.type = type
        self.health_profile = health_profile
        self.ageing_damage = ageing_damage

    def get_label(self):
        return self.label

    def get_type(self):
        return self.type

    # returns the number of life cycles the product will last under normal ageing conditions
    def get_remaining_cycles(self):
        return self.health_profile.calculate_cycles(self.ageing_damage)

    # Age the product. This is called each cycle damages the product due to ageing.
    def age(self):
        self.health_profile.do_damage(self.ageing_damage)

    def is_expired(self):
        return self.health_profile.get_health() == 0
