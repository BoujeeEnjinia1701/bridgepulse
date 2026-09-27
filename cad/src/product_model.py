"""BridgePulse product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: the sensor hub as a filleted, powder-coated die-cast
box with a separate lid, a gasket line at the parting plane, four lid screws, a name plate and a
clear viewing window over the accelerometer and signal boards (with a lit status light on the
board); two cable glands and the M12 panel connector with its moulded plug underneath; the hard
anodized mounting plate with its top tab, lock nut, jack screw and swivel pad; the two flange-tip
clamps with bolts, nuts and jaws; the active strain gauge under its cover patch below the bottom
flange; the dummy gauge on its steel coupon on the flange top; the steel temperature probe on the
web; and the sensor cables. Context is a 520 mm section of the south (-Y) girder, an IPE 360
class section with root fillets, with a strip of the timber deck on top.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.
A research prototype that supports but never replaces inspection by qualified engineers.

Every main dimension and interface comes from PARAMS and derived() in model.py, with the same axes:
X along the span (midspan at x = 0), Y across the bridge (the monitored girder on -Y), Z up, with
the soffit at z = g_z0. Differences from model.py (cable routes shortened to the girder section,
north girder gauge, air probe and FieldNode core not shown, lid window) are listed in
docs/REVIEW.md, session 2026-09-26.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Cylinder, Plane, Pos, RegularPolygon, Rot, Solid, Sphere, Vector,
                       extrude, fillet)
from model import PARAMS, derived, far_cable_inner

TITLE = "BridgePulse: clamp-on vibration and strain monitor for small bridges"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "accessory", "context"], "explode": False, "el": 24, "az": -52,
     "note": "Product render from the front right and above (about 24 deg elevation); sensor hub on its plate "
             "between the flanges of a girder section, boards and status light behind the lid window, dummy "
             "gauge coupon on the flange at right; the active gauge is under the bottom flange"},
    {"name": "exploded", "groups": ["shell", "internal"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): lid with window, gasket, "
             "signal and accelerometer boards, hub base with glands and M12 plug, mounting plate, jack screw, "
             "flange clamps, strain gauge and cover patch, dummy gauge coupon, steel temperature probe"},
    {"name": "detail", "groups": ["shell", "internal", "accessory", "context"], "explode": False, "el": 8, "az": -66,
     "note": "Detail from the front right, just above the bottom flange (about 8 deg elevation): accelerometer "
             "board at upper left and signal board behind the lid window, clamps on the flange tip below"},
]

# Colours (restrained product palette; kit accent)
C_HUB = "#D9DCE0"        # powder-coated die-cast aluminium, light grey
C_LID = "#E6E8EB"
C_GASKET = "#23272D"
C_ACCENT = "#0F766E"
C_LABEL = "#F4F4F2"
C_INK = "#2B2F36"
C_WINDOW = "#DCEBF5"
C_ANOD = "#4B5158"       # hard anodized plate
C_STEEL = "#B8BEC6"      # stainless fasteners and clamps
C_ZINC = "#9AA1A9"
C_BRASS = "#C9A227"
C_GLAND = "#2B2F36"
C_CABLE = "#1C1F24"
C_PCB = "#166534"
C_PCB2 = "#1E3A5F"
C_CHIP = "#111827"
C_TERM = "#2E7D5B"
C_LED = "#22C55E"
C_FOIL = "#C9832F"       # polyimide gauge backing with copper grid
C_COVER = "#3A3F45"      # gauge protective cover patch
C_GIRDER = "#8C949B"     # painted steel girder (existing structure)
C_DECK = "#9A7B5C"       # timber deck (existing structure)


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _box(cx, cy, cz, sx, sy, sz):
    return Pos(cx, cy, cz) * Box(sx, sy, sz)


def _zcyl(x, y, z, r, h):
    return Pos(x, y, z) * Cylinder(r, h)


def _ycyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(r, h)


def _xcyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(r, h)


def _pipe(points, r):
    """Round cable through `points` with spherical joints (clean bends)."""
    out = None
    for a, c in zip(points, points[1:]):
        a, c = Vector(*a), Vector(*c)
        d = c - a
        seg = Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))
        out = seg if out is None else out + seg
    for q in points[1:-1]:
        out += Pos(*q) * Sphere(r)
    return out


def _union(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def _edges_par(s, axis):
    return s.edges().filter_by(axis)


def _top(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _front(s):
    return s.faces().sort_by(Axis.Y)[0].edges()


def _hex_z(x, y, z, af, h):
    """Hex prism along Z (across flats `af`), centred at z."""
    return Pos(x, y, z - h / 2) * extrude(RegularPolygon(af / 1.732, 6), amount=h)


def _knurl_z(x, y, z, r, h, n=18):
    """Round nut along Z with shallow axial grooves (knurled grip)."""
    body = _zcyl(x, y, z, r, h)
    for k in range(n):
        a = 2 * math.pi * k / n
        body -= Pos(x + r * math.cos(a), y + r * math.sin(a), z) * Rot(0, 0, math.degrees(a)) * Box(1.2, 1.0, h + 1)
    return body


def product_parts(P=PARAMS):
    D = derived(P)
    d, bf, tf, tw = P["girder"]
    z0 = P["g_z0"]
    gy = -P["gy"]                                   # south girder centreline
    hx, hy, hz = P["hub"]
    w = P["hub_wall"]
    y0, y1 = D["hub_y0"], D["hub_y1"]               # hub back (on the plate) and front faces
    hyc = (y0 + y1) / 2
    hzc = D["hub_zc"]
    hz0, hz1 = hzc - hz / 2, hzc + hz / 2
    out = []

    def add(name, shape, color, material, bom, group, explode):
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    # ------------------------------------------------------------ 1 sensor hub enclosure
    E_BASE, E_GASK, E_LID, E_LSCR = (0, -110, 0), (0, -300, 0), (0, -390, 0), (0, -450, 0)
    lid_d = 12.0                                    # lid depth; base takes the rest of the 64 mm
    yp = y1 + lid_d                                 # parting plane
    gap = 0.6
    outer = _box(0, hyc, hzc, hx, hy, hz)
    outer = _fillet_try(outer, _edges_par(outer, Axis.Y), [8.0, 6.0, 4.0])
    outer = _fillet_try(outer, _front(outer), [3.0, 2.0, 1.0])
    cavity = _box(0, hyc, hzc, hx - 2 * w, hy - 2 * w, hz - 2 * w)
    cavity = _fillet_try(cavity, _edges_par(cavity, Axis.Y), [4.0, 2.0])
    base = (outer & _box(0, (y0 + yp) / 2, hzc, hx + 2, y0 - yp, hz + 2)) - cavity
    # four bosses for the lid screws inside the corners
    sxz = [(sx * (hx / 2 - 9), hzc + sz * (hz / 2 - 9)) for sx in (-1, 1) for sz in (-1, 1)]
    for (bx, bz) in sxz:
        base += _ycyl(bx, (y0 - w + yp) / 2, bz, 5.5, (y0 - w) - yp) & outer
    add("Hub base, die-cast aluminium", base, C_HUB, "painted", 1, "shell", E_BASE)

    gasket = _box(0, yp - gap / 2, hzc, hx - 3, gap, hz - 3) - _box(0, yp - gap / 2, hzc, hx - 2 * w - 1, 2, hz - 2 * w - 1)
    add("Lid gasket", gasket, C_GASKET, "rubber", 1, "shell", E_GASK)

    lid = (outer & _box(0, (yp - gap + y1) / 2, hzc, hx + 2, yp - gap - y1, hz + 2)) - cavity
    # window opening over the boards, rounded corners
    wx0, wx1, wz0, wz1 = -72.0, 66.0, hz0 + 23.0, hz1 - 17.0
    wcx, wcz, ww, wh = (wx0 + wx1) / 2, (wz0 + wz1) / 2, wx1 - wx0, wz1 - wz0
    opening = _box(wcx, y1 + 6, wcz, ww, 20, wh)
    opening = _fillet_try(opening, _edges_par(opening, Axis.Y), [5.0, 3.0])
    lid -= opening
    # shallow recess round the window for the pane
    rec = _box(wcx, y1 + 0.6, wcz, ww + 6, 1.2, wh + 6)
    rec = _fillet_try(rec, _edges_par(rec, Axis.Y), [6.0, 4.0])
    lid -= rec
    for (bx, bz) in sxz:
        lid -= _ycyl(bx, y1 + 0.7, bz, 3.9, 1.6)
    add("Hub lid, die-cast aluminium", lid, C_LID, "painted", 1, "shell", E_LID)

    pane = _box(wcx, y1 + 1.2, wcz, ww + 5.6, 2.4, wh + 5.6)
    pane = _fillet_try(pane, _edges_par(pane, Axis.Y), [5.8, 4.0])
    add("Clear polycarbonate lid window", pane, C_WINDOW, "clear", 1, "shell", E_LID)

    lscr = None
    for (bx, bz) in sxz:
        s = _ycyl(bx, y1 + 0.3, bz, 3.5, 1.4)
        s = _fillet_try(s, _front(s), [0.6, 0.3])
        s -= _box(bx, y1 - 0.5, bz, 4.2, 1.0, 0.9) + _box(bx, y1 - 0.5, bz, 0.9, 1.0, 4.2)
        lscr = s if lscr is None else lscr + s
    add("Lid screws, stainless", lscr, C_STEEL, "metal", 1, "shell", E_LSCR)

    # name plate on the strip under the window, with printed marks (thin raised parts)
    npz = (hz0 + wz0) / 2 - 1
    plate_n = _box(-10, y1 - 0.2, npz, 96, 0.4, 12)
    add("Hub name plate", plate_n, C_ACCENT, "painted", 1, "shell", E_LID)
    ink = (_box(-40, y1 - 0.5, npz + 1, 28, 0.3, 4) + _box(-4, y1 - 0.5, npz + 2, 32, 0.3, 2)
           + _box(-4, y1 - 0.5, npz - 2, 24, 0.3, 1.6) + _box(26, y1 - 0.5, npz, 12, 0.3, 6))
    add("Name plate print", ink, C_LABEL, "paper", 1, "shell", E_LID)
    tz = hz1 - 9.0
    triad = (_box(-44, y1 - 0.2, tz, 14, 0.4, 1.4) + _box(-51, y1 - 0.2, tz + 1, 1.4, 0.4, 13 - 3)
             + _ycyl(-51, y1 - 0.2, tz, 1.6, 0.4))
    add("Accelerometer axis mark", triad, C_ACCENT, "painted", 1, "shell", E_LID)
    ip = _box(55, y1 - 0.2, npz, 20, 0.4, 9)
    add("IP67 rating label", ip, C_LABEL, "paper", 1, "shell", E_LID)
    ipk = _box(55, y1 - 0.45, npz + 1, 14, 0.3, 2.2) + _box(55, y1 - 0.45, npz - 2, 10, 0.3, 1.4)
    add("Rating label print", ipk, C_INK, "paper", 1, "shell", E_LID)

    # two M12 cable glands (gauge cables) and the M12 panel connector underneath (model.py positions)
    E_GL = (E_BASE[0], E_BASE[1], -40)
    gl = None
    for gx in (-50, 50):
        g = _hex_z(gx, hyc, hz0 - 2.5, 20.0, 5.0) + _zcyl(gx, hyc, hz0 - 9, 9.0, 8.0)
        g = _fillet_try(g, _bottom(g), [2.5, 1.5])
        g += _zcyl(gx, hyc, hz0 - 14.5, 6.0, 3.0)
        gl = g if gl is None else gl + g
    add("Cable glands, M12 nylon", gl, C_GLAND, "plastic", 1, "shell", E_GL)
    bulk = _hex_z(0, hyc, hz0 - 1.5, 18.0, 3.0) + _zcyl(0, hyc, hz0 - 8, 6.0, 10.0)
    add("M12 panel connector", bulk, C_STEEL, "metal", 7, "shell", E_GL)
    plug = _knurl_z(0, hyc, hz0 - 21, 8.0, 16.0)
    body = _zcyl(0, hyc, hz0 - 37, 7.0, 16.0)
    body = _fillet_try(body, _bottom(body), [2.5, 1.5])
    add("M12 coupling nut", plug, C_STEEL, "metal", 7, "shell", (0, -110, -70))
    add("M12 moulded plug body", body, C_GLAND, "rubber", 7, "shell", (0, -110, -70))

    # ------------------------------------------------------------ 2 accelerometer board (model.py position)
    E_ACC = (0, -170, 30)
    ax, ay, az = P["acc_board"]
    acc_y = y0 - w - ay / 2
    apcb = _box(-55, acc_y, hzc + 15, ax, ay, az)
    apcb = _fillet_try(apcb, _edges_par(apcb, Axis.Y), [2.0, 1.0])
    add("Accelerometer board (ADXL355 class)", apcb, C_PCB2, "plastic", 2, "internal", E_ACC)
    ay_f = acc_y - ay / 2
    chip = _box(-55, ay_f - 0.8, hzc + 18, 6, 1.6, 6)
    head = _box(-55, ay_f - 4, hzc + 15 - az / 2 + 5, 16, 8, 5)
    add("Accelerometer and header", chip + head, C_CHIP, "plastic", 2, "internal", E_ACC)
    ascr = _union(_ycyl(-55 + sx * 15, ay_f - 0.7, hzc + 15 + sz * 15, 2.2, 1.4) for sx in (-1, 1) for sz in (-1, 1))
    add("Accelerometer board screws", ascr, C_STEEL, "metal", 2, "internal", E_ACC)

    # ------------------------------------------------------------ 3 signal board (model.py position)
    E_SIG = (0, -240, 0)
    sx_, sy_, sz_ = P["sig_board"]
    sig_y = y0 - w - 14
    sf = sig_y - sy_ / 2                             # front (component) side of the board
    spcb = _box(22, sig_y, hzc - 5, sx_, sy_, sz_)
    spcb = _fillet_try(spcb, _edges_par(spcb, Axis.Y), [2.0, 1.0])
    add("Signal board PCB", spcb, C_PCB, "plastic", 3, "internal", E_SIG)
    so = _union(_ycyl(xx, (y0 - w + sig_y + sy_ / 2) / 2, hzc - 35, 3.0, abs(sig_y + sy_ / 2 - y0 + w))
                for xx in (-25, 70))
    add("Signal board standoffs", so, C_BRASS, "metal", 3, "internal", E_SIG)
    mcu = _box(46, sf - 0.6, hzc + 17, 51, 1.2, 21)
    add("Microcontroller module (RP2040 class)", mcu, "#14532D", "plastic", 3, "internal", E_SIG)
    chips = (_box(46, sf - 1.7, hzc + 17, 7, 1.0, 7) + _box(30, sf - 1.5, hzc + 20, 4, 0.8, 5)
             + _box(-14, sf - 1.8, hzc + 17, 8, 1.2, 8) + _box(-14, sf - 1.5, hzc - 20, 6, 0.8, 5)
             + _zcyl(14, sf - 3.5, hzc - 20, 3.5, 6))
    add("Signal board ICs", chips, C_CHIP, "plastic", 3, "internal", E_SIG)
    adc = _box(-14, sf - 0.6, hzc + 17, 18, 1.2, 26) + _box(-14, sf - 0.6, hzc - 18, 18, 1.2, 20)
    add("ADC and RS-485 modules", adc, "#312E81", "plastic", 3, "internal", E_SIG)
    sd = _box(50, sf - 1.2, hzc - 25, 15, 2.4, 15)
    add("microSD socket", sd, C_STEEL, "metal", 3, "internal", E_SIG)
    card = _box(50, sf - 1.2, hzc - 34.5, 11, 1.0, 4)
    add("microSD card, industrial 32 GB", card, C_CHIP, "plastic", 9, "internal", E_SIG)
    term = _box(8, sf - 5, hzc - 38, 36, 10, 8)
    for k in range(6):
        term -= _box(-7 + 6 * k, sf - 10, hzc - 36, 3, 2, 3)
    add("Gauge terminal block", term, C_TERM, "plastic", 3, "internal", E_SIG)
    led = _ycyl(70, sf - 1.0, hzc + 28, 1.8, 2.0) + Pos(70, sf - 2.0, hzc + 28) * Sphere(1.8)
    add("Status light (lit)", led, C_LED, "emissive", 3, "internal", E_SIG)

    # ------------------------------------------------------------ 4 mounting plate, jack screw, clamps
    pt = P["plate_t"]
    pz0, pz1 = D["plate_z0"], D["plate_z1"]
    pl_yc = D["web_face"] - pt / 2
    plate = _box(0, pl_yc, (pz0 + pz1) / 2, P["plate_w"], pt, D["plate_h"])
    plate = _fillet_try(plate, _edges_par(plate, Axis.Y), [10.0, 6.0, 4.0])
    plate = _fillet_try(plate, _front(plate), [1.5, 1.0])
    tx, ty, tz = P["tab"]
    tyc = D["web_face"] - pt - ty / 2
    tab = _box(0, tyc, pz1 - tz / 2, tx, ty, tz)
    tab = _fillet_try(tab, _edges_par(tab, Axis.Z), [4.0, 2.0])
    plate += tab
    add("Mounting plate, 6061 hard anodized", plate, C_ANOD, "metal", 4, "shell", (0, 0, 0))
    plab = _box(0, D["web_face"] - pt - 0.2, pz1 - 40, 60, 0.4, 16)
    add("Plate ID label", plab, C_LABEL, "paper", 4, "shell", (0, 0, 0))
    plk = (_box(-12, D["web_face"] - pt - 0.45, pz1 - 36, 28, 0.3, 3) + _box(-6, D["web_face"] - pt - 0.45, pz1 - 42, 40, 0.3, 2)
           + _box(-10, D["web_face"] - pt - 0.45, pz1 - 46, 32, 0.3, 1.6))
    add("Plate label print", plk, C_INK, "paper", 4, "shell", (0, 0, 0))

    jg, jd = P["jack_gap"], P["jack_d"]
    jz0, jz1 = pz1, pz1 + jg
    nut = _hex_z(0, tyc, jz0 + 3.5, 19.0, 7.0)
    nut = _fillet_try(nut, _top(nut), [1.0, 0.5])
    add("Jack screw lock nut", nut, C_STEEL, "metal", 4, "shell", (0, 0, 45))
    rod = _zcyl(0, tyc, (jz0 + jz1) / 2, jd / 2, jg)
    for k in range(6):
        rod -= _zcyl(0, tyc, jz0 + 8.5 + 1.6 * k, jd / 2 + 1, 0.6) - _zcyl(0, tyc, jz0 + 8.5 + 1.6 * k, jd / 2 - 0.7, 1)
    pad = _zcyl(0, tyc, jz1 - 2.5, 10.0, 5.0)
    pad = _fillet_try(pad, _bottom(pad), [1.5, 1.0])
    add("Jack screw, M12, with swivel pad", rod + pad, C_STEEL, "metal", 4, "shell", (0, 0, 80))

    jx, jr, jt = P["clamp"]
    tip = D["tip"]
    E_CB, E_JAW, E_BOLT, E_CNUT = (0, -40, -40), (0, -40, -110), (0, -40, -175), (0, -40, 5)
    cbody, jaws, bolts, cnuts, cscr = [], [], [], [], []
    for cx in (-P["clamp_x"], P["clamp_x"]):
        blk = _box(cx, D["web_face"] - pt - 12, z0 + tf + 12, jx, 24, 24)
        spy0, spy1 = D["web_face"] - pt - 24, tip - 12
        sp = _box(cx, (spy0 + spy1) / 2, z0 + tf + 6, jx, abs(spy1 - spy0), 12)
        cb = _fillet_try(blk, _edges_par(blk, Axis.Y), [4.0, 2.0]) + _fillet_try(sp, _edges_par(sp, Axis.Z), [4.0, 2.0])
        cb -= _zcyl(cx, tip - 6, z0 + tf + 6, 5.5, 14)
        cbody.append(cb)
        jaw = _box(cx, tip + jr / 2 - 8, z0 - jt / 2, jx, jr, jt)
        jaw = _fillet_try(jaw, _edges_par(jaw, Axis.Z), [4.0, 2.0])
        jaw -= _zcyl(cx, tip - 6, z0 - jt / 2, 5.5, jt + 2)
        jaws.append(jaw)
        bz_lo = z0 - jt
        b = _zcyl(cx, tip - 6, (bz_lo + z0 + tf + 12) / 2 + 3, 5.0, z0 + tf + 12 - bz_lo + 6)
        b += _hex_z(cx, tip - 6, bz_lo - 2.5, 16.0, 5.0)
        bolts.append(b)
        wsh = _zcyl(cx, tip - 6, z0 + tf + 12.75, 8.5, 1.5)
        hn = _hex_z(cx, tip - 6, z0 + tf + 12 + 1.5 + 4, 16.0, 8.0)
        hn = _fillet_try(hn, _top(hn), [1.0, 0.5])
        cnuts.append(wsh + hn)
        cscr.append(_ycyl(cx - 10, D["web_face"] - pt - 24.6, z0 + tf + 16, 3.0, 1.2)
                    + _ycyl(cx + 10, D["web_face"] - pt - 24.6, z0 + tf + 16, 3.0, 1.2))
    add("Flange clamp bodies", _union(cbody), C_STEEL, "metal", 4, "shell", E_CB)
    add("Clamp screws to plate foot", _union(cscr), C_ZINC, "metal", 4, "shell", E_CB)
    add("Flange clamp jaws", _union(jaws), C_STEEL, "metal", 4, "shell", E_JAW)
    add("Clamp bolts, M10", _union(bolts), C_ZINC, "metal", 4, "shell", E_BOLT)
    add("Clamp nuts and washers", _union(cnuts), C_ZINC, "metal", 4, "shell", E_CNUT)

    # ------------------------------------------------------------ 5 strain gauges (south girder)
    gx_, gy_, gz_ = P["gauge_patch"]
    E_COV, E_GAU = (0, -330, -70), (0, -330, -25)
    cover = _box(0, gy, z0 - gz_ / 2, gx_, gy_, gz_)
    cover = _fillet_try(cover, _edges_par(cover, Axis.Z), [10.0, 6.0])
    cover = _fillet_try(cover, _bottom(cover), [2.5, 1.5])
    cover -= _box(0, gy, z0 - 0.25, 16, 10, 0.5)
    add("Strain gauge cover patch", cover, C_COVER, "rubber", 5, "shell", E_COV)
    foil = _box(0, gy, z0 - 0.25, 15, 9, 0.5)
    add("Active foil strain gauge", foil, C_FOIL, "plastic", 5, "shell", E_GAU)

    cx_, cy_, cz_ = P["coupon"]
    ccx, ccy = P["coupon_x"], gy - (tw / 2 + 25)
    E_CPN = (70, -60, 40)
    coupon = _box(ccx, ccy, z0 + tf + cz_ / 2, cx_, cy_, cz_)
    coupon = _fillet_try(coupon, _edges_par(coupon, Axis.Z), [3.0, 2.0])
    coupon = _fillet_try(coupon, _top(coupon), [0.8, 0.5])
    add("Dummy gauge steel coupon", coupon, C_ZINC, "metal", 5, "shell", E_CPN)
    ctop = z0 + tf + cz_
    dfoil = _box(ccx, ccy, ctop + 0.25, 15, 9, 0.5)
    add("Dummy foil strain gauge", dfoil, C_FOIL, "plastic", 5, "shell", (70, -60, 70))
    dcov = _box(ccx, ccy, ctop + 2.0, 26, 16, 3.0)
    dcov = _fillet_try(dcov, _edges_par(dcov, Axis.Z), [5.0, 3.0])
    dcov = _fillet_try(dcov, _top(dcov), [1.2, 0.8])
    dcov -= _box(ccx, ccy, ctop + 0.25, 16, 10, 0.5)
    add("Dummy gauge cover", dcov, C_COVER, "rubber", 5, "shell", (70, -60, 100))

    # ------------------------------------------------------------ 6 steel temperature probe on the web
    tr, tl = P["t_probe"]
    pzc = hzc + 30
    boss = _ycyl(P["t_steel_x"], D["web_face"] - tl / 8, pzc, tr, tl / 4)
    boss = _fillet_try(boss, _front(boss), [2.0, 1.0])
    add("Steel temperature probe (bonded boss)", boss, C_STEEL, "metal", 6, "shell", (60, -70, 0))
    tail = _ycyl(P["t_steel_x"], D["web_face"] - tl / 4 - 3, pzc, 3.5, 6.0)
    add("Probe lead strain relief", tail, C_CABLE, "rubber", 6, "shell", (60, -70, 0))

    # ------------------------------------------------------------ 7 sensor cables (shortened to the section)
    r = P["cable_r"]
    cxc = P["cable_x"]
    tipo = tip - r - 3
    under = z0 - r - 2
    gz_in = hz0 - 14.0                                   # cable enters the gland seal
    near = _pipe([(cxc, gy - gy_ / 2 + 2, under), (cxc, tipo, under), (cxc, tipo, z0 + tf + 30),
                  (-50, hyc, z0 + tf + 30), (-50, hyc, gz_in)], r)
    far_x = 100.0                                        # model.py crosses at x = -100; see docs/REVIEW.md
    inner = -far_cable_inner(P)                          # as model.py: inboard of the south inner flange edge
    far = _pipe([(50, hyc, gz_in), (50, hyc, z0 + tf + 45), (far_x, tipo, z0 + tf + 45), (far_x, tipo, under),
                 (far_x, inner, under), (far_x, inner, z0 + 150)], r)
    out_y = -P["deck"][1] / 2 - 12
    fz = z0 + tf + 60
    fnx = -130.0                                         # model.py rises at x = 0; see docs/REVIEW.md
    fn = _pipe([(0, hyc, hz0 - 44), (0, hyc, fz), (0, tipo - 8, fz), (fnx, tipo - 8, fz), (fnx, out_y, fz),
                (fnx, out_y, D["deck_top"])], r)
    add("Sensor cables, shielded 4-core", near + far, C_CABLE, "rubber", 7, "accessory", (0, 0, 0))
    add("M12 cable to the FieldNode core", fn, C_CABLE, "rubber", 7, "accessory", (0, 0, 0))
    fascia = -P["deck"][1] / 2
    clips = None
    for zz in (D["deck_z0"] + 25,):
        c = _box(fnx, (fascia + out_y - r - 2) / 2, zz, 2 * r + 6, fascia - out_y + r + 2, 10)
        c = _fillet_try(c, _edges_par(c, Axis.Z), [2.0, 1.0])
        c -= _zcyl(fnx, out_y, zz, r + 0.2, 12)
        c += _box(fnx, fascia - 1.5, zz, 26, 3, 10)
        clips = c if clips is None else clips + c
    add("UV-stable cable clips", clips, C_GLAND, "plastic", 7, "accessory", (0, 0, 0))

    # ------------------------------------------------------------ context: girder section and deck strip
    L = 520.0
    girder = (_box(0, gy, z0 + tf / 2, L, bf, tf) + _box(0, gy, z0 + d - tf / 2, L, bf, tf)
              + _box(0, gy, z0 + d / 2, L, tw, d - 2 * tf))
    roots = [e for e in girder.edges().filter_by(Axis.X)
             if abs(abs(e.center().Y - gy) - tw / 2) < 0.1
             and (abs(e.center().Z - (z0 + tf)) < 0.1 or abs(e.center().Z - (z0 + d - tf)) < 0.1)]
    girder = _fillet_try(girder, roots, [18.0, 12.0, 8.0])
    add("Steel girder section, IPE 360 class (existing)", girder, C_GIRDER, "painted", None, "context", (0, 0, 0))
    deck = None
    ny = 4
    y_out, y_in = -P["deck"][1] / 2, gy + 60
    for k in range(ny):
        bw = (L - (ny - 1) * 6) / ny
        bx = -L / 2 + bw / 2 + k * (bw + 6)
        bd = _box(bx, (y_out + y_in) / 2, D["deck_z0"] + P["deck"][0] / 2, bw, y_in - y_out, P["deck"][0])
        bd = _fillet_try(bd, _top(bd), [2.0, 1.0])
        deck = bd if deck is None else deck + bd
    add("Timber deck boards (existing)", deck, C_DECK, "wood", None, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:46s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:9.2f} cm3")
