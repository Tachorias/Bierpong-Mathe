from numpy import *
from pylab import figure, show, axis
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from celluloid import Camera

# ------ Tischebene erstellen -------
x_vals = [0, 60]
y_vals = [0, 230]
x_t, y_t = meshgrid(x_vals, y_vals)
z_t = ones((2, 2))  # Tischhöhe = z = 1

# ----- Becher erstellen -----
def erstelle_becher(x0, y0, z0):
    t = linspace(0, 2 * pi, 30)
    r = 4  # Radius
    x_becher = r * cos(t)
    y_becher = r * sin(t)
    h = 12  # Höhe

    seiten = []
    for i in range(len(t) - 1):
        seiten.append([
            [x0 + x_becher[i], y0 + y_becher[i], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0 + h],
            [x0 + x_becher[i], y0 + y_becher[i], z0 + h]
        ])

    boden = []
    for i in range(len(t)):
        boden.append([x0 + x_becher[i], y0 + y_becher[i], z0])
    boden.append(boden[0])

    return seiten, boden

# ---- Becherpositionen ----
x0, y0 = 30, 190
positionen_versatz = [
    (0, 0),
    (-5, 10), (5, 10),
    (-10, 20), (0, 20), (10, 20),
    (-15, 30), (-5, 30), (5, 30), (15, 30)
]

# ---- Wurfparameter ----
x_start = 30
y_start = 0
z_start = 90
v0 = 50  # cm/s
t_winkel = radians(0)
p_winkel = radians(-3)
vx = v0 * cos(p_winkel) * sin(t_winkel)
vy = v0 * cos(p_winkel) * cos(t_winkel)
vz_start = v0 * sin(p_winkel)
g = 9.81
e = 0.88  # Elastizität

# ---- Kugel erstellen ----
s_k = linspace(0, 2 * pi, 100)
t_k = s_k
S_k, T_k = meshgrid(s_k, t_k)
r_k = 2

# ---- Zeiterfassung & Ballzustand ----
t_bounce = 0
x_start_actual = x_start
y_start_actual = y_start
z_start_actual = z_start
vz = vz_start
z_tisch = 1

# ----- MAIN PROGRAM -----
fig = figure()
ax = fig.add_subplot(111, projection='3d')
camera = Camera(fig)

dt = 0.1
total_time = 5

for t in arange(0, total_time + dt, dt):
    # Tisch zeichnen
    ax.plot_surface(x_t, y_t, z_t, color='grey', alpha=0.3)

    # Becher zeichnen
    for dx, dy in positionen_versatz:
        becher_x = x0 + dx
        becher_y = y0 + dy
        seiten, boden = erstelle_becher(becher_x, becher_y, 1)
        ax.add_collection3d(Poly3DCollection(seiten, facecolors='darkred', edgecolors='black', alpha=0.9))
        ax.add_collection3d(Poly3DCollection([boden], facecolors='darkred', edgecolors='black', alpha=0.8))

    # Zeit seit letztem Aufprall
    t_rel = t - t_bounce

    # Position berechnen
    x = x_start_actual + vx * t_rel
    y = y_start_actual + vy * t_rel
    z = z_start_actual + vz * t_rel - 0.5 * g * t_rel**2

    # Momentane vertikale Geschwindigkeit
    vz_t = vz - g * t_rel

    # Kollisionserkennung & Abprallen
    if z <= z_tisch and vz_t < 0:
        vz = -vz_t * e  # reflektieren mit Elastizität
        t_bounce = t
        x_start_actual = x
        y_start_actual = y
        z_start_actual = z_tisch
        z = z_tisch  # Korrektur für Darstellungsgenauigkeit

    # Kugel zeichnen
    X_k = r_k * sin(T_k) * cos(S_k) + x
    Y_k = r_k * sin(T_k) * sin(S_k) + y
    Z_k = r_k * cos(T_k) + z
    ax.plot_surface(X_k, Y_k, Z_k, cmap='jet', color='orange')

    axis('scaled')
    camera.snap()

# ------- Animation anzeigen -------
anim = camera.animate(interval=30)
show()
