from typing import List, Tuple


class HealthProfile:
    """A health profile determines how a product reacts to damage, its longevity, whether or not it will regenerate, ...


    Attributes
    ----------
    MAX_HEALTH : float = 100.0
        A constant indicating the maximum health percentage, being 100%, a product can have.
    INFINITE_CYCLES: int
        A constant used to indicate an infinite amount of cycles.
    max_health : float
        When too much damage has occured it is possible that the maximum health possible is reduced. This attribute
        stores that value. It can never ne increased.
    health : float
        The current health of the product.
    damage_thresholds : List[Tuple[float, float]]
        A list of thresholds indicating the real amount of damage 1 point of damage does to the Product.
        Example:
        [(MAX_HEALTH, 0.5), (75.0, 1), (50.0, 2)]
        As long as health is above 75%, 1 point of damage only lowers the health of the product by 0.5%. As soon as the
        health drops to 75% but remains above 50%, 1 point of damage results in 1% of health decrease. Once health
        frops to 50% or below, 1 point of damage incurs a 2% drop in health.
    health_thresholds : List[Tuple[float, float)]
        A list of thresholds indicating the maximum health a product can recover to if too much damage occurs.
        Example:
        [(MAX_HEALTH, MAX_HEALTH), (50.0, 75.0)]
        If health of the product drops to 50% or lower, it can never be restored above 75% again. This will be reflected
        in the max_health attribute.
    regeneration_thresholds : List[Tuple[float, float]]
        A product can be configured to be regenerating. If a product is regenerative it recovers some health during
        each cycle. It can never recover more health than its max_health though.
    active_regeneration : float = 0.0
        Regenerative products possibly regenerate differently when being used. This is indicated by a multiplier.
    """

    MAX_HEALTH: float = 100.0
    INFINITE_CYCLES: int = int('inf')

    max_health = MAX_HEALTH
    health = MAX_HEALTH

    damage_thresholds: List[Tuple[float, float]] = [(MAX_HEALTH, 1)]
    health_thresholds: List[Tuple[float, float]] = [(MAX_HEALTH, MAX_HEALTH)]

    regeneration_thresholds: List[Tuple[float, float]] = [(MAX_HEALTH, 0.0)]
    active_regeneration: float = 0.0

    def set_health(self, health):
        self.health = health

    def get_health(self):
        return self.health

    def set_damage_thresholds(self, damage_thresholds: List[Tuple[float, float]]):
        """Sets the damage thresholds.

        Parameters
        ----------
        damage_thresholds : list
            A list of tuples consisting of health percentage thresholds and damage multipliers."""
        self.damage_thresholds = damage_thresholds.copy()

    def set_health_thresholds(self, health_thresholds: List[Tuple[float, float]]):
        """Sets the health thresholds.

        Parameters
        ----------
        health_thresholds : list
            A list of tuples consisting of health percentage thresholds and the corresponding max health once health
            falls below the threshold."""
        self.health_thresholds = health_thresholds.copy()

    def set_regeneration(self, regeneration_thresholds: List[Tuple[float, float]], active_regeneration: float = 0.0):
        self.regeneration_thresholds = regeneration_thresholds.copy()
        self.active_regeneration = active_regeneration

    def regenerate(self, idling: bool):
        pass # TODO implement

    def repair(self, damage: float):
        """Repairs an mount of damage. Damage can never be repaired above max_health."""
        pass # TODO implement

    # Calculates the remaining cycles if each cycle causes a specific amount of damage.
    # damage: the damage done per cycle.
    def calculate_cycles(self, damage) -> int:
        pass # TODO: implement

    # Inflict damage
    # damage: the amount of damage to inflict
    # Returns the new health percentage.
    # The actual damage which is inflicted can differ depending on the damage_thersholds
    def do_damage(self, damage):
        self.set_health(max(0, self.get_health() - self.get_value_for_health(self.damage_thresholds, False) * damage))
        self.max_health = self.get_value_for_health(self.health_thresholds, True)

        return self.get_health()

    # thresholds: the list of thresholds.
    # maximize: True for retrieving the highest matching value, False for retrieving the lowest matching value.
    def get_value_for_health(self, thresholds, maximise):
        if maximise:
            value = 0
        else:
            value = float('inf')

        for threshold in thresholds:
            if self.get_health() <= threshold[0]:
                if maximise:
                    value = max(value, threshold[1])
                else:
                    value = min(value, threshold[1])

        return value
