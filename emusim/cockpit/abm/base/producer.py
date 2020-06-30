from collections import deque
from typing import Dict, Deque, List, Tuple

from emusim.cockpit.abm.base.enhancer import Enhancer
from emusim.cockpit.abm.base.health_profile import HealthProfile
from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.product_type import ProductType


class Order():
    """For placing order_cluster with Producers.

    Attributes
    ----------
    priority : str
        The priority for the order. Higher priority order_cluster are handled first. High priority order_cluster result in
        overproduction when necessary. Low priority order_cluster are pushed to the backorder queue if needed in order to
        satisfy higher priority order_cluster.
    requested_batches : int
        The number of batches requested from the Producer.
    partial_acceptance:
        Determines whether the order can be partially accepted. If False, the order is either accepted in full or is
        not accepted at all. If True then the number of batches acepted for production can be lower than the number
        of requested batches.
    accepted_batches : int
        The number of batches accepted by the Producer. This can be less than the number of requested batches due to
        limits in production capacity of the Producer.
    produced_batches : int
        The number of batches which have already been produced.
    delayed : bool
        Set to True when production of an order has been delayed."""

    # Priorities for order_cluster.
    PRIORITY_LOW = "LOW"
    PRIORITY_NORMAL = "NORMAL"
    PRIORITY_HIGH = "HIGH"

    accepted_batches: int = 0
    produced_batches: int = 0
    delayed: bool = False

    def __init__(self, requested_batches: int, partial_acceptance: bool = False, priority: str = PRIORITY_NORMAL):
        self.requested_batches = requested_batches
        self.partial_acceptance = partial_acceptance
        self.priority = priority

    def get_priority(self) -> str:
        return self.priority

    def get_requested_batches(self) -> int:
        return self.requested_batches

    def get_partial_acceptance(self) -> bool:
        return self.partial_acceptance

    def set_accepted_batches(self, accepted_batches : int):
        self.accepted_batches = min(self.requested_batches, accepted_batches)

    def get_accepted_batches(self) -> int:
        return self.accepted_batches

    def batch_produced(self):
        self.produced_batches += 1

    def order_finished(self) -> bool:
        return self.produced_batches == self.accepted_batches

    def set_daleyed(self, delayed : bool):
        self.delayed = delayed

    def get_delayed(self) -> bool:
        return self.delayed


