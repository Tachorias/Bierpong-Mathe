import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameter des Bechers
r_becher = 4
h_becher = 12

# Bechermantel (Zylinderfläche)
s = np.linspace(0, h_becher, 10)
t = np.linspace(0, 2 * np.pi, 25)
S, T = np.meshgrid(s, t)




# Achsen einstellen
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')
# ax.set_title('3D Becher (Zylinder)')

# Gleichmäßige Skalierung


x0, y0 = 30, 190
positionen_versatz = [
    (0, 0),
    (-5, 10), (5, 10),
    (-10, 20), (0, 20), (10, 20),
    (-15, 30), (-5, 30), (5, 30), (15, 30)
]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for dx, dy in positionen_versatz:
    becher_x = x0 + dx
    becher_y = y0 + dy
    X = np.cos(T) * r_becher
    Y = np.sin(T) * r_becher
    Z = S
    X = dx + np.cos(T) * r_becher
    Y = dy + np.sin(T) * r_becher
    Z = S
    # Plot setup
    # Bechermantel zeichnen
    ax.plot_surface(X, Y, Z, color='lightblue', alpha=0.7, rstride=1, cstride=1, edgecolor='none')
    ax.set_box_aspect([1, 1, r_becher/h_becher])

plt.show()