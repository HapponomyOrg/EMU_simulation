# module utilities

import pygal

def create_chart(title):
    chart = pygal.Line(show_dots=True)
    chart.title = title
    return chart