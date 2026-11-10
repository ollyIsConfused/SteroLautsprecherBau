// Lautsprecherbox (Stereo-Paar, 2 Stueck) – Buche 18 mm
// 40 x 30 x 25 cm, 2-Wege: Tieftoener Oe 18 cm + Hochtoener, Sanduhr-Bassreflexrohr hinten
// Einheiten: mm.  Koordinaten (Box "links", von vorne gesehen):
//   x = Breite (links -> rechts), y = Tiefe (Front bei y = 0), z = Hoehe (Boden bei z = 0)
// Box "rechts" ist das Spiegelbild: Hochtoener sitzen bei beiden Boxen innen (zur Mitte).
//
// Ansichten (oben bei "ansicht" umstellen oder per Kommandozeile -D):
//   "zusammenbau" – eine fertige Box (welche: siehe "box")
//   "paar"        – beide Boxen nebeneinander, wie sie aufgestellt werden
//   "schnitt"     – Blick ins Innere (Deckel + eine Seite ausgeblendet)
//   "explosion"   – alle Holzteile auseinandergezogen
//   "rohr_aussen" / "rohr_innen" / "rohr_muffe" – die 3 Druckteile des Rohrs (STL exportieren)
//   "rohr_schnitt" – das zusammengesetzte Rohr, aufgeschnitten
//   "front" / "rueckwand" / "strebe" – Platten flach (2D) zum Anzeichnen

ansicht = "zusammenbau";
box     = "links";      // "links" oder "rechts" (Spiegelbild)

// Innenkontur + Masse des Rohrs, berechnet von rohr_aerodynamik.py
include <rohr_profil.scad>

$fn = 96;

// ---------- Aussenmasse ----------
breite = 400;
tiefe  = 300;
hoehe  = 250;
wand   = 18;     // Buche-Multiplex 18 mm (oder Buche-Leimholz 18 mm)

// ---------- Tieftoener ----------
chassis_d     = 180;   // Korb aussen
ausschnitt_d  = 155;   // Einbauausschnitt
fase          = 10;    // 45-Grad-Fase hinten am Ausschnitt (Membran "atmet" frei)
chassis_x     = 150;
chassis_z     = hoehe / 2;
chassis_tiefe = 85;    // nur Vorschau/Kollisionscheck

// ---------- Hochtoener (innen, zur Mitte des Paares) ----------
ht_ausschnitt_d = 30.2;  // aus Skizze -> VOR DEM BOHREN mit Datenblatt pruefen!
ht_flansch_d    = 60;    // nur Vorschau
ht_tiefe        = 40;    // nur Vorschau
ht_x            = 300;
ht_z            = hoehe / 2;

// ---------- Bassreflexrohr: Sanduhr-Rohr aus 3 Druckteilen ----------
// Kontur, Laenge und Durchmesser stehen in rohr_profil.scad (Werte rp_...).
// Das Rohr wird von INNEN in die Rueckwand gesetzt und schliesst aussen buendig ab.
rohr_x        = breite / 2;  // genau mittig = Druckknoten der Breiten-Mode
rohr_z        = hoehe / 2;   // genau mittig = Druckknoten der Hoehen-Mode
loch_rohr_d   = 102;         // Loch in der Rueckwand (Lochsaege 102 mm)
rp_schraube_r = 57.5;        // Lochkreis der 4 Schrauben im Flansch
// s-Koordinate entlang des Rohrs: 0 = Aussenflaeche Rueckwand, rp_L = Mund innen
rp_mitte = rp_L / 2;                               // Trennebene der beiden Trichterteile
rp_r_tw  = rp_rt + rp_wand;                        // Aussenradius im geraden Teil
rp_s_fl  = rp_platte + rp_fl_h;                    // Flansch endet hier
rp_s_la0 = rp_s_fl + (rp_r_fl - rp_r_land);        // Muffensitz Aussenteil: von ...
rp_s_la1 = rp_s_la0 + rp_land_h;                   // ... bis
rp_s_ka  = rp_s_la1 + (rp_r_land - rp_r_tw);       // 45-Grad-Kegel laeuft in die Rohrwand aus
rp_s_lb0 = rp_L - rp_s_la1;                        // Muffensitz Innenteil: von ...
rp_s_lb1 = rp_L - rp_s_la0;                        // ... bis
rp_s_kb  = rp_s_lb0 - (rp_r_land - rp_r_tw);
rp_s_tp  = rp_L - rp_nase - rp_nase * sin(45);     // Lippe geht hier in den 45-Grad-Kegel ueber
rp_r_tp  = rp_rm + rp_nase * cos(45);
rp_r_abs = rp_r_tp - (rp_s_tp - rp_s_lb1);

