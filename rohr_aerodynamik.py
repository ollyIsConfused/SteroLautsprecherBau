#!/usr/bin/env python3
"""Aerodynamische Auslegung des Bassreflexrohrs (Sanduhr-Rohr).

Erzeugt:
  rohr_profil.scad  – Innenkontur + Masse fuer lautsprecherbox.scad
  stroemung.png     – Stroemungsbild (Potentialstroemung, Schnitt durch Rohr und Box)

Was gerechnet wird:
  1. Trichterkontur mit konstanter Abloese-Sicherheit ("Iso-KC"):
     An jeder Stelle des Trichters gilt  Kruemmungsradius * Flaeche = konstant.
     Die Luft wird nach aussen langsamer (Flaeche waechst), also darf die Wand
     dort staerker gekruemmt sein. So ist jede Stelle gleich weit von der
     Stroemungsabloesung entfernt (Keulegan-Carpenter-Zahl KC = Luftauslenkung /
     Kruemmungsradius ueberall gleich).
  2. Akustische Masse des Rohrs aus einer rotationssymmetrischen
     Potentialstroemung (Finite-Volumen, inkl. Muendungskorrekturen innen und
     aussen) -> Abstimmfrequenz. Die Engstelle wird so gewaehlt, dass die
     Zielfrequenz getroffen wird.
  3. Erste Rohrresonanz (Laengsresonanz) mit einem 1D-Leitungsmodell und dazu
     passend die Lochzahl der Resonanzfalle (bedaempfter Helmholtz-Absorber).

Grenzen: Die Rechnung ist reibungsfrei. Sie zeigt die ideale, anliegende
Stroemung und liefert die Abstimmung. Turbulenz und Stroemungsgeraeusche kann
sie nicht vorhersagen – dafuer steht das KC-Kriterium.

Aufruf:  python3 rohr_aerodynamik.py            (Auslegung + Dateien schreiben)
         python3 rohr_aerodynamik.py --selbsttest (Loeser an gerader Roehre pruefen)
"""
import math
import pathlib
import sys

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

HIER = pathlib.Path(__file__).resolve().parent

# ---------------- Vorgaben (mm, Liter, Hz) ----------------
C0 = 343.0                      # Schallgeschwindigkeit m/s
ZIEL_FB = 45.0                  # Abstimmfrequenz
BOX_INNEN = (364.0, 264.0, 214.0)   # Breite, Tiefe, Hoehe innen (Buche 18 mm)
ABZUG_OHNE_ROHR_L = 1.0 + 0.5594 + 0.0829 + 0.0287 + 0.105  # Tieftoener, Strebe, Stab, Hochtoener, Weiche
PLATTE = 18.0                   # Staerke der Rueckwand

L = 155.0                       # Rohrlaenge: Aussenflaeche Rueckwand bis Mund innen
R_MUND = 49.0                   # Mundradius an beiden Enden (Oe 98)
ROHRWAND = 3.0                  # Wandstaerke im geraden Teil
R_ZYL = 50.7                    # Zylinder, der im 102-mm-Loch der Rueckwand sitzt
R_FLANSCH, FLANSCH_H = 63.0, 4.0  # Flansch innen an der Rueckwand
R_LAND, LAND_H = 41.8, 6.0      # Sitz fuer die Muffe
MUFFE_RI, MUFFE_W = 42.0, 2.4   # Muffe = Aussenwand der Resonanzkammer
NASE = 8.0                      # Radius der eingerollten Lippe am inneren Mund
LOCH_D = 2.4                    # Loecher der Resonanzfalle
LOCH_S = (4.5, 10.0)            # Abstand der Lochreihen von der Trennebene

VD_CM3 = 60.0                   # angenommenes Hubvolumen des Tieftoeners (Spitze): 135 cm2 x 4,5 mm
R_BOX = math.sqrt(BOX_INNEN[0] * BOX_INNEN[2] / math.pi)  # Ersatzradius der Box (rotationssymmetrisch)


# ---------------- Kontur ----------------
def trichter(r_t, r_m=R_MUND, n=160):
    """Iso-KC-Trichter: d(theta)/d(bogen) = r^2 / K. Liefert x (ab Engstelle), r, K."""
    K = (r_m**3 - r_t**3) / 3.0
    th = np.linspace(0.0, math.pi / 2, n)
    r = (r_t**3 + 3.0 * K * (1.0 - np.cos(th))) ** (1.0 / 3.0)
    dx = np.cos(th) * K / r**2
    x = np.concatenate([[0.0], np.cumsum(0.5 * (dx[1:] + dx[:-1]) * np.diff(th))])
    return x, r, K


