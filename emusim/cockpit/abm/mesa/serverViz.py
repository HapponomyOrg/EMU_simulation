from emusim.cockpit.abm.mesa.MoneyModel import *

from mesa.visualization.ModularVisualization import ModularServer #webserver
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule #chart module for webserver

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = ChartModule([{"Label": "Gini",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

server = ModularServer(MoneyModel,
                       [grid, chart],
                       "Money Model",
                       {"N":50, "width":10, "height":10})

server.port = 8521 # The default
server.launch()