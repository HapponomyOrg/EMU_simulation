from copy import deepcopy
from uuid import uuid4, UUID

from emusim.cockpit.abm.base.health_profile import HealthProfile
from emusim.cockpit.abm.base.product_type import ProductType


class Product:
    """Product is the base class for all objects within an economy.

    When a Product needs to be produced, a clone of a 'template' product is made.


    Attributes
    ----------
    id : UUID
        The unique id of the product.
    health_profile : HealthProfile = HealthProfile()
        The health profile for the product. The default is a simple health profile.
    single_use : bool
        When True the Product is a consumable and can only be used once. Otherwise it is reusable.
    ageing_damage : float = 0.0
        The damage one cycle of ageing does to the product. Depending on the health_profile older products
        might age faster due to multiplier effects. If this is set to 0, the product does not age.
    used_up : bool = False
        Determines whether the product is used up. Only for single use products.

    Methods
    -------
    get_id()"""

    id: UUID = uuid4()
    health_profile: HealthProfile = None
    single_use: bool = True
    ageing_damage: float = 0.0
    used_up = False

    def __init__(self,
                 product_type: ProductType,
                 subtype: str,
                 health_profile: HealthProfile = HealthProfile()):
        """Create a new Product.

        Parameters
        ----------
        product_type : ProductType
            The type of the Product. See ProductType.
        subtype : str
            A subtype for the product. Used as a group identifier.
        health_profile : HealthProfile
            The health profile of the product. This determines how it reacts to damage, its longevity, whether or not it
            will regenerate, ..."""

        self.type_id = str(type) + "-" + str(subtype)
        self.subtype = subtype
        self.product_type = product_type
        self.health_profile = health_profile

    def get_id(self) -> UUID:
        return self.id

    def set_single_use(self, single_use: bool):
        self.single_use = single_use

    def is_single_use(self):
        return self.single_use

    def is_used_up(self):
        return self.used_up

    def set_ageing_damage(self, ageing_damage: float):
        self.ageing_damage = ageing_damage

    def get_product_type(self) -> ProductType:
        return self.product_type

    def get_subtype(self) -> str:
        return self.subtype

    def get_type_id(self) -> str:
        """Returns the type id of the Product. This is the id used for all Products of a specific ProductType-subtype
        combination."""
        return self.type_id

    def use(self) -> bool:
        """Use the Product. If it is a single use product it can no longer be used and should be discarded."""
        self.used_up = self.single_use

        return self.used_up

    def is_waste(self):
        """Check whether a product counts as waste. A Product turns into waste if it is expired while it is not used
        up. Only single use products which are used up before they are expired can be discarded without needing
        processing."""
        return self.is_expired() and not self.used_up

    # returns the number of life cycles the product will last under normal ageing conditions
    def get_remaining_cycles(self) -> int:
        return self.health_profile.calculate_cycles(self.ageing_damage)

    def age(self):
        """Age the product. This should be called each cycle. It damages the product due to ageing."""
        self.health_profile.do_damage(self.ageing_damage)

    def is_expired(self) -> bool:
        return self.used_up or self.health_profile.get_health() == 0

    def clone(self):
        """Creates a clone of the Product. This is a deep copy with a new, unique, id."""
        new_clone = deepcopy(self)
        new_clone.id = uuid4()

        return new_clone

