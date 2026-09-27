"""BridgePulse parametric model (build123d), TRL 3, massing-plus level of detail.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    bridgepulse-assembly.step / .stl   the monitor (BOM items 1 to 9) as installed, no bridge
    sensor-hub.step / .stl             hub enclosure, boards, mounting plate, jack screw and clamps
    bridgepulse-installed.step / .stl  the monitor on an 800 mm midspan segment of the example bridge

Axes as in cad/src/concept_media.py: X along the span (midspan at x = 0), Y across the bridge
(the monitored girder and the FieldNode post are on -Y), Z up, with the underside of the girders
(the soffit) at z = g_z0. The example host is a 7 m steel footbridge on two IPE 360 class girders
with a timber deck. The bridge is existing structure and carries no BOM number.

Mounting (TRL 3 change, see BRP-CAL-001 section H): the hub sits on an aluminium plate that stands
on the bottom flange against the outer face of the web and is wedged against the underside of the
top flange by a jack screw, with two clamps holding its foot to the bottom flange tip. The hub is
inside the flange outline, so nothing but the clamp jaws, the gauge covers and one cable crossing
lies below the soffit. Nothing is drilled or welded into the structure.

Main dimensions and interfaces only; not fabrication detail; not for fabrication. The same PARAMS
feed docs/04-calcs/sizing.py (BRP-CAL-001) and drawing BRP-DWG-001 (cad/src/sheets.py). FieldNode
dimensions are copied from the FieldNode repo (cad/src/model.py, TRL 3) and are owned there.
"""
import math
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # example host bridge (context, not in the BOM)
    "span": 6800.0, "bearing_span": 6400.0,
    "gy": 600.0,                                  # girder centerline offset from the bridge axis
    "girder": (360.0, 170.0, 12.7, 8.0),          # depth, flange width, flange thickness, web thickness
    "g_z0": 1200.0,                               # soffit (underside of girders)
    "deck": (50.0, 1500.0),                       # timber deck thickness, width
    "post": (50.0, 3.0, 1100.0),                  # square hollow handrail post: size, wall, height above deck
    "seg": 800.0,                                 # girder length shown in the installed model and drawing
    # 1 sensor hub enclosure, die-cast aluminium, IP67: along X, out from the plate (Y), height (Z)
    "hub": (170.0, 64.0, 110.0), "hub_wall": 4.0,
    "hub_zc": 190.0,                              # hub center above the soffit
    # 4 mounting plate, 6061 aluminium, stands on the bottom flange against the web
    "plate_w": 200.0, "plate_t": 8.0, "jack_gap": 22.0,   # gap under the top flange for the jack screw
    "jack_d": 12.0, "tab": (40.0, 30.0, 10.0),
    "clamp_x": 70.0, "clamp": (40.0, 30.0, 8.0),  # flange-tip clamps at +/- clamp_x; jaw width, reach, thickness
    # 2 accelerometer board, 3 signal board (inside the hub)
    "acc_board": (40.0, 3.0, 40.0), "sig_board": (110.0, 2.0, 80.0),
    # 5 strain gauges: protective cover patch under each bottom flange; dummy gauge coupon
    "gauge_patch": (90.0, 45.0, 6.0), "coupon": (40.0, 25.0, 6.0), "coupon_x": 160.0,
    # 6 temperature probes: steel probe on the web, air probe hanging in shade under the deck
    "t_probe": (7.0, 60.0), "t_steel_x": 130.0, "t_air": (-300.0, -450.0, 160.0),
    # 7 sensor cables (radius of the modelled cable)
    "cable_r": 4.0, "cable_x": -40.0,
    # 8 FieldNode core (from the FieldNode repo): enclosure, panel, V-block depth, base above the deck
    "fn_enc": (150.0, 90.0, 200.0), "fn_panel": (290.0, 200.0, 17.0), "fn_tilt": 40.0,
    "fn_panel_c": (115.0, 385.0),                 # panel center: out from the enclosure back, above the base
    "fn_vblock": 30.0, "fn_plate": (180.0, 320.0, 3.0), "fn_base_above_deck": 450.0,
    "fn_whip": (10.0, 190.0),
}

