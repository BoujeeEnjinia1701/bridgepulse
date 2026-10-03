"""BridgePulse product appearance model (build123d), TRL 3, constructable design.

Finished-product look for photoreal renders. The sensor hub is drawn for appearance: a filleted,
powder-coated die-cast box with a separate lid, a gasket line at the parting plane, four lid screws,
a name plate and a clear viewing window over the boards (a render aid only, decided 2026-10-02; the
build uses the plain die-cast lid). Everything else is taken directly from the constructable model
in model.py (build_components), so it follows that model exactly: the hub's two M16 gauge glands,
two M12 probe glands and M12 panel connector; the accelerometer and signal boards on their spacers
and standoffs; the mounting plate lying on the web clear of the root fillets; the stepped foot
blocks, steel jaws, packers and M10 bolts; the jack block, jack screw and lock nut; the lanyard pad
eye, the 3 mm stainless wire lanyard and its independent girder clamp on the bottom flange tip; the
active gauge under its cover and the dummy gauge coupon on the flange top; the steel temperature
probe under its flange clip; and the cables and flange clips on the model's routes (BRP-DDR-004,
P10 and P11), cut to the girder section. Context is a section of the south (-Y) girder, an IPE 360
class section with root fillets, long enough for the girder clamp, with a strip of the timber deck.
Left out, as accepted on 2026-10-02: the north girder's gauge, the air probe, the FieldNode core and
the post (FieldNode has its own renders).
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.
A research prototype that supports but never replaces inspection by qualified engineers.

Axes as in model.py: X along the span (midspan at x = 0), Y across the bridge (the monitored girder
on -Y), Z up, with the soffit at z = g_z0.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Cylinder, Plane, Pos, RegularPolygon, Rot, Solid, Sphere, Vector,
                       extrude, fillet)
from model import PARAMS, derived, build_components

TITLE = "BridgePulse: clamp-on vibration and strain monitor for small bridges"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "accessory", "context"], "explode": False, "el": 24, "az": -52,
     "note": "Product render from the front right and above (about 24 deg elevation); sensor hub on its plate "
             "between the flanges of a girder section, on two clamped foot blocks with the jack screw above; boards "
             "and status light behind the lid window; wire lanyard from the pad eye to its own girder clamp at left"},
    {"name": "exploded", "groups": ["shell", "internal"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): lid with window, gasket, "
             "signal and accelerometer boards, hub base with glands and M12 plug, mounting plate, foot blocks, "
             "jaws and bolts, jack block and screw, lanyard pad eye and girder clamp, strain gauge and cover, "
             "dummy gauge coupon, steel temperature probe and its clip"},
    {"name": "detail", "groups": ["shell", "internal", "accessory", "context"], "explode": False, "el": 8, "az": -66,
     "note": "Detail from the front right, just above the bottom flange (about 8 deg elevation): boards behind "
             "the lid window, foot blocks and clamps on the flange below, cables on their flange clips"},
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


def _win(shape, x0, x1, y0, y1, z0_, z1_):
    """Part of `shape` inside an axis-aligned box (cables cut to the girder section)."""
    return shape & Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0_ + z1_) / 2) * Box(x1 - x0, y1 - y0, z1_ - z0_)


def product_parts(P=PARAMS):
    D = derived(P)
    C = build_components(P)
    L = 2 * (abs(P["lan_clamp_x"]) + 45)            # girder section long enough for the lanyard's girder clamp
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

    # penetrations in the bottom face, taken from model.py: two M16 gauge glands, two M12 probe
    # glands and the M12 5-pin panel connector, with the moulded plug of the FieldNode cable
    E_GL = (E_BASE[0], E_BASE[1], -40)
    add("Gauge cable glands, M16 nylon", C["glands"].shape, C_GLAND, "plastic", 1, "shell", E_GL)
    add("Probe glands, M12 nylon", C["probe_glands"].shape, C_GLAND, "plastic", 1, "shell", E_GL)
    add("M12 panel connector", C["connector"].shape, C_STEEL, "metal", 7, "shell", E_GL)
    m12_bot = hz0 - 14.0
    plug = _knurl_z(0, D["body_yc"], m12_bot - 8, 8.0, 16.0)
    add("M12 coupling nut", plug, C_STEEL, "metal", 7, "shell", (0, -110, -70))

    # ------------------------------------------------------------ 2 accelerometer board, 3 signal board (model.py)
    E_ACC, E_SIG = (0, -170, 30), (0, -240, 0)
    add("Accelerometer spacers", C["acc_spacers"].shape, C_STEEL, "metal", 2, "internal", E_ACC)
    add("Accelerometer board (ADXL355 class)", C["acc"].shape, C_PCB2, "plastic", 2, "internal", E_ACC)
    add("Signal board standoffs", C["sig_standoffs"].shape, C_BRASS, "metal", 3, "internal", E_SIG)
    add("Signal board with modules (RP2040 class, ADC, RS-485, microSD)", C["sig"].shape, C_PCB, "plastic", 3, "internal", E_SIG)
    sf = y0 - w - P["sig_standoff"] - P["sig_board"][1]          # component side of the signal board
    gcx = P["sig_xz"][0]
    led = _ycyl(gcx + 40, sf - 1.0, hzc + 28, 1.8, 2.0) + Pos(gcx + 40, sf - 2.0, hzc + 28) * Sphere(1.8)
    add("Status light (lit)", led, C_LED, "emissive", 3, "internal", E_SIG)
    add("Hub screws with sealing washers", C["hub_screws"].shape, C_STEEL, "metal", 1, "internal", E_BASE)

    # ------------------------------------------------------------ 4 mounting plate, foot clamps, jack (model.py)
    pt = P["plate_t"]
    pz1 = D["plate_z1"]
    add("Mounting plate, 6061 hard anodized", C["plate"].shape, C_ANOD, "metal", 4, "shell", (0, 0, 0))
    plab = _box(0, D["web_face"] - pt - 0.2, pz1 - 48, 50, 0.4, 14)
    add("Plate ID label", plab, C_LABEL, "paper", 4, "shell", (0, 0, 0))
    plk = (_box(-8, D["web_face"] - pt - 0.45, pz1 - 45, 24, 0.3, 3) + _box(-2, D["web_face"] - pt - 0.45, pz1 - 50, 34, 0.3, 1.6))
    add("Plate label print", plk, C_INK, "paper", 4, "shell", (0, 0, 0))
    E_FT, E_JAW, E_BOLT, E_JK = (0, -40, -40), (0, -40, -110), (0, -40, -175), (0, -40, 60)
    add("Foot blocks, hard anodized", C["feet"].shape, C_ANOD, "metal", 4, "shell", E_FT)
    add("Foot block cap screws", C["foot_screws"].shape, C_STEEL, "metal", 4, "shell", E_FT)
    add("Clamp jaws, zinc plated steel", C["jaws"].shape, C_ZINC, "metal", 4, "shell", E_JAW)
    add("Packers", C["packers"].shape, C_ZINC, "metal", 4, "shell", E_JAW)
    add("Clamp bolts, M10 stainless", C["foot_bolts"].shape, C_STEEL, "metal", 4, "shell", E_BOLT)
    add("Jack block, hard anodized", C["jack_block"].shape, C_ANOD, "metal", 4, "shell", E_JK)
    add("Jack block cap screws", C["jack_screws"].shape, C_STEEL, "metal", 4, "shell", E_JK)
    add("Jack screw and lock nut, M12 stainless", C["jack"].shape, C_STEEL, "metal", 4, "shell", (0, -40, 110))
    E_LAN = (-60, -120, 0)
    add("Lanyard pad eye and screws, stainless", C["pad_eye"].shape + C["pad_eye_screws"].shape, C_STEEL, "metal", 4, "shell", E_LAN)
    add("Lanyard, 3 mm stainless wire", C["lanyard"].shape, C_STEEL, "metal", 4, "accessory", E_LAN)
    add("Lanyard girder clamp, galvanized", C["lan_clamp"].shape, C_ZINC, "metal", 4, "shell", (-60, -120, -60))
    add("Girder clamp set screw and lock nut", C["lan_screw"].shape, C_STEEL, "metal", 4, "shell", (-60, -120, -60))

    # ------------------------------------------------------------ 5 strain gauges (south girder; the north is the same)
    gx_, gy_, gz_ = P["gauge_patch"]
    E_COV, E_GAU = (0, -330, -70), (0, -330, -25)
    cover = _box(0, gy, z0 - gz_ / 2, gx_, gy_, gz_)
    cover = _fillet_try(cover, _edges_par(cover, Axis.Z), [10.0, 6.0])
    cover = _fillet_try(cover, _bottom(cover), [2.5, 1.5])
    cover -= _box(0, gy, z0 - 0.25, 16, 10, 0.5)
    add("Strain gauge cover patch", cover, C_COVER, "rubber", 5, "shell", E_COV)
    add("Active foil strain gauge", _box(0, gy, z0 - 0.25, 15, 9, 0.5), C_FOIL, "plastic", 5, "shell", E_GAU)
    cx_, cy_, cz_ = P["coupon"]
    ccx, ccy = P["coupon_x"], gy - (tw / 2 + P["coupon_out"])
    E_CPN = (70, -60, 40)
    coupon = _box(ccx, ccy, z0 + tf + cz_ / 2, cx_, cy_, cz_)
    coupon = _fillet_try(coupon, _edges_par(coupon, Axis.Z), [3.0, 2.0])
    add("Dummy gauge steel coupon", coupon, C_ZINC, "metal", 5, "shell", E_CPN)
    ctop = z0 + tf + cz_
    add("Dummy foil strain gauge", _box(ccx, ccy, ctop + 0.25, 15, 9, 0.5), C_FOIL, "plastic", 5, "shell", (70, -60, 70))
    dcov = _box(ccx, ccy, ctop + 2.0, 26, 16, 3.0)
    dcov = _fillet_try(dcov, _edges_par(dcov, Axis.Z), [5.0, 3.0])
    dcov -= _box(ccx, ccy, ctop + 0.25, 16, 10, 0.5)
    add("Dummy gauge cover", dcov, C_COVER, "rubber", 5, "shell", (70, -60, 100))

    # ------------------------------------------------------------ 6 steel temperature probe under its flange clip
    add("Steel temperature probe, stainless sheath", C["steel_probe"].shape, C_STEEL, "metal", 6, "shell", (60, -70, 0))
    add("Probe flange clip, spring steel", C["probe_clip"].shape, C_ZINC, "metal", 6, "shell", (60, -70, 20))

    # ------------------------------------------------------------ 7 cables on the model.py routes, cut to the girder section
    win = (-L / 2, L / 2, -900, -500, z0 - 40, D["deck_top"] + 5)
    add("Sensor cables, shielded 4-core", _win(C["near_cable"].shape + C["far_cable"].shape, *win), C_CABLE, "rubber", 7, "accessory", (0, 0, 0))
    add("Probe lead", _win(C["probe_leads"].shape, *win), C_CABLE, "rubber", 6, "accessory", (0, 0, 0))
    add("M12 cable to the FieldNode core", _win(C["fn_cable"].shape, *win), C_CABLE, "rubber", 7, "accessory", (0, 0, 0))
    add("Spring-steel flange clips", _win(C["cable_clips"].shape, *win), C_ZINC, "metal", 7, "accessory", (0, 0, 0))

    # ------------------------------------------------------------ context: girder section and deck strip
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
