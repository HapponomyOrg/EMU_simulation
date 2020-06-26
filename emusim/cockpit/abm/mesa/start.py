import matplotlib.pyplot as plt  # needed for plotting histogram of wealth
import numpy as np

from emusim.cockpit.abm.mesa.MoneyModel import *



model = MoneyModel(50, 10, 10)
for i in range(20):
    model.step()

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()

gini = model.datacollector.get_model_vars_dataframe()
gini.plot()

plt.show()