DENSITY = {"al": 2.70e-6, "steel": 7.85e-6, "st": 7.95e-6, "pc": 1.20e-6}   # kg/mm3


def derived(p=PARAMS):
    """Dimensions the calc note and the drawing quote, computed from PARAMS."""
    d, b, tf, tw = p["girder"]
    z0 = p["g_z0"]
    web_face = -p["gy"] - tw / 2                   # outer face of the south (-Y) web
    tip = -p["gy"] - b / 2                         # south girder, outer flange tip
    clear = d - 2 * tf                             # clear web height between flanges
    plate_h = clear - p["jack_gap"]
    hub_y0 = web_face - p["plate_t"]               # hub back face (on the plate)
    hub_y1 = hub_y0 - p["hub"][1]                  # hub front face
    deck_z0 = z0 + d
    deck_top = deck_z0 + p["deck"][0]
    post_y = -(p["deck"][1] / 2 + p["post"][0] / 2)
    fn_back = post_y - p["post"][0] / 2 - p["fn_vblock"] - p["fn_plate"][2]
    fn_z0 = deck_top + p["fn_base_above_deck"]
    return {
        "web_face": web_face, "tip": tip, "clear": clear, "plate_h": plate_h,
        "plate_z0": z0 + tf, "plate_z1": z0 + tf + plate_h,
        "hub_y0": hub_y0, "hub_y1": hub_y1, "hub_zc": z0 + p["hub_zc"],
        "hub_inside_tip": hub_y1 - tip,             # >0: hub front face inside the flange outline
        "deck_z0": deck_z0, "deck_top": deck_top, "post_y": post_y,
        "fn_back": fn_back, "fn_front": fn_back - p["fn_enc"][1], "fn_z0": fn_z0,
        "fn_z1": fn_z0 + p["fn_enc"][2],
        "fn_panel_cz": fn_z0 + p["fn_panel_c"][1],
        "post_top": deck_top + p["post"][2],
    }


def _b():
    import build123d as b
    return b


def box(cx, cy, cz, sx, sy, sz):
    b = _b()
    return b.Pos(cx, cy, cz) * b.Box(sx, sy, sz)


def tube(a, c, r):
    """Solid rod of radius r between two 3D points."""
    b = _b()
    a, c = b.Vector(*a), b.Vector(*c)
    d = c - a
    return b.Solid.make_cylinder(r, d.length, b.Plane(origin=a, z_dir=d.normalized()))


def fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def path(points, r):
    """Cable as rods between points, with a ball at each bend so the joints are closed."""
    b = _b()
    rods = [tube(a, c, r) for a, c in zip(points, points[1:])]
    balls = [b.Pos(*q) * b.Sphere(r) for q in points[1:-1]]
    return fuse(rods + balls)


def far_cable_inner(p=PARAMS):
    """|Y| of the far gauge cable's vertical runs between the girders: one cable radius plus 3 mm
    inboard of the inner bottom-flange edges, so the cable clears both flanges (BRP-DDR-003)."""
    d, bf, tf, tw = p["girder"]
    return p["gy"] - bf / 2 - p["cable_r"] - 3


def i_girder(p, y, x0, x1):
    d, bf, tf, tw = p["girder"]
    L, xc, z0 = x1 - x0, (x0 + x1) / 2, p["g_z0"]
    return (box(xc, y, z0 + tf / 2, L, bf, tf) + box(xc, y, z0 + d - tf / 2, L, bf, tf)
            + box(xc, y, z0 + d / 2, L, tw, d - 2 * tf))