def kontur(r_t):
    """Innenkontur s -> r von s = 0 (Mund aussen) bis s = L (Mund innen)."""
    x, r, K = trichter(r_t)
    lf = x[-1]
    if 2 * lf >= L - 20:
        raise ValueError("Trichter zu lang fuer diese Rohrlaenge")
    s_aussen = lf - x[::-1]                 # 0 .. lf
    r_aussen = r[::-1]
    s_innen = L - lf + x                    # L-lf .. L
    s = np.concatenate([s_aussen, [L / 2], s_innen])
    rr = np.concatenate([r_aussen, [r_t], r])
    return s, rr, lf, K


def huelle(s, r_t):
    """Aussenkontur des montierten Rohrs in der Box (ab Innenflaeche Rueckwand)."""
    s = np.asarray(s, dtype=float)
    r_tw = r_t + ROHRWAND
    r_mu = MUFFE_RI + MUFFE_W
    s_fl = PLATTE + FLANSCH_H
    s_land_a0 = s_fl + (R_FLANSCH - R_LAND)
    s_land_b1 = L - s_land_a0
    s_tp = L - NASE - NASE * math.sin(math.radians(45))
    r_tp = R_MUND + NASE * math.cos(math.radians(45))
    out = np.full_like(s, r_mu)
    out = np.where(s < s_fl, R_FLANSCH, out)
    kegel = R_FLANSCH - (s - s_fl)
    out = np.where((s >= s_fl) & (kegel > r_mu), kegel, out)
    hinten = np.maximum(r_tw, r_tp - (s_tp - s))
    out = np.where((s > s_land_b1) & (s <= s_tp), hinten, out)
    nase = R_MUND + np.sqrt(np.clip(NASE**2 - (s - (L - NASE)) ** 2, 0.0, None))
    out = np.where(s > s_tp, nase, out)
    return out


def rohr_volumen_l(r_t):
    s = np.linspace(PLATTE, L, 4000)
    return float(np.trapezoid(math.pi * huelle(s, r_t) ** 2, s)) / 1e6


def netto_l(r_t):
    brutto = BOX_INNEN[0] * BOX_INNEN[1] * BOX_INNEN[2] / 1e6
    return brutto - ABZUG_OHNE_ROHR_L - rohr_volumen_l(r_t)


