#!/usr/bin/env python3
"""Erzeugt bauplan.png: bemasste Werkstattzeichnung der Box (Box links;
rechte Box spiegelbildlich). Alle Masse in mm. Laeuft mit matplotlib."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

HOLZ = "#e8d6b8"; KANTE = "#6b5236"; MASS = "#1a4a7a"; ROT = "#b03030"

def dim_h(ax, x0, x1, y, text, oben=True):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=MASS, lw=1.1))
    ax.text((x0 + x1) / 2, y + (4 if oben else -11), text, ha="center", color=MASS, fontsize=9)

def dim_v(ax, x, y0, y1, text):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=MASS, lw=1.1))
    ax.text(x + 5, (y0 + y1) / 2, text, va="center", color=MASS, fontsize=9, rotation=90)

def platte(ax, b, h, titel):
    ax.add_patch(Rectangle((0, 0), b, h, facecolor=HOLZ, edgecolor=KANTE, lw=2))
    ax.set_title(titel, fontsize=11, weight="bold")
    ax.set_aspect("equal"); ax.set_xlim(-45, b + 45); ax.set_ylim(-45, h + 60)
    ax.axis("off")

fig, axs = plt.subplots(2, 2, figsize=(13.5, 9.2), dpi=140)
fig.suptitle("Bauplan Stereo-Lautsprecher (Hertz K 165, geschlossen) – Box LINKS, Maße in mm.  "
             "Rechte Box: alle x-Maße spiegeln (x' = 400 − x)", fontsize=12.5, weight="bold")

# --- Front (von aussen) ---
ax = axs[0][0]; platte(ax, 400, 250, "FRONT von außen (Platte 364 × 214 sitzt zwischen den Wänden)")
for d, x, name in ((116, 150, "Tieftöner Ø 116\n+ 45°-Fase innen"), (30.2, 300, "Hochtöner Ø 30,2\n(am Becher prüfen!)")):
    ax.add_patch(Circle((x, 125), d / 2, fill=False, color=KANTE, lw=1.8))
    ax.plot(x, 125, "+", color=KANTE, ms=10)
    ax.text(x, 125 - d / 2 - 26, name, ha="center", fontsize=8.5, color=KANTE)
dim_h(ax, 0, 150, 262, "150"); dim_h(ax, 0, 300, 285, "300")
dim_v(ax, -28, 0, 125, "125"); dim_h(ax, 0, 400, -30, "400", oben=False)

# --- Rueckwand (von hinten) ---
ax = axs[0][1]; platte(ax, 400, 250, "RÜCKWAND von hinten gesehen")
ax.add_patch(Circle((60, 50), 6, fill=False, color=KANTE, lw=1.8)); ax.plot(60, 50, "+", color=KANTE, ms=8)
ax.text(60, 70, "Kabel Ø 12\n(M12-Verschraubung)", ha="center", fontsize=8.5, color=KANTE)
ax.add_patch(Circle((200, 125), 51, fill=False, color=ROT, lw=1.3, linestyle="--"))
ax.text(200, 186, "Ø 102 NICHT bohren!\n(nur für die Bassreflex-Variante)", ha="center", fontsize=8.5, color=ROT)
dim_h(ax, 0, 60, 262, "60"); dim_v(ax, -28, 0, 50, "50"); dim_h(ax, 0, 400, -30, "400", oben=False)

# --- Draufsicht (Schnitt) ---
ax = axs[1][0]; platte(ax, 400, 300, "DRAUFSICHT, aufgeschnitten (Front unten)")
ax.add_patch(Rectangle((18, 18), 364, 264, facecolor="white", edgecolor="none"))
for r in ((0, 0, 400, 18), (0, 282, 400, 18), (0, 0, 18, 300), (382, 0, 18, 300)):
    ax.add_patch(Rectangle((r[0], r[1]), r[2], r[3], facecolor=HOLZ, edgecolor=KANTE, lw=1.2))
ax.add_patch(Rectangle((18, 121), 364, 18, facecolor="#d9b98a", edgecolor=KANTE, lw=1.2, hatch="//"))
ax.text(200, 148, "Fensterstrebe (Fenster 304 × 154, Ecken R 20)", ha="center", va="center", fontsize=8.5)
ax.add_patch(Rectangle((245, 18), 20, 264, facecolor="#caa06a", edgecolor=KANTE, lw=1))
ax.text(255, 230, "Rundstab Ø 20\n(x = 255, z = 70)", ha="center", fontsize=8, rotation=90)
ax.plot([92, 208], [18, 18], color=ROT, lw=3)
ax.text(150, 30, "Tieftöner", ha="center", fontsize=8.5, color=ROT)
dim_v(ax, 428, 0, 121, "121 bis Strebe")
ax.annotate("", (-28, 0), (-28, 300), arrowprops=dict(arrowstyle="<->", color=MASS, lw=1.1))
ax.text(-36, 150, "300", va="center", color=MASS, fontsize=9, rotation=90)
ax.text(200, -32, "Strebe: Vorderkante 121 mm hinter der Außenfront", ha="center", fontsize=9, color=MASS)

# --- Daemmschema (Seitenschnitt) ---
ax = axs[1][1]; platte(ax, 300, 250, "DÄMMUNG (Seitenschnitt, Front links) – geschlossene Box")
ax.add_patch(Rectangle((18, 18), 264, 214, facecolor="white", edgecolor="none"))
for r in ((0, 0, 300, 18), (0, 232, 300, 18), (0, 0, 18, 250), (282, 0, 18, 250)):
    ax.add_patch(Rectangle((r[0], r[1]), r[2], r[3], facecolor=HOLZ, edgecolor=KANTE, lw=1.2))
ax.add_patch(Rectangle((121, 18), 18, 214, facecolor="#d9b98a", edgecolor=KANTE, lw=1.2, hatch="//"))
for r in ((252, 18, 30, 214), (18, 202, 103, 30), (139, 202, 113, 30)):   # Rueckwand + Deckel
    ax.add_patch(Rectangle((r[0], r[1]), r[2], r[3], facecolor="#f3ead2", edgecolor="#b9a97e", lw=1, hatch="..."))
ax.add_patch(Rectangle((139, 18), 113, 184, facecolor="none", edgecolor="#b9a97e", lw=1.2, linestyle=":"))
ax.text(195, 110, "hintere Kammer\nlocker füllen", ha="center", fontsize=8.5, color="#7a6a40")
ax.text(76, 110, "vordere Kammer:\nWände 2–3 cm belegen,\n≥ 3 cm Luft hinter\nder Membran", ha="center", fontsize=8.5, color="#7a6a40")
ax.plot([18, 18], [67, 183], color=ROT, lw=3)
ax.text(28, 125, "Chassis", fontsize=8.5, color=ROT, rotation=90, va="center")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig("bauplan.png")
print("bauplan.png geschrieben")
