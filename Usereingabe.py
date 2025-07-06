import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation

# ----- Parameter -----
r_becher, h_becher = 4, 12
r_kugel = 2
x_tisch, y_tisch, z_tisch = 60, 230, 1
g = 9.81
e = 0.88

# ---- Becherpositionen ----
x0, y0 = 30, 190
positionen_versatz = [
    (0, 0), (-5, 10), (5, 10), (-10, 20), (0, 20), (10, 20),
    (-15, 30), (-5, 30), (5, 30), (15, 30)
]

# ---- Globale Variablen ----
ball_plot = [None]
ani = None

# ---- Funktionen ----
def erstelle_becher(x0, y0, z0):
    t = np.linspace(0, 2 * np.pi, 30)
    x_becher = r_becher * np.cos(t)
    y_becher = r_becher * np.sin(t)

    seiten = []
    for i in range(len(t) - 1):
        seiten.append([
            [x0 + x_becher[i], y0 + y_becher[i], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0],
            [x0 + x_becher[i + 1], y0 + y_becher[i + 1], z0 + h_becher],
            [x0 + x_becher[i], y0 + y_becher[i], z0 + h_becher]
        ])

    boden = [[x0 + x_becher[i], y0 + y_becher[i], z0] for i in range(len(t))]
    bieroberflaeche = [[x0 + x_becher[i], y0 + y_becher[i], z0 + h_becher/2] for i in range(len(t))]

    return seiten, [boden], [bieroberflaeche]

def zeichne_becher(ax, x, y, z=1):
    seiten, boden, bieroberflaeche = erstelle_becher(x, y, z)
    ax.add_collection3d(Poly3DCollection(seiten, facecolors='red', edgecolors='black', alpha=1))
    ax.add_collection3d(Poly3DCollection(boden, facecolors='darkred', edgecolors='black', alpha=0.8))
    ax.add_collection3d(Poly3DCollection(bieroberflaeche, facecolors='yellow', edgecolors='black', alpha=0.8))

def kugel_daten(x, y, z):
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 15)
    X = r_kugel * np.outer(np.cos(u), np.sin(v)) + x
    Y = r_kugel * np.outer(np.sin(u), np.sin(v)) + y
    Z = r_kugel * np.outer(np.ones_like(u), np.cos(v)) + z
    return X, Y, Z

def berechne_bahn(v0, t_winkel_deg, p_winkel_deg):
    t_winkel = np.radians(t_winkel_deg)
    p_winkel = np.radians(p_winkel_deg)

    vx = v0 * np.cos(p_winkel) * np.sin(t_winkel)
    vy = v0 * np.cos(p_winkel) * np.cos(t_winkel)
    vz = v0 * np.sin(p_winkel)

    dt = 0.05
    t_max = 5
    px, py, pz = [], [], []

    x, y, z = 30, 0, 90
    vz0 = vz
    t_bounce = 0
    x0, y0, z0 = x, y, z

    for t in np.arange(0, t_max, dt):
        t_rel = t - t_bounce
        xt = x0 + vx * t_rel
        yt = y0 + vy * t_rel
        zt = z0 + vz0 * t_rel - 0.5 * g * t_rel**2
        vz_t = vz0 - g * t_rel

        # Aufprall auf Tisch
        if zt - r_kugel <= z_tisch and vz_t < 0:
            vz0 = -vz_t * e
            vx *= e
            vy *= e
            if abs(vz0) < 0.1:
                break  # zu wenig Energie zum Fortsetzen
            t_bounce = t
            x0, y0, z0 = xt, yt, z_tisch + r_kugel
            continue

        # Treffer in Becher
        for dx, dy in positionen_versatz:
            bx, by = x0 + dx, y0 + dy
            localS = transform_to_local(np.array([xt, yt, zt]), np.array([bx, by, 0]))
            dist = (localS[0])**2 + (localS[1])**2
            if zt <= h_becher and dist < (r_becher - r_kugel)**2:
                print("Bechertreffer")
                vx = vy = vz0 = 0
                x0, y0, z0 = xt, yt, zt
                t_bounce = t
                break

        px.append(xt)
        py.append(yt)
        pz.append(max(zt, z_tisch + r_kugel))

    return px, py, pz

def transform_to_local(P_global, C):
    # Vektor vom Zylinderzentrum zur Kugel
    r = P_global - C
    X_local = np.array([1, 0, 0])
    Y_local = np.array([0, 1, 0])
    Z_local = np.array([0, 0, 1])
    # Projektion in lokale Basis
    x_local = np.dot(r, X_local)
    y_local = np.dot(r, Y_local)
    z_local = np.dot(r, Z_local)

    return np.array([x_local, y_local, z_local])

# ----- Plot Setup -----
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(0, x_tisch)
ax.set_ylim(0, y_tisch)
ax.set_zlim(0, 100)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title("Bierpong-Simulation")
ax.set_box_aspect([x_tisch, y_tisch, 100])

# Tisch zeichnen
x_vals = [0, x_tisch]
y_vals = [0, y_tisch]
x_t, y_t = np.meshgrid(x_vals, y_vals)
z_t = np.ones_like(x_t) * z_tisch
ax.plot_surface(x_t, y_t, z_t, color='grey', alpha=0.3)

# Becher zeichnen
for dx, dy in positionen_versatz:
    zeichne_becher(ax, x0 + dx, y0 + dy)

# ----- Slider Setup -----
ax_v = plt.axes([0.2, 0.01, 0.65, 0.02])
ax_tw = plt.axes([0.2, 0.045, 0.65, 0.02])
ax_pw = plt.axes([0.2, 0.08, 0.65, 0.02])

s_v = Slider(ax_v, 'Startgeschwindigkeit', 10, 100, valinit=50)
s_tw = Slider(ax_tw, 'links/rechts (°)', -45, 45, valinit=0)
s_pw = Slider(ax_pw, 'Wurfwinkel (°)', -45, 45, valinit=-10)

# ----- Button Setup -----
ax_button = plt.axes([0.42, 0.115, 0.15, 0.04])
button = Button(ax_button, "Neuer Wurf", color='lightgray', hovercolor='lightblue')

# ----- Animations-Update -----
def update(frame):
    global ball_plot, px, py, pz
    if ball_plot[0]:
        ball_plot[0].remove()

    if frame < len(px):
        X, Y, Z = kugel_daten(px[frame], py[frame], pz[frame])
        ball_plot[0] = ax.plot_surface(X, Y, Z, color='orange')
    return ball_plot[0],

def redraw(val):
    neuer_wurf()

def neuer_wurf(event=None):
    global px, py, pz, ani, ball_plot

    px, py, pz = berechne_bahn(s_v.val, s_tw.val, s_pw.val)

    if ball_plot[0]:
        ball_plot[0].remove()
        ball_plot[0] = None

    if ani:
        ani.event_source.stop()

    ani = FuncAnimation(fig, update, frames=len(px), interval=30, blit=False)
    plt.draw()

s_v.on_changed(redraw)
s_tw.on_changed(redraw)
s_pw.on_changed(redraw)
button.on_clicked(neuer_wurf)

# Erste Animation erzeugen
neuer_wurf()
plt.show()