# ---------------- Potentialstroemung (Finite Volumen, rotationssymmetrisch) ----------------
def loese(bohrung, aussen, s_ende, tiefe_box, h=0.5, D=250.0):
    """bohrung(s), aussen(s): Radien; Kanal fuer 0 < s < s_ende.
    Rueckgabe: akustische Masse / Dichte in 1/m und Felder fuer das Bild."""
    s_min = -(D + 2 * h)
    ns = int(round((tiefe_box + PLATTE - s_min) / h))
    nr = int(round((D + 2 * h) / h))
    s = s_min + (np.arange(ns) + 0.5) * h
    r = (np.arange(nr) + 0.5) * h
    S, R = np.meshgrid(s, r, indexing="ij")
    aussenraum = (S < 0) & (S**2 + R**2 <= D**2)
    fern = (S < 0) & ~aussenraum
    kanal = (S > 0) & (S < s_ende) & (R < bohrung(np.clip(S, 0, s_ende)))
    box = (S > PLATTE) & (S < PLATTE + tiefe_box) & (R < R_BOX) & (
        (S > s_ende) | (R > aussen(np.clip(S, PLATTE, s_ende))))
    fluid = aussenraum | kanal | box
    idx = -np.ones(fluid.shape, dtype=np.int64)
    n = int(fluid.sum())
    idx[fluid] = np.arange(n)

    Q = 1.0
    g_ax = 2 * math.pi * R                 # Leitwert axiale Flaeche / h
    g_ra = 2 * math.pi * (R + h / 2)       # Leitwert radiale Flaeche / h
    zeilen, spalten, werte = [], [], []
    diag = np.zeros(n)
    rhs = np.zeros(n)

    def paare(a, b, g):
        m = fluid[a] & fluid[b]
        i, j, gg = idx[a][m], idx[b][m], g[a][m]
        zeilen.extend([i, j]); spalten.extend([j, i]); werte.extend([-gg, -gg])
        np.add.at(diag, i, gg); np.add.at(diag, j, gg)
        return i, j, gg

    ax = (np.s_[:-1, :], np.s_[1:, :])
    ra = (np.s_[:, :-1], np.s_[:, 1:])
    p_ax = paare(ax[0], ax[1], g_ax)
    p_ra = paare(ra[0], ra[1], g_ra)

    dist = np.sqrt(S**2 + R**2)
    phi_fern = -Q / (2 * math.pi * np.maximum(dist, 1e-9))
    fern_terme = []
    for (a, b, g) in ((ax[0], ax[1], g_ax), (ax[1], ax[0], g_ax), (ra[0], ra[1], g_ra)):
        m = aussenraum[a] & fern[b]
        i = idx[a][m]
        gg = g[a][m]
        pf = phi_fern[b][m]
        np.add.at(diag, i, gg); np.add.at(rhs, i, gg * pf)
        fern_terme.append((i, gg, pf))

    vol = 2 * math.pi * R * h * h
    q = Q / vol[box].sum()
    rhs[idx[box]] -= q * vol[box]

    A = sparse.coo_matrix(
        (np.concatenate(werte + [diag]),
         (np.concatenate(zeilen + [np.arange(n)]), np.concatenate(spalten + [np.arange(n)]))),
        shape=(n, n)).tocsc()
    phi = spsolve(A, rhs)

    E = sum(float(np.sum(gg * (phi[i] - phi[j]) ** 2)) for (i, j, gg) in (p_ax, p_ra))
    E += sum(float(np.sum(gg * (pf - phi[i]) ** 2)) for (i, gg, pf) in fern_terme)
    masse = (E / Q**2 + 1.0 / (2 * math.pi * D)) * 1000.0     # 1/mm -> 1/m

    feld = np.full(fluid.shape, np.nan)
    feld[fluid] = phi
    return masse, dict(s=s, r=r, phi=feld, fluid=fluid, h=h, Q=Q)


def fb_aus_masse(masse, v_l):
    return C0 / (2 * math.pi) * math.sqrt(1.0 / (v_l * 1e-3 * masse))


def rechne(r_t, h=0.5, felder=False):
    s, rr, lf, K = kontur(r_t)
    bohr = lambda x: np.interp(x, s, rr)
    hue = lambda x: huelle(x, r_t)
    masse, f = loese(bohr, hue, L, BOX_INNEN[1], h=h)
    fb = fb_aus_masse(masse, netto_l(r_t))
    return (fb, masse, f) if felder else (fb, masse)


# ---------------- 1D-Modelle ----------------
def masse_1d(r_t):
    s, rr, _, _ = kontur(r_t)
    x = np.linspace(0, L, 4001)
    r = np.interp(x, s, rr)
    kern = float(np.trapezoid(1.0 / (math.pi * r**2), x))
    enden = (0.85 + 0.70) / (math.pi * R_MUND)
    return (kern + enden) * 1000.0


def rohrresonanz(r_t):
    """Erste Laengsresonanz: Maximum von |U_aus / p_Box| zwischen 400 und 3000 Hz."""
    s, rr, _, _ = kontur(r_t)
    x = np.linspace(0, L, 311)
    r = np.interp(0.5 * (x[1:] + x[:-1]), s, rr) * 1e-3
    dl = np.diff(x) * 1e-3
    rho = 1.2
    a = R_MUND * 1e-3
    best = (0.0, 0.0)
    for f in np.arange(400.0, 3000.0, 2.0):
        k = 2 * math.pi * f / C0
        T = np.eye(2, dtype=complex)
        for ri, li in zip(r[::-1], dl[::-1]):          # von innen (s = L) nach aussen (s = 0)
            Z = rho * C0 / (math.pi * ri**2)
            T = T @ np.array([[math.cos(k * li), 1j * Z * math.sin(k * li)],
                              [1j * math.sin(k * li) / Z, math.cos(k * li)]])
        Zm = rho * C0 / (math.pi * a**2)
        z_aus = Zm * ((k * a) ** 2 / 2 + 1j * 0.85 * k * a)
        z_in = Zm * ((k * a) ** 2 / 4 + 1j * 0.70 * k * a)
        u = 1.0 / abs(T[0, 0] * z_aus + T[0, 1] + z_in * (T[1, 0] * z_aus + T[1, 1]))
        if u > best[1]:
            best = (f, u)
    return best[0]


