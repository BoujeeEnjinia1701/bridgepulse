"""BridgePulse concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; not for fabrication.

Coordinates in mm. X along the span, Y across the bridge, Z up. The example host is a
7 m steel footbridge (two I-girders about 360 mm deep, timber deck, steel handrail) over
a small stream. The bridge is existing structure and carries no BOM number. The monitor
clusters at midspan: a sensor hub clamped to the south (-Y) girder, a strain gauge
half-bridge under each girder's bottom flange, two temperature probes and a FieldNode
core on the midspan handrail post where it gets sun.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cylinder, Pos, Rot, Solid, Plane, Vector
import concept
from concept import Part, render_all, human_figure

# ---------------- example host bridge (context, not in kit) ----------------
SPAN = 6800.0              # girder length, bearing to bearing about 6.4 m
GY = 600.0                 # girder centerline offset from bridge axis
G_D, G_B, G_TF, G_TW = 360.0, 170.0, 12.7, 8.0    # IPE 360 class section
G_Z0 = 1200.0              # underside of girders (top of abutments)
DECK_T, DECK_W = 50.0, 1500.0
DECK_Z0 = G_Z0 + G_D       # 1560
DECK_TOP = DECK_Z0 + DECK_T  # 1610
POST_H = 1100.0
POST_Y = -(DECK_W / 2 + 25)  # 50 mm square post against the deck edge
SEG = 800.0                # length of girder shown with the kit in the blueprint

STEEL = "#8A9299"
CONC = "#B8B2A7"
TIMBER = "#A47148"


def tube3(a, b, r):
    a = Vector(*a); b = Vector(*b); d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))


def i_girder(y, x0, x1):
    L = x1 - x0; xc = (x0 + x1) / 2
    bot = Pos(xc, y, G_Z0 + G_TF / 2) * Box(L, G_B, G_TF)
    top = Pos(xc, y, G_Z0 + G_D - G_TF / 2) * Box(L, G_B, G_TF)
    web = Pos(xc, y, G_Z0 + G_D / 2) * Box(L, G_TW, G_D - 2 * G_TF)
    return bot + top + web


def post(x, y):
    return Pos(x, y, DECK_Z0 + (POST_H + DECK_T) / 2) * Box(50, 50, POST_H + DECK_T)


H = SPAN / 2
girders_rest = (i_girder(-GY, -H, -SEG / 2) + i_girder(-GY, SEG / 2, H)
                + i_girder(GY, -H, -SEG / 2) + i_girder(GY, SEG / 2, H))
girders_mid = i_girder(-GY, -SEG / 2, SEG / 2) + i_girder(GY, -SEG / 2, SEG / 2)
deck = Pos(0, 0, DECK_Z0 + DECK_T / 2) * Box(SPAN, DECK_W, DECK_T)
rails = None
for s in (-1, 1):
    y = s * (DECK_W / 2 + 25)
    for x in (-3200, -1600, 1600, 3200):
        rails = post(x, y) if rails is None else rails + post(x, y)
    if s == 1:
        rails = rails + post(0, y)
    rails = rails + Pos(0, y, DECK_TOP + POST_H - 20) * Box(SPAN - 200, 60, 40)
    rails = rails + Pos(0, y, DECK_TOP + POST_H / 2) * Rot(0, 90, 0) * Cylinder(15, SPAN - 200)
mid_post = post(0, POST_Y)
abutments = (Pos(-H - 100, 0, G_Z0 / 2) * Box(1000, 2200, G_Z0)
             + Pos(H + 100, 0, G_Z0 / 2) * Box(1000, 2200, G_Z0))
banks = (Pos(-H - 1000, 0, G_Z0 / 2 - 100) * Box(1000, 3400, G_Z0 - 200)
         + Pos(H + 1000, 0, G_Z0 / 2 - 100) * Box(1000, 3400, G_Z0 - 200))
water = Pos(0, 0, 60) * Box(SPAN - 1200, 3400, 120)

# ---------------- BridgePulse monitor ----------------
WEB_FACE = -GY - G_TW / 2                     # outer face of the south girder web
# 4 Mounting plate against the web, held by two beam clamps on the bottom flange (no drilling)
plate = Pos(0, WEB_FACE - 3, G_Z0 + 170) * Box(260, 6, 260)
clamps = None
for x in (-100, 100):
    c = (Pos(x, -GY - G_B / 2 + 10, G_Z0 + 6) * Box(40, 50, 44)
         + Pos(x, WEB_FACE - 20, G_Z0 + 30) * Box(30, 34, 36))
    clamps = c if clamps is None else clamps + c
mount = plate + clamps

# 1 Sensor hub enclosure (die-cast aluminium, IP67), hollow so the cutaway shows the boards
HUB = (170.0, 64.0, 110.0)                    # along X, out from web (Y), height (Z)
HY = WEB_FACE - 6 - HUB[1] / 2
HZ = G_Z0 + 190
hub_shell = (Pos(0, HY, HZ) * Box(*HUB)
             - Pos(0, HY, HZ) * Box(HUB[0] - 8, HUB[1] - 8, HUB[2] - 8))
glands = (Pos(-50, HY, HZ - HUB[2] / 2 - 10) * Cylinder(9, 20)
          + Pos(50, HY, HZ - HUB[2] / 2 - 10) * Cylinder(9, 20)
          + Pos(0, HY - HUB[1] / 2 - 10, HZ + 20) * Rot(90, 0, 0) * Cylinder(9, 20))
hub = hub_shell + glands

# 2 Accelerometer board, bonded to the enclosure base (web side) for stiff coupling
acc = Pos(-62, WEB_FACE - 6 - 4 - 2, HZ + 15) * Box(40, 3, 40)
# 3 Signal board: 24-bit bridge ADC, MCU, microSD, on standoffs
sig = (Pos(28, HY - 10, HZ - 5) * Box(110, 2, 80)
       + Pos(-20, (WEB_FACE - 10 + HY - 10) / 2, HZ - 35) * Box(6, abs(WEB_FACE - 10 - HY + 10), 6)
       + Pos(65, (WEB_FACE - 10 + HY - 10) / 2, HZ - 35) * Box(6, abs(WEB_FACE - 10 - HY + 10), 6))

# 5 Strain gauge half-bridges under each bottom flange at midspan (protective cover patches)
gauges = (Pos(0, -GY, G_Z0 - 3) * Box(90, 45, 6) + Pos(0, GY, G_Z0 - 3) * Box(90, 45, 6))
# 6 Temperature probes: one on the steel web, one hanging in shaded air under the deck
temps = (Pos(260, WEB_FACE - 8, G_Z0 + 200) * Rot(90, 0, 0) * Cylinder(14, 16)
         + Pos(-300, -GY + 120, G_Z0 + 150) * Cylinder(6, 60)
         + tube3((-300, -GY + 120, G_Z0 + 180), (-300, -GY + 120, G_Z0 + G_D - G_TF), 2.5))

# 7 Sensor cables: far gauge across under the girders, near gauge, steel probe, and up to FieldNode
FN_Z = DECK_TOP + 620
CX = 60.0
cables = (tube3((-60, GY - 45, G_Z0 - 8), (-60, -GY + 45, G_Z0 - 8), 4)
          + tube3((-60, -GY + 45, G_Z0 - 8), (-60, HY, G_Z0 - 8), 4)
          + tube3((-60, HY, G_Z0 - 8), (-50, HY, HZ - HUB[2] / 2 - 20), 4)
          + tube3((180, WEB_FACE - 10, G_Z0 + 200), (85, WEB_FACE - 10, HZ + 10), 3)
          + tube3((0, HY - HUB[1] / 2 - 20, HZ + 20), (CX, POST_Y - 50, HZ + 20), 4)
          + tube3((CX, POST_Y - 50, HZ + 20), (CX, POST_Y - 50, FN_Z - 70), 4)
          + tube3((CX, POST_Y - 50, FN_Z - 70), (20, POST_Y - 70, FN_Z - 70), 4))

# 8 FieldNode core on the midspan post: IP65 enclosure, 6 W panel as a sun hood, pole clamps
FN = (180.0, 90.0, 130.0)
fn_y = POST_Y - 25 - FN[1] / 2 - 10
fn_box = Pos(0, fn_y, FN_Z) * Box(*FN)
fn_clamps = (Pos(0, POST_Y, FN_Z + 40) * Box(80, 80, 20) + Pos(0, POST_Y, FN_Z - 40) * Box(80, 80, 20)
             + Pos(0, POST_Y - 32, FN_Z) * Box(80, 12, 120))
panel = Pos(0, fn_y - 20, FN_Z + FN[2] / 2 + 70) * Rot(-30, 0, 0) * Box(280, 200, 18)
panel_arm = (tube3((-100, POST_Y - 30, FN_Z + 45), (-100, fn_y - 20, FN_Z + FN[2] / 2 + 60), 6)
             + tube3((100, POST_Y - 30, FN_Z + 45), (100, fn_y - 20, FN_Z + FN[2] / 2 + 60), 6))
fieldnode = fn_box + fn_clamps + panel + panel_arm

parts = [
    Part("Existing girders and post at midspan (not in kit)", girders_mid + mid_post, STEEL, None),
    Part("Sensor hub enclosure, IP67 die-cast", hub, "#CBD5E1", 1, (0, -380, 0)),
    Part("Accelerometer board, ADXL355", acc, "#0F766E", 2, (-250, -420, 260)),
    Part("Signal board: 24-bit ADC, MCU, microSD", sig, "#2563EB", 3, (250, -700, 60)),
    Part("Mounting plate and beam clamps", mount, "#D4A017", 4, (0, -120, -330)),
    Part("Strain gauge half-bridges (2)", gauges, "#C2410C", 5, (0, 0, -260)),
    Part("Temperature probes (2)", temps, "#7C3AED", 6, (420, -220, -40)),
    Part("Sensor cables, M12, shielded", cables, "#111827", 7, (0, 0, 0)),
    Part("FieldNode core (6 W panel, cell, radio)", fieldnode, "#115E59", 8, (700, -150, 150)),
]

context = [
    Part("Example 7 m steel footbridge", girders_rest + deck + rails + abutments, "#9CA3AF"),
    Part("banks", banks, "#B9B2A4"),
    Part("stream", water, "#A9C4DC"),
    human_figure(1750.0, x=-1900.0, y=150.0, z=DECK_TOP),
]
context[3].name = "1.75 m person"

outs = render_all(
    parts, project="BridgePulse", title="Footbridge monitor concept", dwg_no="BRP-DWG-010",
    key_figures=["3-axis MEMS accelerometer (22.5 µg/√Hz), 2 strain half-bridges, 2 temperatures",
                 "10 min record every hour at 250 Hz; about 15 mW average (estimate)",
                 "About 0.015 Hz spectral resolution; 1 % frequency shift target (unverified)",
                 "Clamp-on mounting; no drilling or welding of the structure",
                 "About $342 in parts incl. FieldNode; $216 BridgePulse-specific (indicative)"],
    scale_figure=False, context=context, cut=False,
    flow={"title": "hourly data flow (estimates)", "unit": "GB/month",
          "stages": [("Bridge response", "accel, strain, temp"), ("Sensor hub", "10 min each hour"),
                     ("Features", "about 36 B per hour"), ("FieldNode", "hourly LoRaWAN uplink"),
                     ("TwinKit or CityTwin", "trend, band, alert"), ("Bridge owner", "targeted inspection")],
          "losses": [(1, "Raw record kept on microSD (est.)", 1.4)]},
)

# Cutaway of the sensor hub only (the inside of the hub is what matters; a whole-assembly
# section would cut the hub away). Section plane through the hub, looking from the -Y side.
hub_parts = [p for p in parts if p.bom in (1, 2, 3)] + [
    Part("Mounting plate and clamps (item 4)", mount, "#D4A017", None),
    Part("Girder web and bottom flange (existing)",
         Pos(0, -GY, G_Z0 + G_D / 2) * Box(360, G_TW, G_D - 2 * G_TF)
         + Pos(0, -GY, G_Z0 + G_TF / 2) * Box(360, G_B, G_TF), STEEL, None)]
from build123d import Box as _Box
cutter = Pos(0, HY - 18 + 5000, 0) * _Box(10000, 10000, 10000)   # keep everything behind the outer wall
cut = [Part(p.name, p.shape & cutter, p.color, p.bom) for p in hub_parts]
concept._render(cut, Path("media") / "cutaway.png", azim=-115, elev=20, labels=True,
                title="BridgePulse: sensor hub cutaway")

import shutil
for d in Path("media").glob("_views*"):
    shutil.rmtree(d, ignore_errors=True)
print(outs)
