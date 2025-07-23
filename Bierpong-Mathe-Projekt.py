from numpy import *
import matplotlib
from matplotlib.pyplot import figure, show, axis, plot
matplotlib.use('TkAgg')
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from celluloid import Camera



# ---- Parameter ----

r_becher, h_becher = 4, 12 # Radius_Becher, Hoehe_Becher
r_kugel = 2  # Radius_Kugel
x_tisch, y_tisch, z_tisch = 60, 230, 0  # Breite_Tisch, Laenge_Tisch, Hoehe_Tisch
g = 9.81  # Erdanziehung
e_kugel = 0.88  # Elastizität_Kugel
dt = 0.03 # Zeitschritt

# ----- Bounding Boxes erstellen -----

def berechne_aabb_becher(becher_x, becher_y, r_becher, h_becher, puffer=2):
    r_total = r_becher + r_kugel
    return {
        "min": array([becher_x - r_total - puffer, becher_y - r_total - puffer, 0]),
        "max": array([becher_x + r_total + puffer, becher_y + r_total + puffer, h_becher + r_kugel+puffer])
    }

def kugel_in_aabb(pos, aabb):
    return all(aabb["min"] <= pos) and all(pos <= aabb["max"])


# ------ Tischebene erstellen -------

x_vals = [0, 60]
y_vals = [0, 230]
x_t, y_t = meshgrid(x_vals, y_vals)
z_t = zeros((2, 2))  # Tischhöhe = z = 0


# ----- Becher erstellen -----

def erstelle_becher(x0, y0, z0):
    t = linspace(0, 2 * pi, 15)
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
        bieroberflaeche.append([x0 + x_becher[i], y0 + y_becher[i], z0 + h_becher - 11])
    bieroberflaeche.append(bieroberflaeche[0])

    return seiten, boden, bieroberflaeche



# ---- Funktion zum Zeichnen von Bechern ----

def zeichne_becher(ax, x, y, z=0):
    seiten, boden, bieroberflaeche = erstelle_becher(x, y, z)

    ax.add_collection3d(Poly3DCollection(seiten, facecolors='red', edgecolors='black', alpha=1))
    ax.add_collection3d(Poly3DCollection([boden], facecolors='darkred', edgecolors='black', alpha=0.8))
    ax.add_collection3d(Poly3DCollection([bieroberflaeche], facecolors='yellow', edgecolors='black', alpha=0.8))

from mpl_toolkits.mplot3d.art3d import Line3DCollection

# ----- Bounding Boxes zeichnen -----

def zeichne_bounding_box(ax, aabb, farbe='limegreen', alpha=0.2):
    min_p = aabb['min']
    max_p = aabb['max']

    # Alle 8 Ecken der Bounding Box
    x0, y0, z0 = min_p
    x1, y1, z1 = max_p

    ecken = array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]
    ])

    kanten = [
        [ecken[0], ecken[1]], [ecken[1], ecken[2]], [ecken[2], ecken[3]], [ecken[3], ecken[0]],
        [ecken[4], ecken[5]], [ecken[5], ecken[6]], [ecken[6], ecken[7]], [ecken[7], ecken[4]],
        [ecken[0], ecken[4]], [ecken[1], ecken[5]], [ecken[2], ecken[6]], [ecken[3], ecken[7]]
    ]

    box = Line3DCollection(kanten, colors=farbe, linewidths=1.5, alpha=alpha)
    ax.add_collection3d(box)

# ---- Becherpositionen ----

x0, y0 = 30, 190
positionen_versatz = [
    (0, 0),
    (-5, 10), (5, 10),
    (-10, 20), (0, 20), (10, 20),
    (-15, 30), (-5, 30), (5, 30), (15, 30)
]
#Beispielwürfe
#v0 = 50 p = -1 Becherkante
#v0 = 40 p = 3 Tisch und Becherwand
#v0 = 50 p = 4
#v0 = 50 p = 3


