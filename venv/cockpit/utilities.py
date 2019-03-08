# module utilities

import pygal

def create_chart(title):
    chart = pygal.Line(show_dots=True)
    chart.title = title
    return chart


def get_data(data, do_deflate=False, inflation=0.0):
    processed_data = []
    cycle = 0

    for data_point in data:
        if cycle != 0:  # remove setup step
            if do_deflate:
                processed_data.append(round(deflate(inflation, data_point, cycle), 2))
            else:
                processed_data.append(round(data_point, 2))

        cycle += 1

    return processed_data


# only call after inflation has been applied in a cycle
def deflate(inflation, num, cycle):
    for i in range(cycle):
        num /= 1 + inflation

    return num


def get_growth(raw_data, do_deflate, inflation):
    growth = []

    for cycle in range(len(raw_data)):
        if cycle != 0:
            if do_deflate:
                growth.append(round(deflate(inflation, raw_data[cycle], cycle)
                                    - deflate(inflation, raw_data[cycle - 1], cycle - 1), 2))
            else:
                growth.append(round(raw_data[cycle] - raw_data[cycle - 1], 2))

    return growth