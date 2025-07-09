import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Parameter
r_becher = 4      # Becherradius
h_becher = 12     # Becherhöhe
r_kugel = 2       # Kugelradius
x0, y0, z0 = 0, 0, 0  # Becherposition

# Beispielposition: Kugel knapp über dem Rand
x, y, z = 3.9, 0, h_becher + 1.9  # leicht oberhalb, soll gerade berühren

# Lokale Kugelposition relativ zum Bechermittelpunkt
local_sphere = np.array([x - x0, y - y0, z - z0])
l_x, l_y, l_z = local_sphere

# Abstand zur oberen Becherkante
vertical_dist = l_z - h_becher

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_title("Becherkanten-Kollisionstest")

# Zylinder-Becherrand (Kreis oben)
t = np.linspace(0, 2 * np.pi, 100)
circle_x = r_becher * np.cos(t)
circle_y = r_becher * np.sin(t)
circle_z = np.ones_like(t) * h_becher
ax.plot(circle_x, circle_y, circle_z, color='red', label='Becherrand')

# Prüfe Kollision
if 0 < vertical_dist <= r_kugel:
    vectorS = local_sphere - np.array([0, 0, h_becher])
    cylinder_axis = np.array([0, 0, 1])

    # Richtung auf der Deckfläche
    normal_unnormalized = np.cross(np.cross(vectorS, cylinder_axis), cylinder_axis)
    norm_len = np.linalg.norm(normal_unnormalized)

    if norm_len != 0:
        direction = normal_unnormalized / norm_len
        p_kante_local = np.array([0, 0, h_becher]) + direction * r_becher
        p_kante_global = np.array([x0, y0, z0]) + p_kante_local

        abstand = np.linalg.norm(np.array([x, y, z]) - p_kante_global)

        # Zeichne Kugelmittelpunkt
        ax.scatter(x, y, z, color='blue', s=80, label='Kugelmittelpunkt')

        # Zeichne Kollisionspunkt auf Becherrand
        ax.scatter(*p_kante_global, color='orange', s=80, label='Punkt auf Rand')

        # Linie dazwischen
        ax.plot(
            [x, p_kante_global[0]],
            [y, p_kante_global[1]],
            [z, p_kante_global[2]],
            color='green',
            label=f"Abstand: {abstand:.2f}"
        )

        if abstand <= r_kugel:
            ax.text(x, y, z + 2, "💥 Kollision erkannt", color='green')
            print("✅ Kollision erkannt")
        else:
            ax.text(x, y, z + 2, "❌ Keine Kollision", color='black')
            print("❌ Keine Kollision")

# Achsen & Ansicht
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)
ax.set_zlim(0, 20)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.legend()
plt.show()