def build_parts(p=PARAMS):
    """Return {key: solid} for BOM items 1 to 8 (item 9, the microSD card, sits in the signal board)."""
    b = _b()
    D = derived(p)
    d, bf, tf, tw = p["girder"]
    z0 = p["g_z0"]
    hx, hy, hz = p["hub"]
    hyc = (D["hub_y0"] + D["hub_y1"]) / 2
    hzc = D["hub_zc"]
    parts = {}

    # 1 hub enclosure, hollow, with two M12 glands underneath and one bulkhead connector
    w = p["hub_wall"]
    shell = box(0, hyc, hzc, hx, hy, hz) - box(0, hyc, hzc, hx - 2 * w, hy - 2 * w, hz - 2 * w)
    glands = fuse(b.Pos(gx, hyc, hzc - hz / 2 - 9) * b.Cylinder(9, 18) for gx in (-50, 50))
    bulk = b.Pos(0, hyc, hzc - hz / 2 - 9) * b.Cylinder(8, 18)
    parts["hub"] = shell + glands + bulk

    # 2 accelerometer board, bonded to the enclosure base on the plate side
    ax, ay, az = p["acc_board"]
    parts["acc"] = box(-55, D["hub_y0"] - w - ay / 2, hzc + 15, ax, ay, az)
    # 3 signal board on standoffs
    sx, sy, sz = p["sig_board"]
    sig_y = D["hub_y0"] - w - 14
    parts["sig"] = (box(22, sig_y, hzc - 5, sx, sy, sz)
                    + fuse(box(xx, (D["hub_y0"] - w + sig_y) / 2, hzc - 35, 6, abs(sig_y - D["hub_y0"] + w), 6)
                           for xx in (-25, 70)))

    # 4 mounting plate on the bottom flange against the web, jack screw to the top flange, two tip clamps
    pt = p["plate_t"]
    pl_yc = D["web_face"] - pt / 2
    plate = box(0, pl_yc, (D["plate_z0"] + D["plate_z1"]) / 2, p["plate_w"], pt, D["plate_h"])
    tx, ty, tz = p["tab"]
    tab = box(0, D["web_face"] - pt - ty / 2, D["plate_z1"] - tz / 2, tx, ty, tz)
    jack = b.Pos(0, D["web_face"] - pt - ty / 2, D["plate_z1"] + p["jack_gap"] / 2) * b.Cylinder(p["jack_d"] / 2, p["jack_gap"])
    jx, jr, jt = p["clamp"]
    clamps = None
    for cx in (-p["clamp_x"], p["clamp_x"]):
        top_block = box(cx, D["web_face"] - pt - 12, z0 + tf + 12, jx, 24, 24)          # bolted to the plate foot
        jaw = box(cx, D["tip"] + jr / 2 - 8, z0 - jt / 2, jx, jr, jt)                   # under the flange tip
        bolt = b.Pos(cx, D["tip"] - 6, z0 + (tf + 24) / 2 - jt / 2) * b.Cylinder(5, tf + 24 + jt)
        spacer = box(cx, (D["web_face"] - pt - 24 + D["tip"] - 12) / 2, z0 + tf + 6, jx, abs(D["tip"] - 12 - D["web_face"] + pt + 24), 12)
        c = top_block + jaw + bolt + spacer
        clamps = c if clamps is None else clamps + c
    parts["mount"] = plate + tab + jack + clamps

    # 5 strain gauges: cover patch under each bottom flange at midspan; dummy coupon on each flange top
    gx_, gy_, gz_ = p["gauge_patch"]
    cx_, cy_, cz_ = p["coupon"]
    parts["gauges"] = fuse([box(0, s * p["gy"], z0 - gz_ / 2, gx_, gy_, gz_) for s in (-1, 1)]
                           + [box(p["coupon_x"], s * (p["gy"] + tw / 2 + 25), z0 + tf + cz_ / 2, cx_, cy_, cz_) for s in (-1, 1)])

    # 6 temperature probes
    tr, tl = p["t_probe"]
    steel = b.Pos(p["t_steel_x"], D["web_face"] - tl / 2 / 4, hzc + 30) * b.Rot(90, 0, 0) * b.Cylinder(tr, tl / 4)
    axp, ayp, azp = p["t_air"]
    air = b.Pos(axp, ayp, D["deck_z0"] - azp) * b.Cylinder(tr, tl)
    air_lead = tube((axp, ayp, D["deck_z0"] - azp + tl / 2), (axp, ayp, D["deck_z0"] - tf), 2.5)
    parts["temps"] = steel + air + air_lead

    # 7 cables: near gauge and far gauge wrap round the south bottom flange tip into the hub glands;
    # far gauge crosses between the girders under the deck; hub to FieldNode up outside the deck edge
    r = p["cable_r"]
    cxc = p["cable_x"]
    under = z0 - r - 2                                     # cable centre under the flange, clipped tight
    tipo = D["tip"] - r - 3
    gland_z = hzc - hz / 2 - 18
    near = path([(cxc, -p["gy"], under), (cxc, tipo, under), (cxc, tipo, z0 + tf + 30),
                 (-50, hyc, z0 + tf + 30), (-50, hyc, gland_z)], r)
    far_x = cxc - 60
    inner_n = far_cable_inner(p)                           # inboard of the inner flange edges (BRP-DDR-003)
    inner_s = -inner_n
    far = path([(far_x, p["gy"], under), (far_x, inner_n, under), (far_x, inner_n, D["deck_z0"] - tf - r - 2),
                (far_x, inner_s, D["deck_z0"] - tf - r - 2), (far_x, inner_s, under), (far_x, tipo, under),
                (far_x, tipo, z0 + tf + 45), (50, hyc, z0 + tf + 45), (50, hyc, gland_z)], r)
    fnx = 30.0
    out_y = -p["deck"][1] / 2 - 12
    to_fn = path([(0, hyc, gland_z), (0, hyc, z0 + tf + 60), (0, tipo, z0 + tf + 60), (0, out_y, z0 + tf + 60),
                  (0, out_y, D["deck_top"] + 60), (fnx, D["post_y"] - p["post"][0] / 2 - 6, D["deck_top"] + 60),
                  (fnx, D["post_y"] - p["post"][0] / 2 - 6, D["fn_z0"] - 40),
                  (fnx, (D["fn_back"] + D["fn_front"]) / 2 + 20, D["fn_z0"] - 40),
                  (fnx, (D["fn_back"] + D["fn_front"]) / 2 + 20, D["fn_z0"] - 12)], r)
    parts["cables"] = near + far + to_fn

    # 8 FieldNode core on the outboard face of the midspan post
    ex, ey, ez = p["fn_enc"]
    fyc = (D["fn_back"] + D["fn_front"]) / 2
    enc = box(0, fyc, D["fn_z0"] + ez / 2, ex, ey, ez)
    ports = fuse(b.Pos(px, fyc, D["fn_z0"] - 8) * b.Cylinder(8, 16) for px in (-52, -22))
    whip = b.Pos(58, fyc, D["fn_z0"] - p["fn_whip"][1] / 2) * b.Cylinder(p["fn_whip"][0] / 2, p["fn_whip"][1])
    fpx, fpz, fpt = p["fn_plate"]
    bplate = box(0, D["fn_back"] + fpt / 2, D["fn_z0"] + ez / 2 + 20, fpx, fpt, fpz)
    vb = fuse(box(0, D["post_y"] - p["post"][0] / 2 - p["fn_vblock"] / 2, zz, 50, p["fn_vblock"], 30)
              for zz in (D["fn_z0"] - 20, D["fn_z0"] + 230))
    s = p["post"][0]
    bands = fuse(box(0, D["post_y"], zz, s + 6, s + 6, 12) - box(0, D["post_y"], zz, s, s, 14)
                 for zz in (D["fn_z0"] - 20, D["fn_z0"] + 230))
    pw, ph, ptk = p["fn_panel"]
    pcy = D["fn_back"] - p["fn_panel_c"][0]
    panel = b.Pos(0, pcy, D["fn_panel_cz"]) * b.Rot(-p["fn_tilt"], 0, 0) * b.Box(pw, ph, ptk)
    arms = fuse(tube((xx, D["fn_back"], D["fn_z0"] + ez - 10), (xx, pcy + 20, D["fn_panel_cz"] - 20), 6) for xx in (-110, 110))
    parts["fieldnode"] = enc + ports + whip + bplate + vb + bands + panel + arms
    return parts


