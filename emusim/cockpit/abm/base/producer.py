from emusim.cockpit.abm.base.product import Product
from emusim.cockpit.abm.base.product_type import ProductType
from emusim.cockpit.abm.base.health_profile import HealthProfile

from collections import deque

# Producers order products, which can also be producers, in batches. A batch is the smallest output which can be
# produced.
class Producer(Product):
    UNLIMITED = -1

    max_production: int = 1
    over_production_capacity: int = 0
    damage_per_over_production_batch: float = 0
    production_delay: int = 0
    orders: int = 0
    back_orders: int = 0 # The orders that can not be satisfied at the time of production due to a lack of resources.
                         # These will be produced as soon as resources and production capacity becomes available.
    max_back_orders = UNLIMITED # If back_orders exceeds max_back_orders, over production will be engaged in order to
                                # eliminate back orders as soon as possible.
    production_queue: deque = deque(production_delay + 1)

    enhancers = {} # The installed enhancers. TODO

    # label: a label for the producer. Can serve as an identifier of sorts.
    # producer_lifetime: the amount of cycles the producer lasts. Can be set to Product.NO_EXPIRY.
    # health_profile: determines how much damage the producer can sustain and how damage impacts its capacities.
    # input: a dictionary of product type id's and amount values. It represents the input for one production batch.
    # output_batch:
    # ageing_damage: the damage one cycle of ageing does to the producer. Depending on the health_profile older
    #                producers might age faster due to multiplier effects. If this is set to 0, the producer does not
    #                age.
    def __init__(self, label: str, health_profile: HealthProfile, input, output_batch, ageing_damage: float = 0):
        super().__init__(label, ProductType.PRODUCER, health_profile, ageing_damage)

    # Set the production delay. This can only be done when there are no outstanding orders.
    # production_delay: the number of cycles it takes before a batch is actually produced.
    # Returns True when production_delay is succesfully set to the new value, False otherwise.
    def set_production_delay(self, production_delay: int):
        if self.get_orders_in_pipeline() == 0:
            self.production_delay = production_delay
            self.production_queue = deque(self.production_delay + 1)
            return True
        else:
            return False

    # Sets the maximum batches that can be produced in one cycle without causing damage.
    def set_max_production(self, max_production):
        self.max_production = max_production

    # Sets the maximum over production capacity, expressed in extra batches
    # Every batch that is produced above normal capacity results in an amount of damage. This damage is cumulative.
    def set_over_production_capacity(self, over_production_capacity, damage_per_batch):
        self.over_production_capacity = over_production_capacity
        self.damage_per_over_production_batch = damage_per_batch

    # Returns production capacity without over production.
    def get_production_capacity(self):
        return self.max_production

    # Returns production capacity with over production.
    def get_max_production_capacity(self):
        return self.get_production_capacity() + self.over_production_capacity

    # Returns the capacity still available for orders. This is production capacity without taking over production
    # into account.
    def get_available_order_capacity(self):
        return self.max_production - self.orders

    # Returns the available order capacity, including over production capacity.
    def get_max_available_order_capacity(self):
        return self.get_available_order_capacity() + self.over_production_capacity

    # Add an order for this cycle. Production takes production_delay cycles.
    # num_batches: the number of batches to add to the order.
    # Returns the number of batches which are actually added. This could be less than requested if the total number of
    # orders would exceed max production capacity + over production capacity or if not enough resources are available in
    # order to meet demand.
    def order(self, num_batches):
        self.orders += num_batches

    # Returns the orders that have been placed this cycle.
    def get_current_orders(self):
        return self.orders

    # Returns the sum of all orders in the production queue.
    def get_orders_in_pipeline(self):
        orders_in_pipeline = 0

        for order_size in self.production_queue:
            orders_in_pipeline += order_size

        return orders_in_pipeline

    # Produces the order that reached the end of the production queue.
    # resources: the resources available for production. If not enough resources are available to fulfill the order,
    #            the number of unfulfilled batches is added to the number of back orders.
    # Returns the produced products.
    def produce(self, resources):
        production_size = 0

        # Actual output is only generated when the production queue has been filled up with orders. These can be
        # orders of 0 batches, which will result in no production.
        if len(self.production_queue) == self.production_delay:
            production_size += self.production_queue.pop()

        # Produce extra batches if there are back orders and there is production capacity available
        capacity = 0

        if self.max_back_orders != self.UNLIMITED and self.back_orders > self.max_production:
            capacity = self.get_production_capacity()
        else:
            capacity = self.get_max_production_capacity()

        if self.back_orders > 0 and production_size < capacity:
            extra_production = min(capacity - production_size, self.back_orders)
            self.back_orders -= extra_production
            production_size += extra_production

        self.health_profile.do_damage(self.calculate_damage(production_size))
        # TODO: produce units and deplete required resources. Put products in pipeline (taking delay into account)

        # The new orders are added to the production queue and the orders are reset to 0.
        self.production_queue.append(self.orders)
        self.orders = 0

    def calculate_damage(self, production_demand):
        production_demand = self.trim_order(production_demand)

        if production_demand > self.max_production:
            return self.damage_per_over_production_batch * (production_demand - self.max_production)
        else:
            return 0

    # Trim the order to a number of batches that can actually be produced.
    # num_batches: the number of batches ordered.
    # Returns the actual number of batches that will be produced.
    def trim_order(self, num_batches):
        if num_batches + self.orders > self.max_production + self.over_production_capacity:
            return self.max_production + self.over_production_capacity - self.orders
        else:
            return num_batches