class Producer(Product):
    """A Producer produces Product instances. These can also be Producer instances.

    Production is done in batches. A batch can contain multiple items and it can contain a range of different Product
    types. Production of a batch can require required_resources resources. It is not possible to produce fractions of a batch.


    Attributes
    ----------
    UNLIMITED : int
        A constant which can be used to set the maximum number of back order_cluster to unlimited. This is the default.
    required_resources : Dict[str, int]
        A dictionary containing the type and number of resources required to produce 1 batch.
    production_capacity : int
        The amount of batches the Producer can produce under normal circumstances.
    over_production_capacity : int
        The maximum amount of supplementary batches which can be produced. Overproduction can potentially damage the
        Producer.
    over_production_damage : float
        The amount of damage per overproduced batch. This can be altered depending on the health profile.
    production_delay : int
        The amount of time it takes to produce products.
    current_orders : Dict[str, Deque[Order]]
        The accepted or partially accepted order_cluster for the current cycle. Orders are grouped by priority.
    back_orders : Dict[str, Deque[Order]]
        The orders that can not be satisfied at the time of production due to a lack of resources. These will be
        produced as soon as resources and production capacity becomes available. High priority orders get precedence
        over lower priority orders which are scheduled for production.
    max_back_orders : int
        If the number of batches in back_orders exceeds max_back_orders, over production will be engaged in order to
        eliminate back orders as soon as possible.
    production_queue : Deque[Dict[str, Deque[Order]]]
        The production queue containing the order clusters to be produced. Each cycle an order cluster is popped for
        production and the current order cluster is added. Production is executed from high priority ro low priority.
    production_batch : Dict[Product, int]
        A dictionary with 'template' Products and amounts. During production the 'template' Products are cloned.
    maintenance_resources : Dict[str, int]
        A dict containing the types and number of resources that are needed for maintenance. Failure to do proper
        maintenance results in damage to the producer.
    maintenance_failure_damage : Dict[str, float]
        A dict containing the damage percentages which occur when 1 unit of necessary maintenance resources can not
        be consumed for maintenance. Damage percentages are per type per unit. The state of the health profile might
        increase the listed damage.
    repair_profile : Dict[str, Tuple[float, float]]
        If a product has a repair profile, damage can be repaired by expending resources. The repair profile consists of
        a dict which contains product types as identifiers and a tuple which indicates the amount of damage which is
        repaired for each unit of that resource and the maximum amount which can be repaired in one cycle with that
        particular resource.
    max_batches : int
        The maximum amount of batches a Producer can produce over its lifetime. The default is UNLIMITED. A limit can be
         set to simulate mines for example.
    enhancers : List[Enhancer]
        A Producer can be enhanced by one or more Enhancer instances. Enhancers take effect once they are installed.
    """

    UNLIMITED: int = int('inf')

    required_resources: Dict[str, int] = {}
    production_capacity: int = 1
    over_production_capacity: int = 0
    over_production_damage: float = 0
    production_delay: int = 0
    current_orders: Dict[str, Deque[Order]] = {Order.PRIORITY_LOW: deque(),
                                               Order.PRIORITY_NORMAL: deque(),
                                               Order.PRIORITY_HIGH: deque()}
    back_orders: Dict[str, Deque[Order]] =  {Order.PRIORITY_LOW: deque(),
                                             Order.PRIORITY_NORMAL: deque(),
                                             Order.PRIORITY_HIGH: deque()}
    max_back_orders = UNLIMITED
    production_queue: Deque[Dict[str, Deque[Order]]] = deque()

    production_batch: Dict[Product, int] = {}
    maintenance_resources: Dict[str, int] = {}
    maintenance_failure_damage: Dict[str, float] = {}

    repair_profile: Dict[str, Tuple[float, float]] = {}

    max_batches: int = UNLIMITED

    enhancers: Deque[Enhancer] = []

    def __init__(self, subtype: str, required_resources: Dict[str, int], production_batch: Dict[Product, int],
                 maintenance_resources: Dict[str, int] = None, maintenance_failure_damage: Dict[str, float] = None,
                 health_profile: HealthProfile = HealthProfile()):
        """Create a new Producer.


        Parameters
        ----------
            subtype : str
                A label for the producer. Can serve as an identifier of sorts.
            required_resources : Dict[str, int]
            production_batch : Dict[Product, int]
                A dictionary with 'template' Products and amounts. During production the 'template' Products are cloned.
            maintenance_resources : Dict[str, int]
            maintenance_failure_damage : Dict[str, float]
            health_profile : HealthProfile
                Determines how much damage the producer can sustain and how damage impacts its capacities.
        """

        super().__init__(ProductType.PRODUCER, subtype)

        self.set_single_use(False)
        self.required_resources += required_resources
        self.production_batch += production_batch
        self.health_profile = health_profile
        self.maintenance_resources += maintenance_resources
        self.maintenance_failure_damage += maintenance_failure_damage

    def init_production_delay(self, production_delay: int):
        self.production_delay = production_delay

    def get_production_delay(self) -> int:
        return self.production_delay

    # Sets the maximum batches that can be produced in one cycle without causing damage.
    def init_production_capacity(self, production_capacity):
        self.production_capacity = production_capacity

    # Returns production capacity without over production.
    def get_production_capacity(self) -> int:
        return self.production_capacity

    # Sets the maximum over production capacity, expressed in extra batches
    # Every batch that is produced above normal capacity results in an amount of damage. This damage is cumulative.
    def init_over_production_capacity(self, over_production_capacity: int, over_production_damage: float = 0.0):
        self.over_production_capacity = over_production_capacity
        self.over_production_damage = over_production_damage

    def get_over_production_capacity(self):
        return self.over_production_capacity

    def get_over_production_damage(self) -> float:
        return self.over_production_damage

    def do_maintenance(self, maintenance_resources: Dict[str, Deque[Product]]):
        pass # TODO implement

    def do_repair(self, repair_resources: Dict[str, Deque[Product]]):
        pass # TODO implement

    def get_required_resources(self) -> Dict[str, int]:
        required_resources = self.required_resources.copy()

        for enhancer in self.enhancers:
            required_resources = enhancer.get_required_resources(required_resources)

        return required_resources

    # Returns production capacity with over production.
    def get_max_production_capacity(self) -> int:
        return self.get_production_capacity() + self.get_over_production_capacity()

    def get_spare_capacity(self) -> int:
        """Returns the capacity still available for current orders. This is production capacity without taking over
        production into account."""
        return self.get_production_capacity() - self.get_batches_in_order_cluster(self.current_orders)

    def get_max_spare_capacity(self) -> int:
        """Returns the available order capacity, including over production capacity."""
        return self.get_max_production_capacity() - self.get_batches_in_order_cluster(self.current_orders)

    def order(self, order: Order) -> bool:
        """Attempt to place an order. Orders are only accepted if enough production capacity is available. High
        priority orders might delay low priority orders. High priority orders will engage over production if needed.

        Parameters
        ----------
        order: Order
            The order to be placed. """

        available_capacity = 0

        if order.get_priority() != Order.PRIORITY_HIGH:
            available_capacity = self.get_spare_capacity()
        else:
            # Low priority order_cluster might be delayed at time of production.
            available_capacity = self.get_max_spare_capacity()\
                                 + self.get_batches_in_orders(self.current_orders[Order.PRIORITY_LOW])

        if available_capacity > 0:
            if available_capacity >= order.get_requested_batches() or order.get_partial_acceptance():
                order.set_accepted_batches(min(order.get_requested_batches(), available_capacity))
                self.current_orders[order.get_priority()].append(order)
                return True

        return False

    def get_batches_in_production_queue(self) -> int:
        """Returns the sum of all accepted batches of all orders in the production queue."""
        batches_in_queue = 0

        for order_cluster in self.production_queue:
            batches_in_queue += self.get_batches_in_order_cluster(order_cluster)

        return batches_in_queue

    def get_batches_in_order_cluster(self, order_cluster: Dict[str, Deque[Order]]) -> int:
        batches_in_order_cluster = 0

        for orders in order_cluster.values():
            batches_in_order_cluster += self.get_batches_in_orders(orders)

        return batches_in_order_cluster

    def get_batches_in_orders(self, orders: Deque[Order]):
        batches_in_orders = 0

        for order in orders:
            batches_in_orders += order.get_accepted_batches()

        return batches_in_orders

    def idle(self):
        """Do nothing during a cycle."""
        self.health_profile.regenerate(True)

        #for enhancer in self.enhancers: TODO
        #    enhancer.idle()

    def produce(self, resources: Dict[str, int]):
        """Produces the order that reached the end of the production queue (after production_delay cycles).

        Parameters
        ----------
        resources: dict
            A dictionary of resources to be used for production. Keys are type_id's, values are lists of the
            resource. Resources are used after production. Usage of a resource does not necessarily destroy the
            resource. That depends on whether it is single use or not.

        Returns
        -------
        dict
            A dictionary with products where the keys are product_type_id's"""

        # TODO implement

        self.health_profile.regenerate(False)

    def calculate_damage(self, production_demand):
        if production_demand > self.get_production_capacity():
            return self.get_over_production_damage() * (production_demand - self.get_production_capacity())
        else:
            return 0

    # Trim the order to a number of batches that can actually be produced.
    # requested_batches: the number of batches ordered.
    # Returns the actual number of batches that will be produced.
    def trim_order(self, num_batches, priority: bool): # TODO review
        #if not priority:
        #    num_batches = min(num_batches, self.get_max_production_capacity() - self.orders)
        #else:
        #    num_batches = min(num_batches, self.get_production_capacity() - self.orders)

        return num_batches

    def repair(self, repair_resources: Dict[str, List[Product]]):
        pass # TODO implement