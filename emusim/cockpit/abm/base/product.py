from emusim.cockpit.abm.base.health_profile import HealthProfile
from emusim.cockpit.abm.base.product_type import ProductType
from uuid import uuid4, UUID
from copy import deepcopy


class Product:
    """Product is the base class for all objects within an economy.

    When a Product needs to be produced, a clone of a 'template' product is made.

    Attributes
    ----------

    Methods
    -------
    get_id()"""

    def __init__(self, product_type: ProductType, subtype: str, health_profile: HealthProfile, single_use: bool = True,
                 ageing_damage: float = 0):
        """Create a new Product.

        Parameters
        ----------
        product_type : ProductType
            The type of the Product. See ProductType.
        subtype : str
            A subtype for the product. Used as a group identifier.
        health_profile : HealthProfile
        single_use : bool
            When True the Product is a consumable and can only be used once. Otherwise it is reusable.
        ageing_damage : float = 0
            the damage one cycle of ageing does to the product. Depending on the health_profile older products
            might age faster due to multiplier effects. If this is set to 0, the product does not age."""

        self.id = uuid4()
        self.type_id = str(type) + "-" + str(subtype)
        self.subtype = subtype
        self.product_type = product_type
        self.health_profile = health_profile
        self.ageing_damage = ageing_damage
        self.single_use = single_use
        self.used_up = False

    def get_id(self) -> UUID:
        return self.id

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

    # Age the product. This is called each cycle damages the product due to ageing.
    def age(self):
        self.health_profile.do_damage(self.ageing_damage)

    def is_expired(self) -> bool:
        return self.used_up or self.health_profile.get_health() == 0

    def clone(self):
        """Creates a clone of the Product. This is a deep copy with a new, unique, id."""
        new_clone = deepcopy(self)
        new_clone.id = uuid4()

        return new_clone