BOM_NAMES = {
    "hub": (1, "Sensor hub enclosure, IP67 die-cast"),
    "acc": (2, "Accelerometer board, ADXL355"),
    "sig": (3, "Signal board: 24-bit ADC, MCU, microSD, RS-485"),
    "mount": (4, "Mounting plate, jack screw and flange clamps"),
    "gauges": (5, "Strain gauge half-bridges (2)"),
    "temps": (6, "Temperature probes (2)"),
    "cables": (7, "Sensor cables and M12 connectors"),
    "fieldnode": (8, "FieldNode core (6 W panel, cell, radio)"),
}


def bridge_context(p=PARAMS, full=False):
    """Existing bridge (grey in renders and on the drawing). full=True gives the whole 7 m bridge."""
    D = derived(p)
    s = p["post"][0]
    x0, x1 = (-p["span"] / 2, p["span"] / 2) if full else (-p["seg"] / 2, p["seg"] / 2)
    girders = i_girder(p, -p["gy"], x0, x1) + i_girder(p, p["gy"], x0, x1)
    post = box(0, D["post_y"], D["deck_z0"] + (p["post"][2] + p["deck"][0]) / 2, s, s, p["post"][2] + p["deck"][0])
    post = post - box(0, D["post_y"], D["deck_z0"] + (p["post"][2] + p["deck"][0]) / 2 + 5,
                      s - 2 * p["post"][1], s - 2 * p["post"][1], p["post"][2] + p["deck"][0])
    deck = box((x0 + x1) / 2, 0, D["deck_z0"] + p["deck"][0] / 2, x1 - x0, p["deck"][1], p["deck"][0])
    return {"girders": girders, "post": post, "deck": deck}


