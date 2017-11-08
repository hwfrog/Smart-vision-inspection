import threading
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)
X = np.arange(0, 4, 0.2)
Y = np.arange(-1.5, 1.5, 0.2)
X, Y = np.meshgrid(X, Y)
Z = 1.0

ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')

plt.show()