def kammer_volumen_mm3(r_t):
    r_tw = r_t + ROHRWAND
    s_land_a1 = PLATTE + FLANSCH_H + (R_FLANSCH - R_LAND) + LAND_H
    x = np.linspace(s_land_a1, L - s_land_a1, 2000)
    d = np.minimum(x - s_land_a1, (L - s_land_a1) - x)
    r_aussen = np.maximum(r_tw, R_LAND - d)
    return float(np.trapezoid(math.pi * (MUFFE_RI**2 - r_aussen**2), x))


def falle(r_t, f_ziel):
    """Lochzahl je Reihe, damit der Helmholtz-Absorber nahe der Rohrresonanz liegt."""
    vc = kammer_volumen_mm3(r_t) * 1e-9
    t_eff = (ROHRWAND + 0.85 * LOCH_D) * 1e-3
    a1 = math.pi * (LOCH_D * 1e-3 / 2) ** 2
    reihen = 2 * len(LOCH_S)
    best = None
    for n in range(8, 25, 2):
        f0 = C0 / (2 * math.pi) * math.sqrt(reihen * n * a1 / (vc * t_eff))
        if best is None or abs(f0 - f_ziel) < abs(best[1] - f_ziel):
            best = (n, f0)
    return best[0], best[1], vc * 1e3


# ---------------- Ausgabe ----------------
def schreibe_scad(r_t, werte):
    s, rr, lf, K = kontur(r_t)
    pkt = ", ".join(f"[{a:.3f}, {b:.3f}]" for a, b in zip(s, rr))
    z = [
        "// AUTOMATISCH ERZEUGT von rohr_aerodynamik.py – nicht von Hand aendern.",
        "// Innenkontur und Masse des Sanduhr-Bassreflexrohrs (mm).",
        f"rp_L = {L}; rp_platte = {PLATTE};",
        f"rp_rt = {r_t:.3f}; rp_rm = {R_MUND}; rp_trichter_l = {lf:.3f};",
        f"rp_wand = {ROHRWAND}; rp_r_zyl = {R_ZYL}; rp_r_fl = {R_FLANSCH}; rp_fl_h = {FLANSCH_H};",
        f"rp_r_land = {R_LAND}; rp_land_h = {LAND_H}; rp_muffe_ri = {MUFFE_RI}; rp_muffe_w = {MUFFE_W};",
        f"rp_nase = {NASE}; rp_loch_d = {LOCH_D}; rp_loch_s = [{LOCH_S[0]}, {LOCH_S[1]}]; rp_loch_n = {werte['loch_n']};",
        f"rp_fb = {werte['fb']:.2f}; rp_netto_l = {werte['netto']:.3f}; rp_vol_l = {werte['vol']:.3f};",
        f"rp_f_rohr = {werte['f_rohr']:.0f}; rp_f_falle = {werte['f_falle']:.0f}; rp_kc = {werte['kc']:.3f};",
        "// [s, r]: s = 0 Mund aussen (buendig mit der Rueckwand) ... s = rp_L Mund innen",
        f"rp_bohrung = [{pkt}];",
        "",
    ]
    (HIER / "rohr_profil.scad").write_text("\n".join(z), encoding="utf-8")