def assembly(p=PARAMS):
    b = _b()
    return b.Compound(children=list(build_parts(p).values()))


def hub_group(p=PARAMS):
    b = _b()
    P = build_parts(p)
    return b.Compound(children=[P[k] for k in ("hub", "acc", "sig", "mount")])


def installed(p=PARAMS, deck=False):
    b = _b()
    ctx = bridge_context(p)
    kids = list(build_parts(p).values()) + [ctx["girders"], ctx["post"]] + ([ctx["deck"]] if deck else [])
    return b.Compound(children=kids)


def volumes(p=PARAMS):
    """Solid volumes (mm3) of the made parts, for the mass estimate in BRP-CAL-001."""
    P = build_parts(p)
    D = derived(p)
    plate = p["plate_w"] * p["plate_t"] * D["plate_h"]
    return {"hub_shell": P["hub"].volume, "mount": P["mount"].volume, "plate": plate,
            "mount_other": P["mount"].volume - plate}


if __name__ == "__main__":
    from build123d import export_step, export_stl
    root = Path(__file__).resolve().parents[1]
    (root / "step").mkdir(exist_ok=True)
    (root / "stl").mkdir(exist_ok=True)
    outs = {"bridgepulse-assembly": assembly(), "sensor-hub": hub_group(), "bridgepulse-installed": installed(deck=True)}
    for name, shape in outs.items():
        export_step(shape, str(root / "step" / f"{name}.step"))
        export_stl(shape, str(root / "stl" / f"{name}.stl"))
        bb = shape.bounding_box()
        print(f"{name}: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
    D = derived()
    print(f"hub front face {D['hub_inside_tip']:.1f} mm inside the flange tip; plate {PARAMS['plate_w']:.0f} x {D['plate_h']:.1f} x {PARAMS['plate_t']:.0f} mm")
