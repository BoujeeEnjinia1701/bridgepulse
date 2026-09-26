"""BridgePulse concept media (TRL 3), built from the parametric model in cad/src/model.py.

Run from the repo root:  python cad/src/concept_media.py
Proportions, interfaces and main parts; not for fabrication.

Coordinates in mm, as in model.py: X along the span, Y across the bridge, Z up. The example host
is a 7 m steel footbridge (two IPE 360 class girders, timber deck, steel handrail) over a small
stream; the bridge is existing structure and carries no BOM number. The monitor clusters at
midspan: the sensor hub on its plate between the flanges of the south (-Y) girder, a strain gauge
half-bridge under each girder, two temperature probes and a FieldNode core on the outboard face
of the midspan handrail post. BOM item 9 (the microSD card) sits inside item 3 and has no part.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from build123d import Box, Cylinder, Pos, Rot  # noqa: E402
import concept  # noqa: E402
from concept import Part, render_all, human_figure  # noqa: E402
from model import PARAMS as P, derived, build_parts, bridge_context, i_girder, box, BOM_NAMES  # noqa: E402

D = derived(P)
S = build_parts(P)
STEEL, TIMBER = "#8A9299", "#A47148"
H = P["span"] / 2
z0 = P["g_z0"]

# ---------------- example host bridge (context) ----------------
ctx_full = bridge_context(P, full=True)
girders_rest = (i_girder(P, -P["gy"], -H, -P["seg"] / 2) + i_girder(P, -P["gy"], P["seg"] / 2, H)
                + i_girder(P, P["gy"], -H, -P["seg"] / 2) + i_girder(P, P["gy"], P["seg"] / 2, H))
seg = bridge_context(P)
mid_girders = seg["girders"]
post_mid = seg["post"]
s_ = P["post"][0]
rails = None
for sgn in (-1, 1):
    y = sgn * (P["deck"][1] / 2 + s_ / 2)
    for x in (-3200, -1600, 1600, 3200) + ((0,) if sgn == 1 else ()):
        pz = D["deck_z0"] + (P["post"][2] + P["deck"][0]) / 2
        p_ = Pos(x, y, pz) * Box(s_, s_, P["post"][2] + P["deck"][0])
        rails = p_ if rails is None else rails + p_
    rails = rails + Pos(0, y, D["post_top"] - 20) * Box(P["span"] - 200, 60, 40)
    rails = rails + Pos(0, y, D["deck_top"] + P["post"][2] / 2) * Rot(0, 90, 0) * Cylinder(15, P["span"] - 200)
abutments = (Pos(-H - 100, 0, z0 / 2) * Box(1000, 2200, z0) + Pos(H + 100, 0, z0 / 2) * Box(1000, 2200, z0))
banks = (Pos(-H - 1000, 0, z0 / 2 - 100) * Box(1000, 3400, z0 - 200) + Pos(H + 1000, 0, z0 / 2 - 100) * Box(1000, 3400, z0 - 200))
water = Pos(0, 0, 60) * Box(P["span"] - 1200, 3400, 120)

COL = {"hub": "#CBD5E1", "acc": "#0F766E", "sig": "#2563EB", "mount": "#D4A017", "gauges": "#C2410C",
       "temps": "#7C3AED", "cables": "#111827", "fieldnode": "#115E59"}
EXP = {"hub": (0, -420, 0), "acc": (-140, -480, 220), "sig": (260, -760, 80), "mount": (0, -150, -360),
       "gauges": (0, 0, -300), "temps": (430, -240, -40), "cables": (0, 0, 0), "fieldnode": (700, -200, 200)}

parts = [Part("Existing girders and post at midspan (not in kit)", mid_girders + post_mid, STEEL, None)]
for k, (n, name) in BOM_NAMES.items():
    parts.append(Part(name, S[k], COL[k], n, EXP[k]))

context = [
    Part("Example 7 m steel footbridge", girders_rest + ctx_full["deck"] + rails + abutments, "#9CA3AF"),
    Part("banks", banks, "#B9B2A4"),
    Part("stream", water, "#A9C4DC"),
    human_figure(1750.0, x=-1900.0, y=150.0, z=D["deck_top"]),
]
context[3].name = "1.75 m person"

outs = render_all(
    parts, project="BridgePulse", title="Footbridge monitor concept", dwg_no="BRP-DWG-010",
    key_figures=["3-axis MEMS accelerometer (22.5 µg/√Hz), 2 strain half-bridges, 2 temperatures",
                 "10 min record each hour at 250 Hz; 16.9 mW average at the port (BRP-CAL-001)",
                 "Example 7 m span: first mode 23.9 Hz; 0.05 % scatter at 100 µg (curve fit)",
                 "Hub between the flanges; 10 mm below the soffit at most; no drilling",
                 "$244 BridgePulse-specific parts; $370 with the FieldNode core"],
    scale_figure=False, context=context, cut=False,
    flow={"title": "hourly data flow (estimates)", "unit": "GB/month",
          "stages": [("Bridge response", "accel, strain, temp"), ("Sensor hub", "10 min each hour"),
                     ("Features", "36 B per hour"), ("FieldNode", "hourly LoRaWAN uplink"),
                     ("TwinKit or CityTwin", "trend, band, alert"), ("Bridge owner", "targeted inspection")],
          "losses": [(1, "Raw record kept on microSD (est.)", 1.39)]},
)

# Cutaway of the sensor hub: section plane through the hub, looking from the -Y side, with the
# girder segment behind it. The kit's own cutaway cuts at the mean Y of all parts, which would miss
# the hub, so this view is made here.
hub_y = (D["hub_y0"] + D["hub_y1"]) / 2
hub_parts = [p for p in parts if p.bom in (1, 2, 3, 4)] + [
    Part("Girder web and flanges (existing)", i_girder(P, -P["gy"], -180, 180), STEEL, None)]
cutter = Pos(0, hub_y + 5000, 0) * Box(10000, 10000, 10000)
cut = []
for p in hub_parts:
    c = p.shape & cutter
    if c.volume > 1e-6:
        cut.append(Part(p.name, c, p.color, p.bom))
concept._render(cut, ROOT / "media" / "cutaway.png", azim=-115, elev=18, labels=True,
                title="BridgePulse: sensor hub cutaway")

for d in (ROOT / "media").glob("_views*"):
    shutil.rmtree(d, ignore_errors=True)
print(outs)
