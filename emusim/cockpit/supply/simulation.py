# module simulation

class Simulation:

    def __init__(self):
        self.crash = False
        self.cycles_executed = 0
        self.initial_inflation_rate = 0.019  # initial_inflation_rate
        self.inflation_rate = []  # real inflation rate


    def initialize(self):
        self.inflation_rate.clear()
        self.inflation_rate.append(self.initial_inflation_rate)


    def get_data(self, data, start, stop, do_deflate=False):
        processed_data = []

        for cycle in range(start, stop):
            if do_deflate:
                processed_data.append(round(self.deflate(data[cycle], cycle), 2))
            else:
                processed_data.append(round(data[cycle], 2))

        return processed_data

    def get_percentages(self, data, start, stop):
        percentages = []

        for cycle in range(start, stop):
            percentages.append(round(data[cycle] * 100, 2))

        return percentages


    # only call after initial_inflation_rate has been applied in a cycle
    def deflate(self, num, cycle):
        for i in range(cycle):
            num /= 1 + self.inflation_rate[i]

        return num


    def get_growth(self, raw_data, do_deflate):
        growth = []

        for cycle in range(len(raw_data) - 1):
            if cycle != 0:
                if do_deflate:
                    growth.append(round(self.deflate(raw_data[cycle], cycle)
                                        - self.deflate(raw_data[cycle - 1], cycle - 1), 2))
                else:
                    growth.append(round(raw_data[cycle] - raw_data[cycle - 1], 2))

        return growth