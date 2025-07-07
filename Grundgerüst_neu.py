from numpy import *
import matplotlib
from matplotlib.pyplot import figure, show, axis
matplotlib.use('TkAgg')
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from celluloid import Camera


# ---- Parameter ----

r_becher, h_becher, inner_r_becher = 4, 12, 3.9  # Radius_Becher, Hoehe_Becher
r_kugel = 2  # Radius_Kugel
x_tisch, y_tisch, z_tisch = 60, 230, 1  # Breite_Tisch, Laenge_Tisch, Hoehe_Tisch
g = 9.81  # Erdanziehung
e_kugel = 0.88  # Elastizität_Kugel
dt = 0.05  # Zeitschritt

# ------ Tischebene erstellen -------
x_vals = [0, 60]
y_vals = [0, 230]
x_t, y_t = meshgrid(x_vals, y_vals)
z_t = zeros((2, 2))  # Tischhöhe = z = 1

# ----- Becher erstellen -----


def erstelle_becher(x0, y0, z0):
    t = linspace(0, 2 * pi, 30)
    x_becher = r_becher * cos(t)
    y_becher = r_becher * sin(t)

    seiten = []
    for i in range(len(t) - 1):
        seiten.append([
            [x0 + x_becher[i], y0 + y_becher[i], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0 + h_becher],
            [x0 + x_becher[i], y0 + y_becher[i], z0 + h_becher]
        ])

    boden = []
    for i in range(len(t)):
        boden.append([x0 + x_becher[i], y0 + y_becher[i], z0])
    boden.append(boden[0])

    bieroberflaeche = []
    for i in range(len(t)):
        bieroberflaeche.append([x0 + x_becher[i], y0 + y_becher[i], z0 + h_becher / 2])
    bieroberflaeche.append(bieroberflaeche[0])

    return seiten, boden, bieroberflaeche


# ------- unsichtbare Becher --------
s = linspace(0, h_becher, 10)
t = linspace(0, 2 * pi, 25)
S, T = meshgrid(s, t)
X = cos(T) * r_becher
Y = sin(T) * r_becher
Z = S


# ---- Funktion zum Zeichnen von Bechern ----
def zeichne_becher(ax, x, y, z=0, sichtbar=True):
    seiten, boden, bieroberflaeche = erstelle_becher(x, y, z)

    if sichtbar:
        ax.add_collection3d(Poly3DCollection(seiten, facecolors='red', edgecolors='black', alpha=1))
        ax.add_collection3d(Poly3DCollection([boden], facecolors='darkred', edgecolors='black', alpha=0.8))
        ax.add_collection3d(Poly3DCollection([bieroberflaeche], facecolors='yellow', edgecolors='black', alpha=0.8))
    else:
        ax.plot_surface(X + x, Y + y, Z + z, cmap='jet', alpha=0)


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


total_time = 5

for t in arange(0, total_time + dt, dt):
    # Tisch zeichnen
    ax.plot_surface(x_t, y_t, z_t, color='grey', alpha=0.3)

    # Becher zeichnen
    for dx, dy in positionen_versatz:
        becher_x = x0 + dx
        becher_y = y0 + dy
        zeichne_becher(ax, becher_x, becher_y, sichtbar=True)
        zeichne_becher(ax, becher_x, becher_y, sichtbar=False)
        X = cos(T) * r_becher
        Y = sin(T) * r_becher
        Z = S


    # Zeit seit letztem Aufprall
    t_rel = t - t_bounce

    # Position berechnen
    x = x_start_actual + vx * t_rel
    y = y_start_actual + vy * t_rel
    z = z_start_actual + vz * t_rel - 0.5 * g * t_rel ** 2

    # Momentane vertikale Geschwindigkeit
    vz_t = vz - g * t_rel
    vx_t = vx -g * sin(t_winkel) * cos(t_winkel) * t_rel
    vy_t = vy -g * cos(t_winkel) * t_rel

    # Kollisionerkennung Becher
    local_Sphere = array([x, y, z]) - array([x0, y0, 0])
    l_x, l_y, l_z = local_Sphere
    # 3. Abstand in XY-Ebene zur Zylinderachse
    vertical_dist = l_z - h_becher
    dist_xy = l_x ** 2 + l_y ** 2
    if 0 < vertical_dist <= r_kugel:

        vectorS = local_Sphere - array([0,0,12])
        cylinder_Achse = array([0,0,1])
        normale = linalg.cross((linalg.cross(vectorS, cylinder_Achse)), cylinder_Achse)
        normale_2 = vectorS - normale
        norm_len = linalg.norm(normale_2)
        # if norm_len == 0:
        #     continue  # Keine Richtung – Kugel liegt auf Zylinderachse

        direction = normale_2 / norm_len  # Einheitsvektor auf der Endkappe

        # Punkt auf Rand des Bechers in Richtung Kugel
        p_Kante = array([0, 0, h_becher]) + direction * r_becher

        # Abstand von Kugelmittelpunkt zu diesem Punkt auf dem Rand
        abstand = linalg.norm(local_Sphere - p_Kante)

        if abstand - 0.01 <= r_becher:
            print("Kollision Becherkante")
            vz = -vz_t * e
            t_bounce = t
            x_start_actual = x
            y_start_actual = y
            z_start_actual = h_becher + r_kugel
            z = h_becher + r_kugel


    if (0 <= l_z <= h_becher) and ((r_becher - r_kugel)**2 <= dist_xy <= (r_becher + r_kugel)**2):
        print("Kollision Aussenwand")
    else:
        if (0 <= l_z <= h_becher) and (dist_xy <= (r_becher - r_kugel)**2):
            print("Kollision Innenwand")

    #Kollision mit dem Tisch
    if z-r_kugel <= z_tisch and vz_t < 0:
        vz = -vz_t * e
        t_bounce = t
        x_start_actual = x
        y_start_actual = y
        z_start_actual = z_tisch + r_kugel
        z = z_tisch +r_kugel




    # Kollisionserkennung mit der Bieroberfläche
    # if z <= 12 and vz_t < 0:
    #     for dx, dy in positionen_versatz:
    #         becher_x = x0 + dx
    #         becher_y = y0 + dy
    #         abstand = sqrt((x - becher_x) ** 2 + (
    #                     y - becher_y) ** 2)  # Abstand zwischen Mittelpunkt des Bechers und des Balles berechnen
    #
    #         if abstand <= r_becher - r_kugel:  # damit die Kugel komplett im Becher ist
    #             # Ball stoppen
    #             vz = vy = vx = 0
    #
    #             # Startwerte auf aktuelle Position setzen
    #             x_start_actual = x
    #             y_start_actual = y
    #             z_start_actual = z
    #             t_bounce = t
    #
    #             break;

    # Kugel zeichnen
    X_k = r_kugel * sin(T_k) * cos(S_k) + x
    Y_k = r_kugel * sin(T_k) * sin(S_k) + y
    Z_k = r_kugel * cos(T_k) + z
    ax.plot_surface(X_k, Y_k, Z_k, cmap='jet', color='orange')

    axis('scaled')
    camera.snap()

# ------- Animation anzeigen -------
anim = camera.animate(interval=30)
show()