// ---------- Kabeldurchfuehrung (Rueckwand) ----------
kabel_d   = 12;    // fuer Kabelverschraubung M12 (dichtet + Zugentlastung)
kabel_x   = 340;   // innen-seitig (zur Mitte des Paares, dort steht meist der Verstaerker)
kabel_z   = 50;

// ---------- Versteifung ----------
strebe_y      = 121;   // Fensterstrebe: Vorderkante (ab Aussenfront)
strebe_rahmen = 30;    // Stegbreite des Rahmens
strebe_r      = 20;    // Eckradius des Fensters (stroemungsguenstig)
stab_d        = 20;    // Rundstab Buche Front <-> Rueckwand
stab_x        = 255;
stab_z        = 70;

// ---------- Frequenzweiche (nur Vorschau) ----------
weiche     = [100, 70, 25];
weiche_pos = [245, 195];   // x, y (liegt auf dem Boden, nahe Kabeleingang)

// ---------- Daempfung (nur Vorschau) ----------
daempf = 20;   // Dicke Polyesterwatte / Schafwolle

// ---------- abgeleitete Masse ----------
innen   = [breite - 2 * wand, tiefe - 2 * wand, hoehe - 2 * wand];
seite   = [tiefe, hoehe - 2 * wand];
frontrk = [breite - 2 * wand, hoehe - 2 * wand];
deckel  = [breite, tiefe];
fenster = [innen[0] - 2 * strebe_rahmen, innen[2] - 2 * strebe_rahmen];

buche   = [0.85, 0.66, 0.47];
kante   = [0.80, 0.60, 0.42];
schwarz = [0.12, 0.12, 0.12];
watte   = [0.93, 0.90, 0.82];

// ---------- Hilfen ----------
function enthalten(t, liste) = len([for (x = liste) if (x == t) x]) > 0;

module rund_rechteck(g, r) {
    hull() for (x = [r, g[0] - r], y = [r, g[1] - r]) translate([x, y]) circle(r = r);
}
module bohrung_y(x, z, d, y0 = -1, h = wand + 2) {
    translate([x, y0, z]) rotate([-90, 0, 0]) cylinder(d = d, h = h);
}

// ---------- Holzteile ----------
module boden()  { cube([breite, tiefe, wand]); }
module deckel() { translate([0, 0, hoehe - wand]) cube([breite, tiefe, wand]); }
module seite_links()  { translate([0, 0, wand]) cube([wand, tiefe, innen[2]]); }
module seite_rechts() { translate([breite - wand, 0, wand]) cube([wand, tiefe, innen[2]]); }

module front() {
    difference() {
        translate([wand, 0, wand]) cube([innen[0], wand, innen[2]]);
        bohrung_y(chassis_x, chassis_z, ausschnitt_d);
        // 45-Grad-Fase auf der Innenseite
        translate([chassis_x, wand - fase, chassis_z]) rotate([-90, 0, 0])
            cylinder(d1 = ausschnitt_d, d2 = ausschnitt_d + 2 * fase + 0.02, h = fase + 0.01);
        bohrung_y(ht_x, ht_z, ht_ausschnitt_d);
    }
}

module rueckwand() {
    difference() {
        translate([wand, tiefe - wand, wand]) cube([innen[0], wand, innen[2]]);
        bohrung_y(rohr_x,  rohr_z,  loch_rohr_d, tiefe - wand - 1);
        bohrung_y(kabel_x, kabel_z, kabel_d,     tiefe - wand - 1);
    }
}

// Fensterstrebe: verbindet Deckel, Boden und beide Seiten, ~60 % offen
module fensterstrebe() {
    translate([wand, strebe_y + wand, wand]) rotate([90, 0, 0])
        linear_extrude(wand) difference() {
            square([innen[0], innen[2]]);
            translate([strebe_rahmen, strebe_rahmen]) rund_rechteck(fenster, strebe_r);
        }
}

// Rundstab: koppelt Front und Rueckwand (die beiden groessten freien Flaechen)
module stab() { bohrung_y(stab_x, stab_z, stab_d, wand, innen[1]); }

// ---------- Druckteile des Rohrs ----------
// Alle drei Teile drucken ohne Stuetzen: keine Flaeche haengt mehr als 45 Grad ueber.
// Die Trichter stehen beim Druck wie eine Schale nach oben offen, so wird die
// stroemungswichtige Innenflaeche sauber.

