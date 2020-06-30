from typing import Dict

from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.product_type import ProductType


class Enhancer(Product):
    """Enhancers can be installed on producers. Once an enhancer has been initialized its parameters should not be
    changed.

    Attributes
    ----------
    instalation_cycles : int
        The number of cycles it takes to install the enhancer. The enhancer takes effect after it has been
        succesfully installed.
    required_resources_delta : Dict[str, int]
        """

    installation_cycles: int = 0
    required_resources_delta: Dict[str, int] = {}
    maintenance_resources_delta: Dict[str, int] = {}
    maintenance_failure_damage_delta: Dict[str, float] = {}
    production_delta: Dict[Product, int] = {}
    production_delay_delta: int = 0
    production_capacity_delta: int = 0
    over_production_capacity_delta: int = 0
    over_production_damage_delta: float = 0.0
    ageing_damage_delta: float = 0.0
    waste_handling_delta: dict = {}

    def __init__(self,
                 subtype: str):
        super().__init__(ProductType.ENHANCER, subtype)
        self.set_single_use(False)

    def init_installation_cycles(self, installation_cycles):
        self.installation_cycles = installation_cycles

    def get_remaining_installation_cycles(self) -> int:
        return self.installation_cycles

    def is_installed(self) -> bool:
        return self.installation_cycles == 0

    def install_cycle(self):
        if not self.is_installed():
            self.installation_cycles -= 1

    def init_required_resources_delta(self, required_resources_delta: Dict[str, int]):
        self.required_resources_delta += required_resources_delta

    def get_required_resources(self, required_resources) -> Dict[str, int]:
        if self.is_installed():
            # TODO implement
            pass

        return required_resources

    def init_maintenance_resources_delta(self, maintenance_resources_delta: Dict[str, int]):
        self.maintenance_resources_delta += maintenance_resources_delta

    def get_maintenance_resources(self, maintenance_resources: Dict[str, int]) -> Dict[str, int]:
        if self.is_installed():
            pass # TODO implement

        return maintenance_resources

    def init_maintenance_failure_damage_delta(self, maintenance_failure_damage_delta: Dict[str, float]):
        self.maintenance_failure_damage_delta += maintenance_failure_damage_delta

    def init_production_delta(self, alter_production: Dict[Product, int]):
        self.production_delta = alter_production

    def get_production(self, production: Dict[Product, int]) -> Dict[Product, int]:
        if self.is_installed():
            # TODO implement
            pass

        return production

    def init_production_delay_delta(self, production_delay_delta: int):
        self.production_delay_delta = production_delay_delta

    def changes_production_delay(self) -> bool:
        return self.production_delay_delta != 0

    def get_production_delay(self, production_delay: int) -> int:
        if self.is_installed():
            return production_delay + self.production_delay_delta
        else:
            return production_delay

    def init_production_capacity_delta(self, production_capacity_delta: int):
        self.production_capacity_delta = production_capacity_delta

    def get_production_capacity(self, production_capacity: int) -> int:
        if self.is_installed():
            return production_capacity + self.production_capacity_delta
        else:
            return production_capacity

    def init_over_production_capacity_delta(self, over_production_capacity_delta: int):
        self.over_production_capacity_delta = over_production_capacity_delta

    def get_over_production_capacity(self, over_production_capacity: int) -> int:
        if self.is_installed():
            return over_production_capacity + self.over_production_capacity_delta
        else:
            return over_production_capacity

    def init_over_production_damage_delta(self, over_production_damage_delta: float):
        self.over_production_damage_delta = over_production_damage_delta

    def get_over_production_damage(self, over_production_damage: float) -> float:
        if self.is_installed():
            return over_production_damage + self.over_production_damage_delta
        else:
            return over_production_damage

    def init_ageing_damage_delta(self, ageing_damage_delta: float):
        self.ageing_damage_delta = ageing_damage_delta

    def get_ageing_damage(self, ageing_damage: float) -> float:
        if self.is_installed():
            return ageing_damage + self.ageing_damage_delta
        else:
            return ageing_damage

    def init_waste_handling(self, waste_handling: dict):
        self.waste_handling_delta = waste_handling

    def handle_waste(self, waste: dict) -> dict:
        if self.is_installed():
            # TODO implement
            pass

        return waste