# ---- Wurfparameter ----

x_start = 30
y_start = 0
z_start = 90
v0 = 50  # cm/s
t_winkel = radians(0)
p_winkel = radians(-1)
vx = v0 * cos(p_winkel) * sin(t_winkel)
vy = v0 * cos(p_winkel) * cos(t_winkel)
vz = v0 * sin(p_winkel)

# ---- Kugel erstellen ----

s_k = linspace(0, 2 * pi, 30)
t_k = s_k
S_k, T_k = meshgrid(s_k, t_k)

# ---- Zeiterfassung & Ballzustand ----

t_bounce = 0
x_start_actual = x_start
y_start_actual = y_start
z_start_actual = z_start

# merken der Ballposition zum Flugbahn plotten

flugbahn_x = []
flugbahn_y = []
flugbahn_z = []

collision_points = []

# ----- MAIN PROGRAM -----
fig = figure()
ax = fig.add_subplot(111, projection='3d')
camera = Camera(fig)


total_time = 6

for t in arange(0, total_time + dt, dt):

    # Tisch zeichnen
    ax.plot_surface(x_t, y_t, z_t, color='grey', alpha=0.3)

    # Becher zeichnen
    for dx, dy in positionen_versatz:
        becher_x = x0 + dx
        becher_y = y0 + dy
        zeichne_becher(ax, becher_x, becher_y)


    # Zeit seit letztem Aufprall
    t_rel = t - t_bounce

    # Position berechnen
    x = x_start_actual + vx * t_rel
    y = y_start_actual + vy * t_rel
    z = z_start_actual + vz * t_rel - 0.5 * g * t_rel ** 2

    # aktuelle Position zur Flugbahn hinzufügen
    flugbahn_x.append(x)
    flugbahn_y.append(y)
    flugbahn_z.append(z)


    #momentane vertikale Geschwindigkeit
    vz_t = vz - g * t_rel


    # Kollisionerkennung Becher (optimiert mit Bounding Boxes)

    if z < h_becher + r_kugel + 1:
        kugel_pos = array([x, y, z])

        for dx, dy in positionen_versatz:
            becher_x = x0 + dx
            becher_y = y0 + dy

            aabb = berechne_aabb_becher(becher_x, becher_y, r_becher, h_becher)
            zeichne_bounding_box(ax, aabb)
            if not kugel_in_aabb(kugel_pos, aabb):
                continue  # Kugel ist zu weit weg → keine Kollision möglich

            local_Sphere = kugel_pos - array([becher_x, becher_y, 0])
            l_x, l_y, l_z = local_Sphere
            dist_xy = l_x ** 2 + l_y ** 2

            if dist_xy < (r_becher + r_kugel) ** 2 and l_z > h_becher:
                # Kollision Becherkante
                normale = array([l_x, l_y, 0])
                norm_len = normale / linalg.norm(normale)

                p_Kante = array([0, 0, h_becher]) + norm_len * r_becher
                abstand = linalg.norm(local_Sphere - p_Kante)

                if abstand <= r_kugel + 0.01:
                    print("Kollision Becherkante")
                    world_kollisionspunkt = p_Kante + array([becher_x, becher_y, 0])
                    collision_points.append(tuple(world_kollisionspunkt))

                    kollK_Normale = (local_Sphere - p_Kante) / abstand
                    v_rel = array([vx, vy, vz_t])
                    v_reflektiert = v_rel - (1 + e_kugel) * dot(v_rel, kollK_Normale) * kollK_Normale

                    vx, vy, vz = v_reflektiert

                    local_Sphere = p_Kante + kollK_Normale * (r_kugel + 1e-3)
                    x, y, z = local_Sphere + array([becher_x, becher_y, 0])

                    t_bounce = t
                    x_start_actual, y_start_actual, z_start_actual = x, y, z

                    break

            elif (r_becher) ** 2 <= dist_xy <= ((r_becher + r_kugel) ** 2)+0.01:
                print("Kollision Aussenwand")

                world_kollisionspunkt = array([becher_x, becher_y, l_z]) + (
                            array([l_x, l_y, 0]) / linalg.norm([l_x, l_y])) * r_becher
                collision_points.append(tuple(world_kollisionspunkt))

                cylinder_hoehe_kugel = array([l_x, l_y, 0])
                kollA_len = cylinder_hoehe_kugel / linalg.norm(cylinder_hoehe_kugel)
                p_kollA = array([0,0,l_z]) + r_becher * kollA_len
                kollA_Normale = (local_Sphere - p_kollA) / linalg.norm(local_Sphere - p_kollA)
                v_rel = array([vx, vy, vz_t])
                v_reflektiert = v_rel - (1 + e_kugel) * dot(v_rel, kollA_Normale) * kollA_Normale
                vx, vy, vz = v_reflektiert
                local_Sphere = p_kollA + kollA_Normale * (r_kugel + 1e-3)
                x, y, z = local_Sphere + array([becher_x, becher_y, 0])

                t_bounce = t
                x_start_actual, y_start_actual, z_start_actual = x, y, z

                break

            elif(r_becher**2 >dist_xy >= (r_becher - r_kugel) ** 2):
                print("Kollision Innenwand")

                cylinder_hoehe_kugel = array([l_x, l_y, 0])
                kollA_len = cylinder_hoehe_kugel / linalg.norm(cylinder_hoehe_kugel)
                p_kollA = array([0, 0, l_z]) + r_becher * kollA_len
                kollA_Normale = (local_Sphere - p_kollA) / linalg.norm(local_Sphere - p_kollA)
                v_rel = array([vx, vy, vz_t])
                v_reflektiert = v_rel - (1 + e_kugel) * dot(v_rel, kollA_Normale) * kollA_Normale
                vx, vy, vz = v_reflektiert
                local_Sphere = p_kollA + kollA_Normale * (r_kugel + 0.01)
                x, y, z = local_Sphere + array([becher_x, becher_y, 0])

                t_bounce = t
                x_start_actual, y_start_actual, z_start_actual = x, y, z

                break

    if z-r_kugel-0.1 <= z_tisch and vz_t < 0:
        vz = -vz_t * e_kugel
        t_bounce = t
        x_start_actual = x
        y_start_actual = y
        z_start_actual = z_tisch + r_kugel
        z = z_tisch + r_kugel
        world_kollisionspunkt = array([x, y, z])
        collision_points.append(tuple(world_kollisionspunkt))

    #Kollisionserkennung mit der Bieroberfläche
    if z <= 0 and vz_t < 0:
        for dx, dy in positionen_versatz:
            becher_x = x0 + dx
            becher_y = y0 + dy
            dist_xy = (x-becher_x)**2 + (y-becher_y)**2
            if dist_xy <= (r_becher - r_kugel)**2:  # damit die Kugel komplett im Becher ist
                # Ball stoppen
                vz = vy = vx = 0

                # Startwerte auf aktuelle Position setzen
                x_start_actual = x
                y_start_actual = y
                z_start_actual = z
                t_bounce = t

                break;

    # Kugel zeichnen
    X_k = r_kugel * sin(T_k) * cos(S_k) + x
    Y_k = r_kugel * sin(T_k) * sin(S_k) + y
    Z_k = r_kugel * cos(T_k) + z
    ax.plot_surface(X_k, Y_k, Z_k, cmap='jet', color='orange')
    for(x,y,z) in collision_points:
        ax.scatter(x,y,z, c='r', marker='o', s=30)


    axis('scaled')
    camera.snap()

# Flugbahn zeichnen
ax.plot3D(flugbahn_x, flugbahn_y, flugbahn_z, color='blue')

# ------- Animation anzeigen -------
anim = camera.animate(interval=30)
show()