// Querschnitt Aussentrichter als [r, s]
module rp_kontur_aussen() {
    polygon(concat(
        [for (p = rp_bohrung) if (p[0] <= rp_mitte + 0.001) [p[1], p[0]]],
        [[rp_r_tw, rp_mitte], [rp_r_tw, rp_s_ka], [rp_r_land, rp_s_la1], [rp_r_land, rp_s_la0],
         [rp_r_fl, rp_s_fl], [rp_r_fl, rp_platte], [rp_r_zyl, rp_platte], [rp_r_zyl, 0.5],
         [rp_r_zyl - 0.5, 0]]));
}

// Querschnitt Innentrichter als [r, s]: Kontur, eingerollte Lippe, 45-Grad-Kegel, Muffensitz
module rp_kontur_innen() {
    polygon(concat(
        [for (p = rp_bohrung) if (p[0] >= rp_mitte - 0.001) [p[1], p[0]]],
        [for (a = [5 : 5 : 135]) [rp_rm + rp_nase * sin(a), rp_L - rp_nase + rp_nase * cos(a)]],
        rp_r_abs >= rp_r_tw
            ? [[rp_r_abs, rp_s_lb1]]
            : [[rp_r_tw, rp_s_tp - (rp_r_tp - rp_r_tw)], [rp_r_tw, rp_s_lb1]],
        [[rp_r_land, rp_s_lb1], [rp_r_land, rp_s_lb0], [rp_r_tw, rp_s_kb], [rp_r_tw, rp_mitte]]));
}

// Loecher der Resonanzfalle: seite = -1 Aussenteil, +1 Innenteil (Reihen versetzt)
module rp_falle_loecher(seite) {
    for (k = [0 : len(rp_loch_s) - 1], i = [0 : rp_loch_n - 1])
        rotate([0, 0, (i + 0.5 * k) * 360 / rp_loch_n])
            translate([0, 0, rp_mitte + seite * rp_loch_s[k]]) rotate([0, 90, 0])
                cylinder(d = rp_loch_d, h = rp_r_tw + 1, $fn = 16);
}

// 4 Senkkopfschrauben 3,5 x 16 durch den Flansch in die Rueckwand (von innen)
module rp_schraubloecher() {
    for (w = [45 : 90 : 315]) rotate([0, 0, w]) translate([rp_schraube_r, 0, 0]) {
        translate([0, 0, rp_platte - 1]) cylinder(d = 3.8, h = 12, $fn = 24);
        translate([0, 0, rp_platte + 2.6]) cylinder(d1 = 3.8, d2 = 7.6, h = 1.9, $fn = 24);
        translate([0, 0, rp_platte + 4.49]) cylinder(d = 7.6, h = 30, $fn = 24);
    }
}

// Teile in Einbaulage (z = s)
module rohr_aussen_s() {
    difference() {
        rotate_extrude($fn = 180) rp_kontur_aussen();
        rp_falle_loecher(-1);
        rp_schraubloecher();
    }
}
module rohr_innen_s() {
    difference() {
        rotate_extrude($fn = 180) rp_kontur_innen();
        rp_falle_loecher(1);
    }
}
module rohr_muffe_s() {
    translate([0, 0, rp_s_la0]) difference() {
        cylinder(r = rp_muffe_ri + rp_muffe_w, h = rp_s_lb1 - rp_s_la0, $fn = 180);
        translate([0, 0, -1]) cylinder(r = rp_muffe_ri, h = rp_s_lb1 - rp_s_la0 + 2, $fn = 180);
    }
}

// Teile in Drucklage (Trennebene bzw. Muffenende auf dem Druckbett)
module rohr_aussen() { translate([0, 0, rp_mitte]) mirror([0, 0, 1]) rohr_aussen_s(); }
module rohr_innen()  { translate([0, 0, -rp_mitte]) rohr_innen_s(); }
module rohr_muffe()  { translate([0, 0, -rp_s_la0]) rohr_muffe_s(); }

module rohr_komplett_s() {
    color([0.20, 0.20, 0.22]) rohr_aussen_s();
    color([0.24, 0.30, 0.40]) rohr_innen_s();
    color([0.62, 0.62, 0.65]) rohr_muffe_s();
}