def bild(r_t, f, werte):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s, r, phi, fluid, h = f["s"], f["r"], f["phi"], f["fluid"], f["h"]
    us = np.zeros_like(phi); ur = np.zeros_like(phi)
    d = (phi[1:, :] - phi[:-1, :]) / h
    d[~(fluid[1:, :] & fluid[:-1, :])] = 0.0
    us[1:, :] += 0.5 * d; us[:-1, :] += 0.5 * d
    d = (phi[:, 1:] - phi[:, :-1]) / h
    d[~(fluid[:, 1:] & fluid[:, :-1])] = 0.0
    ur[:, 1:] += 0.5 * d; ur[:, :-1] += 0.5 * d
    v0 = f["Q"] / (math.pi * r_t**2)
    us, ur = -us / v0, ur / v0            # Bild: aussen rechts
    i0, i1 = np.searchsorted(s, -75), np.searchsorted(s, 235)
    j1 = np.searchsorted(r, 112)
    xs = -s[i0:i1][::-1]                  # Bildachse x = -s (Box links, aussen rechts)
    U = us[i0:i1, :j1][::-1, :]; V = ur[i0:i1, :j1][::-1, :]
    fl = fluid[i0:i1, :j1][::-1, :]
    betrag = np.where(fl, np.hypot(U, V), np.nan)
    yy = np.concatenate([-r[:j1][::-1], r[:j1]])
    B = np.concatenate([betrag[:, ::-1], betrag], axis=1).T
    UU = np.concatenate([U[:, ::-1], U], axis=1).T
    VV = np.concatenate([-V[:, ::-1], V], axis=1).T
    FL = np.concatenate([fl[:, ::-1], fl], axis=1).T

    fig, ax = plt.subplots(figsize=(12.5, 7.6), dpi=130)
    ax.set_facecolor("#c9a27a")
    im = ax.pcolormesh(xs, yy, np.clip(B, 0, 1.05), cmap="turbo", vmin=0, vmax=1.05, shading="auto")
    UUm = np.where(FL, UU, 0.0); VVm = np.where(FL, VV, 0.0)
    xr = np.linspace(xs[0], xs[-1], len(xs)); yr = np.linspace(yy[0], yy[-1], len(yy))
    start = np.array([[-228.0, y] for y in np.linspace(-105, 105, 25)]
                     + [[-150.0, y] for y in (-85, -70, 70, 85)])
    ax.streamplot(xr, yr, UUm, VVm, start_points=start, color="white", linewidth=0.8,
                  arrowstyle="-", density=6, broken_streamlines=False, integration_direction="forward")
    # Bauteile mit exakter Kontur darueberzeichnen (Holz hell, Druckteile dunkel)
    ks, kr, _, _ = kontur(r_t)
    sh = np.linspace(PLATTE, L, 600)
    for vz in (1, -1):
        ax.fill([0, 0, -PLATTE, -PLATTE], [vz * R_ZYL, vz * 200, vz * 200, vz * R_ZYL], color="#c9a27a", lw=0)
        px = np.concatenate([-ks, -sh[::-1], [-PLATTE, 0.0]])
        py = np.concatenate([kr, huelle(sh[::-1], r_t), [R_ZYL, R_ZYL]])
        ax.fill(px, vz * py, color="#2f3640", lw=0)
        s_a1 = PLATTE + FLANSCH_H + (R_FLANSCH - R_LAND) + LAND_H
        kx = np.linspace(s_a1, L - s_a1, 200)
        ky = np.maximum(r_t + ROHRWAND, R_LAND - np.minimum(kx - s_a1, (L - s_a1) - kx))
        ax.fill(np.concatenate([-kx, -kx[::-1]]), vz * np.concatenate([ky, np.full_like(kx, MUFFE_RI)]),
                color="#8a8f98", lw=0)
        for sl in (L / 2 - LOCH_S[1], L / 2 - LOCH_S[0], L / 2 + LOCH_S[0], L / 2 + LOCH_S[1]):
            ax.fill([-sl - LOCH_D / 2, -sl + LOCH_D / 2, -sl + LOCH_D / 2, -sl - LOCH_D / 2],
                    [vz * r_t, vz * r_t, vz * (r_t + ROHRWAND), vz * (r_t + ROHRWAND)], color="#8a8f98", lw=0)
    ax.set_xlim(xs[0], xs[-1]); ax.set_ylim(-112, 112); ax.set_aspect("equal")
    ax.set_xlabel("mm (0 = Außenfläche der Rückwand, links das Innere der Box)")
    ax.set_ylabel("mm")
    cb = fig.colorbar(im, ax=ax, shrink=0.86, pad=0.02)
    cb.set_label("Luftgeschwindigkeit, bezogen auf die Engstelle")
    ax.set_title(
        f"Strömung im Sanduhr-Rohr (reibungsfreie Rechnung) – Engstelle Ø {2 * r_t:.1f} mm, "
        f"Mund Ø {2 * R_MUND:.0f} mm, Länge {L:.0f} mm, Abstimmung {werte['fb']:.1f} Hz",
        fontsize=11)
    ax.annotate("Box innen", (-205, 98), color="white", fontsize=11, weight="bold")
    ax.annotate("außen", (40, 98), color="white", fontsize=11, weight="bold")
    ax.annotate("Rückwand", (-PLATTE / 2, -104), color="#3b2a1a", fontsize=9, ha="center", rotation=90, va="bottom")
    ax.annotate("Resonanzkammer (Wolle)", (-L / 2, 33.5), color="white", fontsize=8, ha="center")
    ax.annotate("Die Luft schwingt entlang der weißen Bahnen hin und her.", (-228, -108), color="white", fontsize=9)
    fig.tight_layout()
    fig.savefig(HIER / "stroemung.png")


