from .abstract_aggregate_simulator import *


class SimpleAggregateSimulator(AbstractAggregateSimulator):

    growth_influence_rate: float = 0.0

    def generate_next(self):
        self.inflation += self.inflation * self.real_growth