// ---------- Vorschau-Teile ----------
module tieftoener() {
    color(schwarz) translate([chassis_x, 0, chassis_z]) rotate([90, 0, 0]) {
        difference() {
            cylinder(d = chassis_d, h = 6);
            translate([0, 0, 2]) cylinder(d1 = chassis_d - 40, d2 = chassis_d - 24, h = 5);
        }
        color([0.3, 0.3, 0.3]) translate([0, 0, 1]) sphere(d = 45);
        mirror([0, 0, 1]) cylinder(d1 = ausschnitt_d - 4, d2 = 70, h = chassis_tiefe - 30);
        mirror([0, 0, 1]) translate([0, 0, chassis_tiefe - 35]) cylinder(d = 100, h = 35);
    }
}

module hochtoener() {
    translate([ht_x, 0, ht_z]) rotate([90, 0, 0]) {
        color(schwarz) cylinder(d = ht_flansch_d, h = 4);
        color([0.35, 0.35, 0.38]) translate([0, 0, 4]) scale([1, 1, 0.5]) sphere(d = 26);
        color(schwarz) mirror([0, 0, 1]) cylinder(d = ht_ausschnitt_d - 1, h = ht_tiefe);
    }
}

module rohr_eingebaut() {
    translate([rohr_x, tiefe, rohr_z]) rotate([90, 0, 0]) rohr_komplett_s();
}

module weiche_platine() {
    translate([weiche_pos[0], weiche_pos[1], wand]) {
        color([0.1, 0.45, 0.2]) cube([weiche[0], weiche[1], 2]);
        color([0.85, 0.75, 0.2]) translate([15, 15, 2]) cylinder(d = 18, h = 22);
        color([0.6, 0.35, 0.15]) translate([60, 35, 2]) cylinder(d = 35, h = 18);
    }
}

// Daempfung: Rueckwand, Deckel und eine Seite – NICHT vor dem Rohrmund
module daempfung(mit_deckel = true) {
    color(watte) {
        // Rueckwand (Aussparungen fuer Rohr und Stab, unten frei fuer die Weiche)
        difference() {
            translate([wand, tiefe - wand - daempf, wand + weiche[2] + 5])
                cube([innen[0], daempf, innen[2] - weiche[2] - 5]);
            bohrung_y(rohr_x, rohr_z, 2 * rp_r_fl + 10, tiefe - wand - daempf - 1, daempf + 2);
            bohrung_y(stab_x, stab_z, stab_d + 4,      tiefe - wand - daempf - 1, daempf + 2);
        }
        // Deckel (vor und hinter der Strebe)
        if (mit_deckel) for (s = [[wand, strebe_y], [strebe_y + wand, tiefe - wand - daempf]])
            translate([wand, s[0], hoehe - wand - daempf]) cube([innen[0], s[1] - s[0], daempf]);
        // linke Seite (vor und hinter der Strebe)
        for (s = [[wand, strebe_y], [strebe_y + wand, tiefe - wand - daempf]])
            translate([wand, s[0], wand]) cube([daempf, s[1] - s[0], innen[2] - (mit_deckel ? daempf : 0)]);
    }
}

// ---------- Zusammenbau ----------
module holz(ohne = []) {
    if (!enthalten("boden", ohne))        color(buche) boden();
    if (!enthalten("deckel", ohne))       color(buche) deckel();
    if (!enthalten("seite_links", ohne))  color(kante) seite_links();
    if (!enthalten("seite_rechts", ohne)) color(kante) seite_rechts();
    if (!enthalten("front", ohne))        color(buche * 0.97) front();
    if (!enthalten("rueckwand", ohne))    color(buche * 0.97) rueckwand();
    if (!enthalten("strebe", ohne))       color([0.78, 0.55, 0.36]) fensterstrebe();
    if (!enthalten("stab", ohne))         color([0.70, 0.48, 0.30]) stab();
}

module box_links(ohne = [], innenleben = false) {
    holz(ohne);
    tieftoener();
    hochtoener();
    rohr_eingebaut();
    if (innenleben) { weiche_platine(); daempfung(mit_deckel = !enthalten("deckel", ohne)); }
}

module eine_box(welche = box, ohne = [], innenleben = false) {
    if (welche == "rechts") translate([breite, 0, 0]) mirror([1, 0, 0]) box_links(ohne, innenleben);
    else box_links(ohne, innenleben);
}