def selbsttest():
    """Gerade Roehre Oe 50 x 100 mm, beidseitig buendig in einer Wand."""
    global PLATTE
    alt = PLATTE
    PLATTE = 100.0
    try:
        masse, _ = loese(lambda x: np.full_like(np.asarray(x, float), 25.0),
                         lambda x: np.full_like(np.asarray(x, float), 1e9), 100.0, 164.0)
    finally:
        PLATTE = alt
    l_eff = masse / 1000.0 * math.pi * 25.0**2
    print(f"Selbsttest: wirksame Laenge {l_eff:.1f} mm (Theorie: 100 + 21 aussen + ca. 17 innen = ca. 138 mm)")


def main():
    if "--selbsttest" in sys.argv:
        selbsttest()
        return
    # Engstelle so waehlen, dass die Zielfrequenz getroffen wird (Sekantenverfahren)
    a, b = 21.5, 23.5
    fa, fb_ = rechne(a)[0], rechne(b)[0]
    for _ in range(6):
        c = b + (ZIEL_FB - fb_) * (b - a) / (fb_ - fa)
        a, fa, b = b, fb_, c
        fb_ = rechne(b)[0]
        if abs(fb_ - ZIEL_FB) < 0.03:
            break
    r_t = round(b * 2) / 2           # auf 0,5 mm runden (exakt auf dem Rechengitter darstellbar)
    fb, masse, feld = rechne(r_t, felder=True)
    if "--fein" in sys.argv:         # Kontrolle mit halber Gitterweite (dauert einige Minuten)
        fb_f, masse_f = rechne(r_t, h=0.25)
        print(f"Kontrolle h = 0,25 mm: {fb_f:.2f} Hz (h = 0,5 mm: {fb:.2f} Hz)")
    s, rr, lf, K = kontur(r_t)
    xi_t = VD_CM3 * 1000.0 / (math.pi * r_t**2)
    f_rohr = rohrresonanz(r_t)
    n_loch, f_falle, vc_l = falle(r_t, f_rohr)
    v_max = 2 * math.pi * fb * xi_t / 1000.0
    werte = dict(fb=fb, netto=netto_l(r_t), vol=rohr_volumen_l(r_t), f_rohr=f_rohr, f_falle=f_falle,
                 loch_n=n_loch, kc=xi_t * r_t**2 / K)
    schreibe_scad(r_t, werte)
    bild(r_t, feld, werte)
    print(f"Engstelle            Oe {2 * r_t:.2f} mm")
    print(f"Mund                 Oe {2 * R_MUND:.0f} mm (Flaeche x {(R_MUND / r_t) ** 2:.2f})")
    print(f"Trichterlaenge       {lf:.1f} mm je Ende, gerades Stueck {L - 2 * lf:.1f} mm")
    print(f"Kruemmungsradius     {K / r_t**2:.1f} mm an der Engstelle ... {K / R_MUND**2:.1f} mm am Mund")
    print(f"Rohrvolumen in Box   {werte['vol']:.2f} L  -> Netto {werte['netto']:.2f} L")
    print(f"Akustische Masse     {masse:.1f} 1/m (2D-Rechnung), {masse_1d(r_t):.1f} 1/m (1D-Abschaetzung)")
    print(f"Abstimmung           {fb:.2f} Hz (2D), {fb_aus_masse(masse_1d(r_t), werte['netto']):.2f} Hz (1D)")
    print(f"Bei Vd = {VD_CM3:.0f} cm3:      Auslenkung {xi_t:.1f} mm, {v_max:.1f} m/s in der Engstelle, "
          f"{v_max * (r_t / R_MUND) ** 2:.1f} m/s am Mund")
    print(f"KC-Zahl              {werte['kc']:.2f} im ganzen Trichter (< 1 = Stroemung liegt an)")
    print(f"Rohrresonanz         ca. {f_rohr:.0f} Hz; Falle: 4 x {n_loch} Loecher Oe {LOCH_D} -> {f_falle:.0f} Hz, "
          f"Kammer {vc_l * 1000:.0f} cm3")


if __name__ == "__main__":
    main()
