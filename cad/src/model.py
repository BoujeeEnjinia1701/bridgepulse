"""BridgePulse parametric model (build123d), TRL 3, constructable (BRP-DDR-004).

Run from the repo root:  python cad/src/model.py          (STEP and STL exports, then the checks)
                         python cad/src/model.py --check  (constructability checks only)
Exports STEP and STL into cad/step and cad/stl:
    bridgepulse-assembly.step / .stl   the monitor (BOM items 1 to 9) as installed, no bridge
    sensor-hub.step / .stl             hub, boards, mounting plate, foot clamps and jack
    bridgepulse-installed.step / .stl  the monitor on an 800 mm midspan segment of the example bridge

Axes as in cad/src/concept_media.py: X along the span (midspan at x = 0), Y across the bridge
(the monitored girder and the FieldNode post are on -Y), Z up, with the underside of the girders
(the soffit) at z = g_z0. The example host is a 7 m steel footbridge on two IPE 360 class girders
with a timber deck. The bridge is existing structure and carries no BOM number.

Mounting (BRP-CAL-001 section H, made constructable in BRP-DDR-004): an 8 mm aluminium plate lies
flat against the outer face of the south girder's web, clear of the root fillets at both flanges.
Two stepped foot blocks, screwed to the plate's front face, stand on the bottom flange and are
clamped to it at the flange tip by a steel jaw, a packer and an M10 bolt. A jack block at the top
of the plate carries an M12 jack screw that bears on the underside of the top flange. The hub's
base is screwed flat to the plate by four M5 screws from inside the box. Nothing is drilled or
welded into the structure.

build_components() returns every made, bought and fixing component by name (the build plan
pictures and the checks use it); build_parts() groups them by BOM line for the concept media and
the calculations. The same PARAMS feed docs/04-calcs/sizing.py (BRP-CAL-001), drawing BRP-DWG-001
(cad/src/sheets.py) and the build plan pictures (cad/src/build_plan_media.py). The FieldNode core
is drawn as an envelope with the interface that matters here (its back plate on the post, its
bands and its sensor port); its parts and joints are FieldNode's, in FND-BLD-001.
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

# Top-level parameters (mm). Edit these, not the geometry below.
PARAMS = {
    # example host bridge (context, not in the BOM)
    "span": 6800.0, "bearing_span": 6400.0,
    "gy": 600.0,                                  # girder centerline offset from the bridge axis
    "girder": (360.0, 170.0, 12.7, 8.0),          # depth, flange width, flange thickness, web thickness
    "root_r": 18.0,                               # IPE 360 root fillet radius (web to flange)
    "g_z0": 1200.0,                               # soffit (underside of girders)
    "deck": (50.0, 1500.0),                       # timber deck thickness, width
    "post": (50.0, 3.0, 1100.0),                  # square hollow handrail post: size, wall, height above deck
    "seg": 800.0,                                 # girder length shown in the installed model and drawing
    # 1 sensor hub enclosure, die-cast aluminium, IP67: along X, out from the plate (Y), height (Z)
    "hub": (170.0, 64.0, 110.0), "hub_wall": 4.0, "lid_t": 6.0,
    "hub_zc": 190.0,                              # hub center above the soffit
    "hub_screws": (72.0, 42.0),                   # four M5 screws through the base: +/-x, +/-z from the hub center
    # penetrations in the hub's bottom face: x, kind ("g16" gauge gland, "g12" probe gland, "m12" panel connector)
    "pens": {"near_gauge": (-30.0, "g16"), "far_gauge": (30.0, "g16"), "steel_probe": (-60.0, "g12"),
             "air_probe": (60.0, "g12"), "fieldnode": (0.0, "m12")},
    # 4 mounting plate and its clamps
    "plate_w": 200.0, "plate_t": 8.0,
    "fillet_gap": 22.0,                           # plate ends kept this far from each flange (root fillet clear)
    "jack_gap": 22.0,                             # gap under the top flange, bridged by the jack screw
    "jack_d": 12.0,
    "tab": (40.0, 30.0, 30.0),                    # jack block: along X, out from the plate, height
    "jack_out": 18.0,                             # jack screw axis out from the plate's front face
    "clamp_x": 76.0,                              # foot clamps at +/- clamp_x
    "clamp": (40.0, 30.0, 10.0),                  # foot block width (X), jaw reach under the flange, jaw thickness
    "foot": (30.0, 40.0, 12.0, 12.0),             # foot block: tall part depth, tall part height, tail thickness, fillet chamfer
    "foot_over": 23.0,                            # foot block tail runs this far past the flange tip
    "bolt_out": 10.0,                             # clamp bolt axis out from the flange tip
    "packer_od": 16.0,
    # 2 accelerometer board, 3 signal board (inside the hub): size along X, thickness, size along Z
    "acc_board": (40.0, 2.0, 40.0), "acc_xz": (-50.0, 0.0), "acc_spacer": 5.0,
    "sig_board": (92.0, 1.6, 68.0), "sig_xz": (20.0, 0.0), "sig_standoff": 14.0,
    # 5 strain gauges: cover patch under each bottom flange; dummy gauge coupon on the flange top
    "gauge_patch": (60.0, 40.0, 6.0), "coupon": (40.0, 25.0, 6.0), "coupon_x": 20.0, "coupon_out": 35.0,
    # 6 temperature probes: 7 mm x 60 mm sheaths. Steel probe on the bottom flange top, held by a
    # flange clip; air probe hanging in shade between the girders from the far gauge cable
    "t_probe": (7.0, 60.0), "t_steel_x": -140.0, "t_air": (47.0, -300.0, 1430.0),
    # 7 sensor cables (radius of the modelled cable and of a probe lead)
    "cable_r": 4.0, "lead_r": 2.5, "cable_x": -40.0, "far_x": 40.0, "cable_z": 65.0, "fn_cable_z": 80.0,
    # 8 FieldNode core (from the FieldNode repo): enclosure, panel, back plate, base above the deck
    "fn_enc": (150.0, 90.0, 200.0), "fn_panel": (290.0, 200.0, 17.0), "fn_tilt": 40.0,
    "fn_panel_c": (115.0, 385.0),                 # panel center: out from the enclosure back, above the base
    "fn_vblock": 0.0,                             # V-blocks left off on a square post (BRP-DDR-004)
    "fn_plate": (180.0, 320.0, 3.0), "fn_base_above_deck": 450.0,
    "fn_whip": (10.0, 190.0), "fn_band_dz": (-20.0, 230.0), "fn_slot_x": 51.0,
}

DENSITY = {"al": 2.70e-6, "steel": 7.85e-6, "st": 7.95e-6, "pc": 1.20e-6}   # kg/mm3


@dataclass
class Comp:
    """One component: a single made or bought piece (or a matched set of fixings)."""
    name: str
    shape: object
    bom: int | None
    kind: str          # "made", "bought", "fixing" or "fieldnode"
    group: str         # key in BOM_NAMES (build_parts groups components by it)
    mat: str = "al"


def derived(p=PARAMS):
    """Dimensions the calc note, the drawing and the build plan quote, computed from PARAMS."""
    d, b, tf, tw = p["girder"]
    z0 = p["g_z0"]
    web_face = -p["gy"] - tw / 2                   # outer face of the south (-Y) web
    tip = -p["gy"] - b / 2                         # south girder, outer flange tip
    clear = d - 2 * tf                             # clear web height between flanges
    flange_top = z0 + tf                           # top of the bottom flange
    flange_under = z0 + d - tf                     # underside of the top flange
    plate_z0 = flange_top + p["fillet_gap"]
    plate_z1 = flange_under - p["jack_gap"]
    hub_y0 = web_face - p["plate_t"]               # hub back face (on the plate)
    hub_y1 = hub_y0 - p["hub"][1]                  # hub front face (outside of the lid)
    deck_z0 = z0 + d
    deck_top = deck_z0 + p["deck"][0]
    post_y = -(p["deck"][1] / 2 + p["post"][0] / 2)
    fn_back = post_y - p["post"][0] / 2 - p["fn_vblock"] - p["fn_plate"][2]
    fn_z0 = deck_top + p["fn_base_above_deck"]
    hub_zc = z0 + p["hub_zc"]
    return {
        "web_face": web_face, "tip": tip, "clear": clear, "flange_top": flange_top, "flange_under": flange_under,
        "plate_h": plate_z1 - plate_z0, "plate_z0": plate_z0, "plate_z1": plate_z1,
        "hub_y0": hub_y0, "hub_y1": hub_y1, "hub_zc": hub_zc, "hub_z0": hub_zc - p["hub"][2] / 2,
        "hub_z1": hub_zc + p["hub"][2] / 2, "body_y1": hub_y1 + p["lid_t"],
        "hub_inside_tip": hub_y1 - tip,             # >0: hub front face inside the flange outline
        "deck_z0": deck_z0, "deck_top": deck_top, "post_y": post_y,
        "fn_back": fn_back, "fn_front": fn_back - p["fn_enc"][1], "fn_z0": fn_z0,
        "fn_z1": fn_z0 + p["fn_enc"][2],
        "fn_panel_cz": fn_z0 + p["fn_panel_c"][1],
        "post_top": deck_top + p["post"][2],
        "jack_y": hub_y0 - p["jack_out"],
        "bolt_y": tip - p["bolt_out"],
        "foot_screw_z": (plate_z0 + flange_top + p["foot"][1]) / 2,
        "under": z0 - p["cable_r"] - 2,             # centre of a cable clipped under a flange
        "tipo": tip - p["cable_r"] - 3,             # centre of a cable passing the south flange tip
        "body_yc": (hub_y0 + hub_y1 + p["lid_t"]) / 2,
    }


def _b():
    import build123d as b
    return b


def box(cx, cy, cz, sx, sy, sz):
    b = _b()
    return b.Pos(cx, cy, cz) * b.Box(sx, sy, sz)


def cyl_z(x, y, z0_, z1_, r):
    """Vertical cylinder from z0_ to z1_."""
    b = _b()
    return b.Pos(x, y, (z0_ + z1_) / 2) * b.Cylinder(r, abs(z1_ - z0_))


def cyl_y(x, y0_, y1_, z, r):
    b = _b()
    return b.Pos(x, (y0_ + y1_) / 2, z) * b.Rot(90, 0, 0) * b.Cylinder(r, abs(y1_ - y0_))


def cyl_x(x0_, x1_, y, z, r):
    b = _b()
    return b.Pos((x0_ + x1_) / 2, y, z) * b.Rot(0, 90, 0) * b.Cylinder(r, abs(x1_ - x0_))


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


def strip(a, c, z, width, t):
    """Flat band of the given width (along Z) and thickness t from a to c in the XY plane."""
    b = _b()
    dx, dy = c[0] - a[0], c[1] - a[1]
    L = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    return b.Pos((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, z) * b.Rot(0, 0, ang) * b.Box(L + t, t, width)


def far_cable_inner(p=PARAMS):
    """|Y| of the far gauge cable's vertical runs between the girders: one cable radius plus 3 mm
    inboard of the inner bottom-flange edges, so the cable clears both flanges (BRP-DDR-003)."""
    d, bf, tf, tw = p["girder"]
    return p["gy"] - bf / 2 - p["cable_r"] - 3


def i_girder(p, y, x0, x1, fillets=True):
    """Rolled I girder from x0 to x1, with root fillets between the web and the flanges."""
    b = _b()
    d, bf, tf, tw = p["girder"]
    L, xc, z0 = x1 - x0, (x0 + x1) / 2, p["g_z0"]
    g = (box(xc, y, z0 + tf / 2, L, bf, tf) + box(xc, y, z0 + d - tf / 2, L, bf, tf)
         + box(xc, y, z0 + d / 2, L, tw, d - 2 * tf))
    if not fillets or p["root_r"] <= 0:
        return g
    r = p["root_r"]
    for sy in (-1, 1):
        for zf, sz in ((z0 + tf, 1), (z0 + d - tf, -1)):
            # square block in the corner minus a cylinder leaves the fillet
            yc, zc = y + sy * (tw / 2 + r), zf + sz * r
            blk = box(xc, y + sy * (tw / 2 + r / 2), zf + sz * r / 2, L, r, r)
            g = g + (blk - cyl_x(x0 - 1, x1 + 1, yc, zc, r))
    return g


def _bolt_z(x, y, z_head_seat, z_tip, d, head_up=True, washer=True):
    """Hex-head bolt along Z: head sits on z_head_seat (above it if head_up), shank to z_tip."""
    hs = 0.65 * d
    wt = 0.16 * d if washer else 0
    s = 1 if head_up else -1
    parts = [cyl_z(x, y, z_head_seat, z_tip, d / 2)]
    if washer:
        parts.append(cyl_z(x, y, z_head_seat, z_head_seat + s * wt, d))
    parts.append(cyl_z(x, y, z_head_seat + s * wt, z_head_seat + s * (wt + hs), 0.8 * d))
    return fuse(parts)


def _screw_y(x, z, y_seat, y_tip, d, cap=True):
    """Socket cap screw along Y: head on y_seat (toward -Y), shank to y_tip (toward +Y)."""
    hd, hl = 1.5 * d, d
    return cyl_y(x, y_seat, y_tip, z, d / 2) + cyl_y(x, y_seat - hl, y_seat, z, hd / 2)


def build_components(p=PARAMS):
    """Every component, by name, as Comp objects, in build order where that matters."""
    b = _b()
    D = derived(p)
    d, bf, tf, tw = p["girder"]
    z0 = p["g_z0"]
    ft, fu = D["flange_top"], D["flange_under"]
    hx, hy, hz = p["hub"]
    w = p["hub_wall"]
    hzc = D["hub_zc"]
    y0, y1 = D["hub_y0"], D["hub_y1"]
    by1 = D["body_y1"]
    byc = D["body_yc"]
    hz0, hz1 = D["hub_z0"], D["hub_z1"]
    pt = p["plate_t"]
    wf = D["web_face"]
    C = {}

    def add(key, name, shape, bom, kind, group, mat="al"):
        C[key] = Comp(name, shape, bom, kind, group, mat)

    # ---------------- 4 mounting plate, against the web, clear of both root fillets
    pz0, pz1 = D["plate_z0"], D["plate_z1"]
    pyc = wf - pt / 2
    plate = box(0, pyc, (pz0 + pz1) / 2, p["plate_w"], pt, pz1 - pz0)
    sx, sz = p["hub_screws"]
    holes = [cyl_y(x, wf - pt - 1, wf + 1, z, 2.5) for x in (-sx, sx) for z in (hzc - sz, hzc + sz)]        # M5 tapped
    fz = D["foot_screw_z"]
    holes += [cyl_y(cx + dx, wf - pt - 1, wf + 1, fz, 3.0) for cx in (-p["clamp_x"], p["clamp_x"]) for dx in (-10, 10)]  # M6 tapped
    jz = pz1 - p["tab"][2] / 2
    holes += [cyl_y(dx, wf - pt - 1, wf + 1, jz, 3.0) for dx in (-12, 12)]                                       # M6 tapped
    holes.append(cyl_y(-85, wf - pt - 1, wf + 1, pz1 - 20, 3.25))                                               # lanyard 6.5
    for h in holes:
        plate = plate - h
    add("plate", "Mounting plate", plate, 4, "made", "mount")

    # ---------------- foot blocks: stepped, chamfered over the root fillet, clamped at the flange tip
    fd, fh, tt, ch = p["foot"]
    fw = p["clamp"][0]
    yb = D["bolt_y"]
    ytail = D["tip"] - p["foot_over"]
    feet, jaws, packers, fbolts, fscrews = [], [], [], [], []
    for cx in (-p["clamp_x"], p["clamp_x"]):
        y_tall0, y_tall1 = wf - pt, wf - pt - fd                       # back face on the plate, front face
        tall = box(cx, (y_tall0 + y_tall1) / 2, ft + fh / 2, fw, fd, fh)
        tail = box(cx, (y_tall1 + ytail) / 2, ft + tt / 2, fw, abs(ytail - y_tall1), tt)
        blk = tall + tail
        # 45 degree chamfer along the bottom back edge, so the block clears the root fillet
        cut = (b.Pos(cx, y_tall0, ft) * b.Rot(45, 0, 0) * b.Box(fw + 2, ch * math.sqrt(2), ch * math.sqrt(2)))
        blk = blk - cut
        for dx in (-10, 10):
            blk = blk - cyl_y(cx + dx, y_tall1 - 1, y_tall0 + 1, fz, 3.3) - cyl_y(cx + dx, y_tall1 - 1, y_tall1 + 6.5, fz, 5.5)
        blk = blk - cyl_z(cx, yb, ft - 1, ft + tt + 1, 5.5)
        feet.append(blk)
        jr, jt = p["clamp"][1], p["clamp"][2]
        jy0, jy1 = D["tip"] + jr - 8, ytail                             # 22 mm under the flange, out past the bolt
        jaw = box(cx, (jy0 + jy1) / 2, z0 - jt / 2, fw, abs(jy1 - jy0), jt) - cyl_z(cx, yb, z0 - jt - 1, z0 + 1, 5.0)
        jaws.append(jaw)
        packers.append(cyl_z(cx, yb, z0, ft - 0.5, p["packer_od"] / 2) - cyl_z(cx, yb, z0 - 1, ft + 1, 5.25))
        fbolts.append(_bolt_z(cx, yb, ft + tt, z0 - jt + 1.2, 10.0))
        for dx in (-10, 10):
            fscrews.append(_screw_y(cx + dx, fz, y_tall1 + 6.5, wf - 1.5, 6.0))
    add("feet", "Foot blocks (2)", fuse(feet), 4, "made", "mount")
    add("jaws", "Clamp jaws (2)", fuse(jaws), 4, "made", "mount", "steel")
    add("packers", "Packers (2)", fuse(packers), 4, "made", "mount", "steel")
    add("foot_bolts", "M10 clamp bolts (2)", fuse(fbolts), 4, "fixing", "mount", "steel")
    add("foot_screws", "M6 foot screws (4)", fuse(fscrews), 4, "fixing", "mount", "steel")

    # ---------------- jack block and jack screw
    jx, jy, jzh = p["tab"]
    jb_y0, jb_y1 = wf - pt, wf - pt - jy
    jyc = D["jack_y"]
    jblk = box(0, (jb_y0 + jb_y1) / 2, pz1 - jzh / 2, jx, jy, jzh) - cyl_z(0, jyc, pz1 - jzh - 1, pz1 + 1, p["jack_d"] / 2)
    for dx in (-12, 12):
        jblk = jblk - cyl_y(dx, jb_y1 - 1, jb_y0 + 1, jz, 3.3) - cyl_y(dx, jb_y1 - 1, jb_y1 + 6.5, jz, 5.5)
    add("jack_block", "Jack block", jblk, 4, "made", "mount")
    jd = p["jack_d"]
    nut_t, head_t = 10.0, 7.5
    jzb = pz1 - jzh
    jack = (cyl_z(0, jyc, jzb - nut_t - head_t, fu, jd / 2)
            + cyl_z(0, jyc, jzb - nut_t, jzb, 9.0)                         # lock nut under the block
            + cyl_z(0, jyc, jzb - nut_t - head_t, jzb - nut_t, 9.0))       # hex head
    add("jack", "M12 jack screw and lock nut", jack, 4, "fixing", "mount", "steel")
    add("jack_screws", "M6 jack block screws (2)",
        fuse(_screw_y(dx, jz, jb_y1 + 6.5, wf - 1.5, 6.0) for dx in (-12, 12)), 4, "fixing", "mount", "steel")

    # ---------------- 1 hub body (base on the plate, open at the front), lid, penetrations
    body = box(0, (y0 + by1) / 2, hzc, hx, abs(by1 - y0), hz) - box(0, (y0 - w + by1 - 1) / 2, hzc, hx - 2 * w, abs(by1 - 1 - y0 + w), hz - 2 * w)
    PEN = {"g16": (8.1, 10.0, 16.0, 11.0, 5.0), "g12": (6.1, 7.5, 14.0, 8.0, 4.0), "m12": (8.1, 8.0, 14.0, 10.0, 4.0)}
    pens = {}
    for k, (x, kind) in p["pens"].items():
        hr, orr, oh, nr, nh = PEN[kind]
        body = body - cyl_z(x, byc, hz0 - 1, hz0 + w + 1, hr)
        pens[k] = (cyl_z(x, byc, hz0 - oh, hz0, orr) + cyl_z(x, byc, hz0, hz0 + w, hr)
                   + cyl_z(x, byc, hz0 + w, hz0 + w + nh, nr))
    for x in (-sx, sx):
        for z in (hzc - sz, hzc + sz):
            body = body - cyl_y(x, y0 - w - 1, y0 + 1, z, 2.75)
    # eight 3.2 mm holes for the board spacers and standoffs (M3 countersunk from outside)
    for (bx_, bz_, bw_, bh_) in ((p["acc_xz"][0], p["acc_xz"][1], p["acc_board"][0], p["acc_board"][2]),
                                 (p["sig_xz"][0], p["sig_xz"][1], p["sig_board"][0], p["sig_board"][2])):
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                body = body - cyl_y(bx_ + s1 * (bw_ / 2 - 4), y0 - w - 1, y0 + 1, hzc + bz_ + s2 * (bh_ / 2 - 4), 1.6)
    add("body", "Hub enclosure body, drilled", body, 1, "bought", "hub")
    add("lid", "Hub lid", box(0, (by1 + y1) / 2, hzc, hx, p["lid_t"], hz), 1, "bought", "hub")
    add("glands", "Gauge cable glands (2, M16)", pens["near_gauge"] + pens["far_gauge"], 1, "bought", "hub")
    add("probe_glands", "Probe glands (2, M12)", pens["steel_probe"] + pens["air_probe"], 1, "bought", "hub")
    add("connector", "M12 5-pin panel connector", pens["fieldnode"], 7, "bought", "cables")
    # four M5 screws from inside, through the base into the plate, bonded sealing washer under each head
    hs = []
    for x in (-sx, sx):
        for z in (hzc - sz, hzc + sz):
            hs.append(cyl_y(x, y0 - w, wf - 2, z, 2.5) + cyl_y(x, y0 - w - 2, y0 - w, z, 6.5) + cyl_y(x, y0 - w - 5.5, y0 - w - 2, z, 4.25))
    add("hub_screws", "M5 hub screws with sealing washers (4)", fuse(hs), 1, "fixing", "hub", "steel")

    # ---------------- 2 accelerometer board on four short spacers; 3 signal board on four standoffs
    ax_, at, az_ = p["acc_board"]
    acx, acz = p["acc_xz"]
    ys = y0 - w
    aspace = p["acc_spacer"]
    acc_sp = fuse(cyl_y(acx + sx_ * (ax_ / 2 - 4), ys - aspace, ys, hzc + acz + sz_ * (az_ / 2 - 4), 2.75)
                  for sx_ in (-1, 1) for sz_ in (-1, 1))
    acc = (box(acx, ys - aspace - at / 2, hzc + acz, ax_, at, az_)
           + box(acx, ys - aspace - at - 0.75, hzc + acz, 6, 1.5, 6)                 # the sensor chip
           + box(acx, ys - aspace - at - 4, hzc + acz - az_ / 2 + 5, 16, 8, 6))      # header
    add("acc_spacers", "Accelerometer spacers (4)", acc_sp, 2, "fixing", "acc")
    add("acc", "Accelerometer board", acc, 2, "bought", "acc")
    gx_, gt, gz_ = p["sig_board"]
    gcx, gcz = p["sig_xz"]
    so = p["sig_standoff"]
    sig_so = fuse(cyl_y(gcx + sx_ * (gx_ / 2 - 4), ys - so, ys, hzc + gcz + sz_ * (gz_ / 2 - 4), 2.75)
                  for sx_ in (-1, 1) for sz_ in (-1, 1))
    yb_ = ys - so - gt
    mods = [box(gcx - 18, yb_ - 2, hzc + 14, 51, 4, 21),            # RP2040 class board
            box(gcx + 28, yb_ - 1.5, hzc + 16, 24, 3, 18),          # ADC module
            box(gcx + 28, yb_ - 1.5, hzc - 10, 20, 3, 14),          # RS-485 module
            box(gcx - 26, yb_ - 1.5, hzc - 14, 22, 3, 17),          # buck converter
            box(gcx + 2, yb_ - 1.5, hzc - 16, 16, 3, 15),           # microSD socket
            box(gcx - 2, yb_ - 4, hzc - 29, 40, 8, 7)]              # terminal block for gauges and probes
    sig = box(gcx, ys - so - gt / 2, hzc + gcz, gx_, gt, gz_) + fuse(mods)
    add("sig_standoffs", "Signal board standoffs (4)", sig_so, 3, "fixing", "sig")
    add("sig", "Signal board with modules", sig, 3, "bought", "sig")

    # ---------------- 5 strain gauges: cover patch under each bottom flange, dummy coupon on the flange top
    gx_, gy_, gz_ = p["gauge_patch"]
    add("patches", "Active gauges under their covers (2)",
        fuse(box(0, s * p["gy"], z0 - gz_ / 2, gx_, gy_, gz_) for s in (-1, 1)), 5, "bought", "gauges")
    cx_, cy_, cz_ = p["coupon"]
    yco = p["gy"] + tw / 2 + p["coupon_out"]
    add("coupons", "Dummy gauge coupons (2)",
        fuse(box(p["coupon_x"], s * yco, ft + cz_ / 2, cx_, cy_, cz_) for s in (-1, 1)), 5, "made", "gauges", "steel")

    # ---------------- 6 temperature probes (sheath 7 x 60 mm)
    tr, tl = p["t_probe"][0] / 2, p["t_probe"][1]
    ty_ = D["tip"] + tr + 6.5
    tx = p["t_steel_x"]
    steel = cyl_x(tx - tl / 2, tx + tl / 2, ty_, ft + tr, tr)
    ax_p, ay_p, az_p = p["t_air"]
    air = cyl_z(ax_p, ay_p, az_p - tl, az_p, tr)
    add("steel_probe", "Steel temperature probe", steel, 6, "made", "temps", "st")
    add("air_probe", "Air temperature probe", air, 6, "made", "temps", "st")

    # ---------------- 7 cables, leads and clips
    r, lr = p["cable_r"], p["lead_r"]
    under, tipo = D["under"], D["tipo"]
    zc_ = ft + p["cable_z"]
    PX = {k: v[0] for k, v in p["pens"].items()}
    g16_bot, g12_bot, m12_bot = hz0 - PEN["g16"][2], hz0 - PEN["g12"][2], hz0 - PEN["m12"][2]
    nx, fx = p["cable_x"], p["far_x"]
    inner = far_cable_inner(p)
    cross_z = D["deck_z0"] - tf - r - 2
    near = path([(nx, -p["gy"], under), (nx, tipo, under), (nx, tipo, zc_), (PX["near_gauge"], byc, zc_),
                 (PX["near_gauge"], byc, g16_bot)], r)
    far = path([(fx, p["gy"], under), (fx, inner, under), (fx, inner, cross_z), (fx, -inner, cross_z),
                (fx, -inner, under), (fx, tipo, under), (fx, tipo, zc_), (PX["far_gauge"], byc, zc_),
                (PX["far_gauge"], byc, g16_bot)], r)
    add("near_cable", "Near gauge cable", near, 7, "bought", "cables")
    add("far_cable", "Far gauge cable", far, 7, "bought", "cables")
    alx = fx + r + lr + 0.5
    air_lead = path([(alx, ay_p, az_p), (alx, ay_p, cross_z), (alx, -inner, cross_z), (alx, -inner, under),
                     (alx, tipo, under), (alx, tipo, zc_), (PX["air_probe"], byc, zc_), (PX["air_probe"], byc, g12_bot)], lr)
    slx = tx + tl / 2
    zl = ft + p["cable_z"] + 35
    steel_lead = path([(slx, ty_, ft + tr), (slx + 8, ty_, ft + tr), (slx + 8, ty_, zl), (PX["steel_probe"], ty_, zl),
                       (PX["steel_probe"], byc, zl), (PX["steel_probe"], byc, g12_bot)], lr)
    add("probe_leads", "Probe leads (2)", air_lead + steel_lead, 6, "made", "temps")
    zf_ = ft + p["fn_cable_z"]
    py_ = D["post_y"]
    px_side = -p["post"][0] / 2 - 10
    port_y = D["fn_back"] - 55
    to_fn = path([(PX["fieldnode"], byc, m12_bot), (PX["fieldnode"], byc, zf_), (PX["fieldnode"], py_, zf_),
                  (px_side, py_, zf_), (px_side, py_, D["fn_z0"] - 60), (-22, port_y, D["fn_z0"] - 60),
                  (-22, port_y, D["fn_z0"] - 16)], r)
    add("fn_cable", "M12 cable to the FieldNode port", to_fn, 7, "bought", "cables")
    # spring-steel flange clips (push on to a flange edge, cable tie through the clip)
    clips = []

    def fclip(x, edge_y, toward, upper_z=None):
        """Clip on a bottom-flange edge at edge_y; toward = +1 if the flange runs from the edge toward +Y."""
        t_, reach, wdt = 1.5, 15.0, 20.0
        uz = ft if upper_z is None else upper_z
        web_ = box(x, edge_y - toward * t_ / 2, (z0 - t_ + uz + t_) / 2, wdt, t_, uz + t_ - (z0 - t_))
        lo = box(x, edge_y + toward * reach / 2, z0 - t_ / 2, wdt, reach, t_)
        up = box(x, edge_y + toward * reach / 2, uz + t_ / 2, wdt, reach, t_)
        return web_ + lo + up
    tip = D["tip"]
    north_edge = p["gy"] - bf / 2
    clips += [fclip(nx, tip, 1), fclip(fx, tip, 1), fclip(fx, -north_edge, -1), fclip(fx, north_edge, 1)]
    add("cable_clips", "Flange clips for cables (4)", fuse(clips), 7, "bought", "cables", "steel")
    add("probe_clip", "Flange clip for the steel probe", fclip(tx, tip, 1, upper_z=ft + 2 * tr), 6, "bought", "temps", "steel")

    # ---------------- 8 FieldNode core (envelope; built to FND-BLD-001) on the outboard face of the post
    ex, ey, ez = p["fn_enc"]
    fb = D["fn_back"]
    fyc = fb - ey / 2
    fz0 = D["fn_z0"]
    fpx, fpz, fpt = p["fn_plate"]
    bplate = box(0, fb + fpt / 2, fz0 + ez / 2 + 20, fpx, fpt, fpz)
    for dz in p["fn_band_dz"]:
        for sxs in (-1, 1):
            bplate = bplate - box(sxs * p["fn_slot_x"], fb + fpt / 2, fz0 + dz, 3, fpt + 2, 15)
    enc = box(0, fyc, fz0 + ez / 2, ex, ey, ez)
    port_y = fb - 55
    ports = fuse(cyl_z(px, port_y, fz0 - 16, fz0, 8) for px in (-54, -22))
    whip = cyl_z(30, port_y, fz0 - p["fn_whip"][1], fz0, p["fn_whip"][0] / 2)
    pw, ph, ptk = p["fn_panel"]
    pcy = fb - p["fn_panel_c"][0]
    pcz = D["fn_panel_cz"]
    tilt = p["fn_tilt"]
    panel = b.Pos(0, pcy, pcz) * b.Rot(tilt, 0, 0) * b.Box(pw, ph, ptk)       # faces -Y (away from the post)
    t = math.radians(tilt)

    def on_panel(ly, lz=-ptk / 2):
        return (pcy + ly * math.cos(t) - lz * math.sin(t), pcz + ly * math.sin(t) + lz * math.cos(t))
    hy_, hz_ = on_panel(ph / 2 - 15, -ptk / 2 + 2)
    ly_, lz_ = on_panel(-ph / 2 + 15, -ptk / 2 + 2)
    top_ = fz0 + ez / 2 + 20 + fpz / 2
    arms = fuse([tube((xx, fb - 5, top_ - 10), (xx, hy_, hz_), 5) for xx in (-82, 82)]
                + [tube((xx, fb - 5, top_ - 40), (xx, ly_, lz_), 5) for xx in (-82, 82)])
    add("fieldnode", "FieldNode core (built to its own plan)", bplate + enc + ports + whip + panel + arms, 8, "fieldnode", "fieldnode")
    # band clamps round the square post, through the plate slots and across the plate's front
    s = p["post"][0] / 2
    pf = py_ - s
    bands = []
    for dz in p["fn_band_dz"]:
        zb = fz0 + dz
        bt, bw = 0.8, 12.0
        pts = [(-s - bt / 2, py_ + s + bt / 2), (s + bt / 2, py_ + s + bt / 2), (s + bt / 2, pf + bt / 2)]
        segs = [strip(pts[0], pts[1], zb, bw, bt), strip(pts[1], pts[2], zb, bw, bt),
                strip((-s - bt / 2, py_ + s + bt / 2), (-s - bt / 2, pf + bt / 2), zb, bw, bt)]
        for sxs in (-1, 1):
            segs.append(strip((sxs * (s + bt / 2), pf + bt / 2), (sxs * (p["fn_slot_x"]), pf + bt / 2), zb, bw, bt))
            segs.append(box(sxs * p["fn_slot_x"], fb + fpt / 2, zb, bt, fpt, bw))
        segs.append(strip((-p["fn_slot_x"], fb - bt / 2), (p["fn_slot_x"], fb - bt / 2), zb, bw, bt))
        housing = box(0, py_ + s + bt + 6, zb, 22, 12, 16)
        bands.append(fuse(segs) + housing)
    add("fn_bands", "FieldNode band clamps, long (2)", fuse(bands), 8, "fieldnode", "fieldnode", "steel")
    return C


BOM_NAMES = {
    "hub": (1, "Sensor hub enclosure, IP67 die-cast"),
    "acc": (2, "Accelerometer board, ADXL355"),
    "sig": (3, "Signal board: 24-bit ADC, MCU, microSD, RS-485"),
    "mount": (4, "Mounting plate, foot clamps and jack"),
    "gauges": (5, "Strain gauge half-bridges (2)"),
    "temps": (6, "Temperature probes (2)"),
    "cables": (7, "Sensor cables, clips and M12 connectors"),
    "fieldnode": (8, "FieldNode core (6 W panel, cell, radio)"),
}


def build_parts(p=PARAMS):
    """Return {key: solid} for BOM items 1 to 8 (item 9, the microSD card, sits in the signal board)."""
    C = build_components(p)
    out = {}
    for k in BOM_NAMES:
        out[k] = fuse(c.shape for c in C.values() if c.group == k)
    return out


def bridge_context(p=PARAMS, full=False, fillets=True):
    """Existing bridge (grey in renders and on the drawing). full=True gives the whole 7 m bridge."""
    D = derived(p)
    s = p["post"][0]
    x0, x1 = (-p["span"] / 2, p["span"] / 2) if full else (-p["seg"] / 2, p["seg"] / 2)
    girders = i_girder(p, -p["gy"], x0, x1, fillets) + i_girder(p, p["gy"], x0, x1, fillets)
    post = box(0, D["post_y"], D["deck_z0"] + (p["post"][2] + p["deck"][0]) / 2, s, s, p["post"][2] + p["deck"][0])
    post = post - box(0, D["post_y"], D["deck_z0"] + (p["post"][2] + p["deck"][0]) / 2 + 5,
                      s - 2 * p["post"][1], s - 2 * p["post"][1], p["post"][2] + p["deck"][0])
    deck = box((x0 + x1) / 2, 0, D["deck_z0"] + p["deck"][0] / 2, x1 - x0, p["deck"][1], p["deck"][0])
    return {"girders": girders, "post": post, "deck": deck}


def assembly(p=PARAMS):
    b = _b()
    return b.Compound(children=list(build_parts(p).values()))


HUB_KEYS = ("plate", "feet", "jaws", "packers", "foot_bolts", "foot_screws", "jack_block", "jack", "jack_screws",
            "body", "lid", "glands", "probe_glands", "connector", "hub_screws", "acc_spacers", "acc",
            "sig_standoffs", "sig")


def hub_group(p=PARAMS):
    b = _b()
    C = build_components(p)
    return b.Compound(children=[C[k].shape for k in HUB_KEYS])


def installed(p=PARAMS, deck=False):
    b = _b()
    ctx = bridge_context(p)
    kids = list(build_parts(p).values()) + [ctx["girders"], ctx["post"]] + ([ctx["deck"]] if deck else [])
    return b.Compound(children=kids)


def volumes(p=PARAMS):
    """Solid volumes (mm3) for the mass estimate in BRP-CAL-001: the hub shell (body, lid and
    penetrations), the plate, the other aluminium mount parts and the steel mount parts."""
    C = build_components(p)
    v = lambda ks: sum(C[k].shape.volume for k in ks)  # noqa: E731
    mount = [k for k, c in C.items() if c.group == "mount"]
    return {"hub_shell": v(("body", "lid", "glands", "probe_glands", "connector")),
            "plate": C["plate"].shape.volume,
            "mount_al": v([k for k in mount if C[k].mat == "al" and k != "plate"]),
            "mount_steel": v([k for k in mount if C[k].mat == "steel"])}


# ------------------------------------------------------------------ constructability checks
def _vol(a, b_):
    try:
        s = a & b_
        return s.volume if s is not None else 0.0
    except Exception:
        return float("nan")


def _gap(a, b_):
    return a.distance_to(b_)


def checks(p=PARAMS):
    """Pairs that must touch (the joint is made there) and pairs that must stay apart, with the
    overlap volume (mm3) and gap (mm). Returns (description, volume, gap, expectation, ok) rows."""
    C = build_components(p)
    ctx = bridge_context(p)
    G, POST = ctx["girders"], ctx["post"]
    S = lambda k: C[k].shape  # noqa: E731
    rows = []

    def chk(desc, a, b_, expect):
        """expect: 'touch' (no overlap, gap 0) or a minimum clearance in mm."""
        v = _vol(a, b_)
        gp = _gap(a, b_)
        ok = v < 1e-2 and (gp < 0.05 if expect == "touch" else gp >= expect - 1e-6)
        rows.append((desc, v, gp, expect, ok))

    # mount on the girder
    chk("Plate flat on the web", S("plate"), G, "touch")
    chk("Plate clear of the bottom root fillet and flange", S("plate"), G - box(0, -600, 1400, 900, 8.01, 400), 3.0)
    chk("Foot blocks on the bottom flange", S("feet"), G, "touch")
    chk("Foot blocks on the plate's front face", S("feet"), S("plate"), "touch")
    chk("Jaws under the bottom flange", S("jaws"), G, "touch")
    chk("Packers on the jaws", S("packers"), S("jaws"), "touch")
    chk("Packers clear of the flange tip", S("packers"), G, 1.0)
    chk("Clamp bolts clear of the flange tip", S("foot_bolts"), G, 2.0)
    chk("Clamp bolts through foot blocks, packers and jaws", S("foot_bolts"), S("feet") + S("packers") + S("jaws"), "touch")
    chk("Foot screws in the plate, short of the web", S("foot_screws"), G, 1.0)
    chk("Foot screws through the foot blocks", S("foot_screws"), S("feet") + S("plate"), "touch")
    chk("Jack block on the plate", S("jack_block"), S("plate"), "touch")
    chk("Jack block clear of the girder (top flange 22 mm above)", S("jack_block"), G, 5.0)
    chk("Jack screw bears on the top flange", S("jack"), G, "touch")
    chk("Jack screw in the jack block", S("jack"), S("jack_block"), "touch")
    chk("Jack block screws short of the web", S("jack_screws"), G, 1.0)
    # hub
    chk("Hub base flat on the plate", S("body"), S("plate"), "touch")
    chk("Hub clear of the web and flanges", S("body") + S("lid"), G, 5.0)
    chk("Lid on the body", S("lid"), S("body"), "touch")
    chk("Hub screws through the base into the plate", S("hub_screws"), S("body") + S("plate"), "touch")
    chk("Hub screws short of the web", S("hub_screws"), G, 1.0)
    for k in ("glands", "probe_glands", "connector"):
        chk(f"{C[k].name} in the bottom face", S(k), S("body"), "touch")
        chk(f"{C[k].name} clear of the signal board", S(k), S("sig"), 5.0)
    chk("Gauge glands apart from the probe glands", S("glands"), S("probe_glands"), 8.0)
    chk("Gauge glands apart from the panel connector", S("glands"), S("connector"), 8.0)
    chk("Accelerometer spacers on the base", S("acc_spacers"), S("body"), "touch")
    chk("Accelerometer board on its spacers", S("acc"), S("acc_spacers"), "touch")
    chk("Signal board standoffs on the base", S("sig_standoffs"), S("body"), "touch")
    chk("Signal board on its standoffs", S("sig"), S("sig_standoffs"), "touch")
    chk("Accelerometer board clear of the signal board", S("acc"), S("sig"), 1.5)
    chk("Boards clear of the hub screws", S("acc") + S("sig"), S("hub_screws"), 0.5)
    chk("Boards clear of the lid", S("acc") + S("sig"), S("lid"), 5.0)
    chk("Hub clear of the foot blocks", S("body") + S("glands") + S("probe_glands") + S("connector"), S("feet"), 20.0)
    chk("Hub clear of the jack", S("body") + S("lid"), S("jack") + S("jack_block"), 20.0)
    # gauges and probes
    chk("Gauge covers under the bottom flanges", S("patches"), G, "touch")
    chk("Dummy coupons on the flange tops", S("coupons"), G, "touch")
    chk("Dummy coupons clear of the root fillets", S("coupons"), G - box(0, 0, 1206.35, 900, 2000, 12.7), 3.0)
    chk("Steel probe on the flange top", S("steel_probe"), G, "touch")
    chk("Probe clip on the flange", S("probe_clip"), G, "touch")
    chk("Probe clip holds the steel probe", S("probe_clip"), S("steel_probe"), "touch")
    chk("Air probe clear of the steel", S("air_probe"), G, 50.0)
    chk("Cable clips on the flange edges", S("cable_clips"), G, "touch")
    # cables
    mount_all = fuse(S(k) for k in ("plate", "feet", "jaws", "packers", "foot_bolts", "jack_block", "jack"))
    hub_all = fuse(S(k) for k in ("body", "lid"))
    for k in ("near_cable", "far_cable", "probe_leads", "fn_cable"):
        chk(f"{C[k].name} clear of the girders", S(k), G, 1.0)
        chk(f"{C[k].name} clear of the mount", S(k), mount_all, 1.0)
        chk(f"{C[k].name} clear of the hub body", S(k), hub_all, 1.0)
    chk("Gauge cables into the gauge glands", S("near_cable") + S("far_cable"), S("glands"), "touch")
    chk("Probe leads into the probe glands", S("probe_leads"), S("probe_glands"), "touch")
    chk("FieldNode cable on the panel connector", S("fn_cable"), S("connector"), "touch")
    chk("Near gauge cable clear of the far gauge cable", S("near_cable"), S("far_cable"), 3.0)
    chk("Probe leads clear of the gauge cables", S("probe_leads"), S("near_cable") + S("far_cable"), 0.3)
    chk("Probe leads clear of the FieldNode cable", S("probe_leads"), S("fn_cable"), 3.0)
    chk("Gauge cables clear of the FieldNode cable", S("near_cable") + S("far_cable"), S("fn_cable"), 3.0)
    chk("Cables clear of the gauge covers and coupons", S("near_cable") + S("far_cable") + S("probe_leads") + S("fn_cable"),
        S("patches") + S("coupons"), 0.5)
    chk("Cables clear of the clips' cable-tie side", S("near_cable") + S("far_cable"), S("cable_clips"), 0.3)
    # FieldNode on the post
    chk("FieldNode back plate on the post face", S("fieldnode"), POST, "touch")
    chk("FieldNode bands on the post", S("fn_bands"), POST, "touch")
    chk("FieldNode bands through the plate slots", S("fn_bands"), S("fieldnode"), "touch")
    chk("FieldNode cable clear of the post (clipped beside it)", S("fn_cable"), POST, 2.0)
    chk("FieldNode cable on the FieldNode port", S("fn_cable"), S("fieldnode"), "touch")
    chk("FieldNode cable clear of the bands", S("fn_cable"), S("fn_bands"), 5.0)
    # below the soffit (R9) and inside the girder outline
    D = derived(p)
    low = max(p["g_z0"] - c.shape.bounding_box().min.Z for k, c in C.items() if c.group != "fieldnode")
    rows.append(("Nothing more than 15 mm below the soffit (R9)", 0.0, 15 - low, 0.0, low <= 15.0))
    rows.append(("Hub front face inside the flange tip line", 0.0, D["hub_inside_tip"], 0.0, D["hub_inside_tip"] > 0))
    return rows


def print_checks(p=PARAMS):
    rows = checks(p)
    bad = [r for r in rows if not r[4]]
    for desc, v, gp, exp, ok in rows:
        e = "touch" if exp == "touch" else f">= {exp:g} mm"
        print(f"{'ok  ' if ok else 'FAIL'} {desc}: overlap {v:.2f} mm3, gap {gp:.2f} mm ({e})")
    print(f"{len(rows) - len(bad)} of {len(rows)} constructability checks pass")
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(1 if print_checks() else 0)
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
    print_checks()