module explosion(a = 120) {
    color(buche) translate([0, 0, -a]) boden();
    color(buche) translate([0, 0, a]) deckel();
    color(kante) translate([-a, 0, 0]) seite_links();
    color(kante) translate([a, 0, 0]) seite_rechts();
    color(buche * 0.97) translate([0, -a, 0]) front();
    color(buche * 0.97) translate([0, a, 0]) rueckwand();
    color([0.78, 0.55, 0.36]) fensterstrebe();
    color([0.70, 0.48, 0.30]) translate([0, 0, -a / 2]) stab();
}

// ---------- Ausgabe ----------
if (ansicht == "zusammenbau") eine_box();
else if (ansicht == "paar") { eine_box("links"); translate([breite + 250, 0, 0]) eine_box("rechts"); }
else if (ansicht == "schnitt") eine_box(box, ["deckel", "seite_rechts"], true);
else if (ansicht == "explosion") explosion();
else if (ansicht == "rohr_aussen") rohr_aussen();
else if (ansicht == "rohr_innen") rohr_innen();
else if (ansicht == "rohr_muffe") rohr_muffe();
else if (ansicht == "rohr_schnitt")
    difference() { rohr_komplett_s(); translate([-100, 0, -5]) cube([200, 100, rp_L + 20]); }
else if (ansicht == "front")
    projection() rotate([-90, 0, 0]) translate([-wand, 0, -wand]) front();
else if (ansicht == "rueckwand")
    // von hinten gesehen; Ursprung = linke untere Ecke der Platte (von hinten)
    projection() mirror([1, 0, 0]) rotate([-90, 0, 0]) translate([-(breite - wand), -tiefe, -wand]) rueckwand();
else if (ansicht == "strebe")
    projection() rotate([-90, 0, 0]) translate([-wand, -strebe_y, -wand]) fensterstrebe();

// ---------- Zuschnittliste + Volumen + Abstimmung (Konsole) ----------
brutto_l = innen[0] * innen[1] * innen[2] / 1e6;
strebe_l = (innen[0] * innen[2] - fenster[0] * fenster[1]) * wand / 1e6;
abzug_l  = 1.0                                              // Tieftoener
         + rp_vol_l                                         // Rohr (aus rohr_aerodynamik.py)
         + strebe_l
         + PI * pow(stab_d / 2, 2) * innen[1] / 1e6
         + PI * pow(ht_ausschnitt_d / 2, 2) * ht_tiefe / 1e6
         + weiche[0] * weiche[1] * weiche[2] / 1e6 * 0.6;
netto_l  = brutto_l - abzug_l;

if (wand != rp_platte) echo("ACHTUNG: Plattenstaerke geaendert -> rohr_aerodynamik.py (PLATTE) anpassen und neu rechnen");
if (abs(netto_l - rp_netto_l) > 0.3) echo("ACHTUNG: Volumen geaendert -> rohr_aerodynamik.py neu rechnen");

echo(str("ZUSCHNITT (fuer 2 Boxen)  4x Deckel/Boden  ", deckel[0], " x ", deckel[1], " mm"));
echo(str("ZUSCHNITT (fuer 2 Boxen)  4x Seiten        ", seite[0], " x ", seite[1], " mm"));
echo(str("ZUSCHNITT (fuer 2 Boxen)  4x Front/Rueck   ", frontrk[0], " x ", frontrk[1], " mm"));
echo(str("ZUSCHNITT (fuer 2 Boxen)  2x Fensterstrebe ", frontrk[0], " x ", frontrk[1], " mm, Fenster ",
         fenster[0], " x ", fenster[1], " R", strebe_r));
echo(str("ZUSCHNITT (fuer 2 Boxen)  2x Rundstab Oe ", stab_d, " x ", innen[1], " mm"));
echo(str("VOLUMEN    brutto ", brutto_l, " L, netto ca. ", netto_l, " L"));
echo(str("ROHR       Engstelle Oe ", 2 * rp_rt, ", Mund Oe ", 2 * rp_rm, ", Laenge ", rp_L,
         " mm, Trichter je ", rp_trichter_l, " mm"));
echo(str("ABSTIMMUNG Bassreflex ca. ", rp_fb, " Hz (2D-Stroemungsrechnung, rohr_aerodynamik.py)"));
echo(str("FALLE      Rohrresonanz ca. ", rp_f_rohr, " Hz, Absorber 4 x ", rp_loch_n, " Loecher -> ", rp_f_falle, " Hz"));
echo(str("MODEN      Breite ", round(343000 / (2 * innen[0])), " Hz, Tiefe ", round(343000 / (2 * innen[1])),
         " Hz, Hoehe ", round(343000 / (2 * innen[2])), " Hz"));
