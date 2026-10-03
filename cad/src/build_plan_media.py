"""BridgePulse prototype build plan pictures (BRP-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|layouts|joints|steps|wiring ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py
(build_components), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/BRP-DWG-101 to 107        making sketches for the made and drilled components
    docs/05-build-plan/plate-holes.png     hole positions on the mounting plate (matplotlib)
    docs/05-build-plan/hub-holes.png       hole positions in the hub's base and bottom face (matplotlib)
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, derived, bridge_context, i_girder, fuse, lanyard_geometry  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-09-30"
DATE_P2 = "2026-10-02"
LAN = lanyard_geometry(P)
REPO = "github.com/BoujeeEnjinia1701/bridgepulse"
D = derived(P)
C = build_components(P)
CTX = bridge_context(P)
S = lambda *ks: fuse([C[k].shape for k in ks])  # noqa: E731
Z0 = P["g_z0"]
FT = D["flange_top"]

COL = {"plate": "#A8A29E", "feet": "#1D4ED8", "jaws": "#B45309", "packers": "#F59E0B", "bolt": "#111827",
       "jack_block": "#0E7490", "body": "#D1D5DB", "lid": "#E5E7EB", "glands": "#1F2937", "pglands": "#4B5563",
       "connector": "#D4A017", "spacers": "#9CA3AF", "acc": "#0F766E", "sig": "#2563EB", "patches": "#C2410C",
       "coupons": "#7C2D12", "probe": "#7C3AED", "lead": "#A78BFA", "cable": "#334155", "clips": "#64748B",
       "fieldnode": "#115E59", "bands": "#9CA3AF", "girder": "#B6BCC4", "post": "#B6BCC4", "lanyard": "#B91C1C"}


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def girder_seg(x0=-400, x1=400):
    return part("Girder offcut (bench rig)", i_girder(P, -P["gy"], x0, x1), COL["girder"])


def jnt(items, out, title, subtitle=None, elev=24, azim=-58, size=(8, 6), dpi=160):
    """Like build_views.joint, but each item may carry the 3D point its leader should end on:
    items are (Part, anchor or None). Parts left empty by a window are dropped."""
    import numpy as np
    items = [(p, a) for p, a in items if bv._has_volume(p.shape)]
    W, H = int(size[0] * dpi), int(size[1] * dpi * bv.PIC_HEIGHT)
    img, proj, verts = bv._raster([(p, p.color, p.alpha, (0, 0, 0)) for p, _ in items], elev, azim, W, H)
    fig, ax = bv._frame(size, dpi, title, subtitle)
    ax.imshow(img, interpolation="bilinear")
    pts = [np.asarray(a, float) if a is not None else bv._anchor(v) for (p, a), v in zip(items, verts)]
    bv._draw_labels(ax, proj, pts, [p.name for p, _ in items], W, H)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); bv.plt.close(fig)
    return out


def win(sh, x0, x1, y0, y1, z0_, z1_):
    import build123d as b
    return sh & (b.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0_ + z1_) / 2) * b.Box(x1 - x0, y1 - y0, z1_ - z0_))


# ----------------------------------------------------------------- named groups, in build order
def made():
    return {
        "plate": part("Mounting plate", C["plate"].shape, COL["plate"]),
        "feet": part("Foot blocks (2) and M6 screws", S("feet", "foot_screws"), COL["feet"]),
        "clamps": part("Jaws, packers, M10 bolts (2 sets)", S("jaws", "packers", "foot_bolts"), COL["jaws"]),
        "jack": part("Jack block, jack screw, M6 screws", S("jack_block", "jack", "jack_screws"), COL["jack_block"]),
        "body": part("Hub enclosure body, drilled", C["body"].shape, COL["body"]),
        "pens": part("Glands and panel connector", S("glands", "probe_glands", "connector"), COL["glands"]),
        "stand": part("Spacers and standoffs", S("acc_spacers", "sig_standoffs"), COL["spacers"]),
        "acc": part("Accelerometer board", C["acc"].shape, COL["acc"]),
        "sig": part("Signal board with modules", C["sig"].shape, COL["sig"]),
        "hub_screws": part("M5 hub screws, sealing washers (4)", C["hub_screws"].shape, COL["bolt"]),
        "patches": part("Active gauges under covers (2)", C["patches"].shape, COL["patches"]),
        "coupons": part("Dummy gauge coupons (2)", C["coupons"].shape, COL["coupons"]),
        "probes": part("Temperature probes (2) and clip", S("steel_probe", "air_probe", "probe_clip"), COL["probe"]),
        "lid": part("Hub lid", C["lid"].shape, COL["lid"]),
        "fieldnode": part("FieldNode core with long bands", S("fieldnode", "fn_bands"), COL["fieldnode"]),
        "lanyard": part("Pad eye, wire lanyard, girder clamp", S("pad_eye", "pad_eye_screws", "lanyard", "lan_clamp", "lan_screw"), COL["lanyard"]),
    }


# ----------------------------------------------------------------- overview
def overview():
    M = made()
    cab = win(S("near_cable", "far_cable", "probe_leads", "fn_cable", "cable_clips"), -160, 160, -760, -560, 1150, 1330)
    M["cables"] = part("Cables, leads, clips (cut short)", cab, COL["cable"])
    off = {"plate": (0, 0, 0), "feet": (0, -110, -170), "clamps": (0, -110, -330), "jack": (0, -110, 200),
           "body": (0, -260, 0), "pens": (0, -260, -150), "stand": (0, -370, 0), "acc": (0, -460, 20),
           "sig": (0, -540, -20), "hub_screws": (0, -620, 0), "patches": (-420, 0, -300), "coupons": (-420, 0, -120),
           "probes": (-120, -60, 330), "cables": (330, -40, -260), "lid": (0, -740, 0),
           "fieldnode": (520, 650, -1020), "lanyard": (-60, -420, -120)}
    order = ["plate", "feet", "clamps", "jack", "body", "pens", "stand", "acc", "sig", "hub_screws",
             "patches", "coupons", "probes", "cables", "lid", "fieldnode", "lanyard"]
    parts = []
    for k in order:
        p = M[k]
        if k in ("patches", "coupons"):
            p = part(p.name, win(p.shape, -200, 200, -800, -400, 1100, 1300), p.color)
        if k == "probes":
            p = part("Temperature probes (2, one shown) and clip", win(p.shape, -300, 100, -800, -600, 1100, 1500), p.color)
        p.explode = off[k]
        parts.append(p)
    return bv.overview(parts, OUT / "overview.png", "BridgePulse prototype: every component, pulled apart",
                       subtitle="Numbered in build order, seen from the front right and above. The FieldNode core (16) goes on the "
                                "post; the lanyard (17) runs to its own girder clamp",
                       elev=16, azim=-52, size=(11, 8.5), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets(only=None):
    import build123d as b
    M = made()
    g = girder_seg(-250, 250)
    base = dict(project="BridgePulse", date=DATE)
    out = []
    wf, pt = D["web_face"], P["plate_t"]
    pz0, pz1 = D["plate_z0"], D["plate_z1"]
    hzc = D["hub_zc"]
    sx, sz = P["hub_screws"]
    fz = D["foot_screw_z"]

    pex, pedz = P["pad_eye"]
    peh = P["pad_eye_size"][0] / 2 - 5
    # 101 mounting plate, laid flat in the drawing frame (front face toward the viewer)
    if only in (None, 101):
      out.append(bv.component_sheet(
        Part("Mounting plate", C["plate"].shape, COL["plate"]),
        [M["feet"], M["body"], M["jack"], part("Pad eye", S("pad_eye", "pad_eye_screws"), COL["lanyard"]), g],
        dwg_no="BRP-DWG-101", title="BridgePulse mounting plate: making sketch",
        material="6061 aluminium plate 8 mm, hard anodized after machining",
        view_shape=b.Pos(0, -(wf - pt / 2), -(pz0 + pz1) / 2) * C["plate"].shape, inset_view=(18, -60),
        notes=[f"Blank {P['plate_w']:.0f} x {D['plate_h']:.1f} x 8 mm: the girder's clear web height",
               "  ({:.1f} mm on IPE 360) less 22 mm at each end, to clear the root fillets.".format(D["clear"]),
               "Front face: the face the hub sits on. Heights from the bottom edge,",
               "  sideways from the centre line. All holes go right through.",
               f"Hub screws: four M5 tapped (drill 4.2) at {sx:.0f} each side,",
               f"  {hzc - sz - pz0:.1f} and {hzc + sz - pz0:.1f} up.",
               f"Foot block screws: four M6 tapped (drill 5.0) at {P['clamp_x'] - 10:.0f} and {P['clamp_x'] + 10:.0f}",
               f"  each side, {fz - pz0:.0f} up.",
               f"Jack block screws: two M6 tapped at 12 each side, {D['plate_h'] - P['tab'][2] / 2:.1f} up.",
               f"Pad eye screws: two M5 tapped at {abs(pex) - peh:.0f} and {abs(pex) + peh:.0f} left of centre,",
               f"  {D['plate_h'] - pedz:.1f} up (left side only).",
               "Deburr; break the edges 0.5 mm; hard anodize (it also insulates).",
               "Check: lay the foot blocks and jack block on it and look through each hole."],
        rev="P2", revisions=[("P1", "Making sketch for the prototype build plan", DATE, "AC"),
                             ("P2", "Pad eye holes replace the lanyard hole (BRP-DEC-001)", DATE_P2, "AC")],
        **{**base, "date": DATE_P2}))
    if only == 101:
        return out

    # 102 foot block, drawn at the right-hand clamp
    fb = win(C["feet"].shape, 0, 200, -800, -500, 1100, 1400)
    out.append(bv.component_sheet(
        Part("Foot block", fb, COL["feet"]), [part("Plate", win(C["plate"].shape, -110, 110, -700, -500, 1200, 1330), COL["plate"]),
                                              part("Clamp", win(S("jaws", "packers", "foot_bolts"), 0, 200, -800, -500, 1100, 1300), COL["jaws"]),
                                              part("Girder", win(CTX["girders"], -30, 180, -720, -560, 1180, 1330), COL["girder"])],
        dwg_no="BRP-DWG-102", title="BridgePulse foot block (make 2): making sketch",
        material="6061 aluminium flat bar 100 x 40 mm, hard anodized",
        view_shape=b.Pos(-P["clamp_x"], -(wf - pt), -FT) * fb, inset_view=(15, -35),
        notes=["Make two, both the same. Saw a 40 mm slice off 100 x 40 mm bar and",
               "  square it to 96 long, 40 tall and 40 wide.",
               "Saw out a step 66 long and 28 deep, leaving a tall end 30 long and",
               "  a tail 12 thick. The tall end's back face goes on the plate.",
               "File a 12 x 12 mm 45 degree chamfer along the bottom of the back face:",
               "  it keeps the block off the girder's root fillet.",
               f"Tall end: two 6.6 mm holes through, 10 each side of centre, {fz - FT:.0f} up;",
               "  counterbore 11 mm, 6.5 deep, from the front for M6 cap screws.",
               f"Tail: one 11 mm hole, {P['foot_over'] - P['bolt_out']:.0f} from its end, on the centre line.",
               "Fit: back face flat on the plate front, bottom on the flange top,",
               "  tail out past the flange tip. Two M6 x 30 screws into the plate.",
               "Check: on a flange offcut it sits flat with no rock at the fillet."],
        **base))

    # 103 clamp jaw (with the packer described)
    jw = win(C["jaws"].shape, 0, 200, -800, -500, 1100, 1300)
    out.append(bv.component_sheet(
        Part("Clamp jaw", jw, COL["jaws"]), [part("Foot block", win(C["feet"].shape, 0, 200, -800, -500, 1100, 1300), COL["feet"]),
                                             part("Flange", win(CTX["girders"], 20, 140, -720, -560, 1150, 1260), COL["girder"]),
                                             part("Bolt", win(C["foot_bolts"].shape, 0, 200, -800, -500, 1100, 1300), COL["bolt"]), part("Packer", win(C["packers"].shape, 0, 200, -800, -500, 1100, 1300), COL["packers"])],
        dwg_no="BRP-DWG-103", title="BridgePulse clamp jaw and packer (make 2 each): making sketch",
        material="Steel flat bar 40 x 10 mm, zinc plated; packer: steel tube 16 mm outside",
        view_shape=b.Pos(-P["clamp_x"], -D["tip"], -Z0) * jw, inset_view=(-25, -40),
        notes=["Jaw: cut two 45 mm lengths of 40 x 10 mm steel flat bar; deburr.",
               f"Drill 8.5 mm and tap M10 right through, {P['foot_over'] - P['bolt_out']:.0f} from one end, on the centre line.",
               "Break the edges; zinc plate or paint with zinc-rich primer.",
               "Packer: cut two lengths of steel tube, 16 mm outside, 10.5 mm or more",
               f"  inside, {P['girder'][2] - 0.5:.1f} long: the flange thickness less 0.5 mm.",
               "  Measure the real flange first and cut to suit; square the ends.",
               "Fit: the jaw goes under the flange, 22 mm in from the tip, its tapped",
               "  end out past the tip. The packer stands on the jaw beside the tip.",
               "  The M10 x 35 bolt comes down through the foot block tail and the",
               "  packer into the jaw; it must not stand out below the jaw.",
               "Check: the bolt runs into the jaw by hand, and its tip stops",
               "  1 mm or more short of the jaw's underside."],
        **base))

    # 104 jack block
    jb = C["jack_block"].shape
    out.append(bv.component_sheet(
        Part("Jack block", jb, COL["jack_block"]), [part("Plate", win(C["plate"].shape, -110, 110, -700, -500, 1420, 1600), COL["plate"]),
                                                    part("Girder", win(CTX["girders"], -120, 120, -720, -560, 1420, 1560), COL["girder"]),
                                                    part("Jack screw", C["jack"].shape, COL["bolt"])],
        dwg_no="BRP-DWG-104", title="BridgePulse jack block: making sketch",
        material="6061 aluminium flat bar 40 x 30 mm",
        view_shape=b.Pos(0, -(wf - pt), -(pz1 - P["tab"][2] / 2)) * jb, inset_view=(10, -50),
        notes=["Cut 30 mm off 40 x 30 mm bar: a block 40 wide, 30 deep, 30 tall.",
               "  The 40 x 30 face that goes on the plate is the back face.",
               f"Jack hole: drill 10.2 mm top to bottom, {P['jack_out']:.0f} from the back face, on the centre",
               "  line, square to the top; tap M12 the full 30 mm.",
               "Fixing holes: two 6.6 mm holes front to back, 12 each side of centre,",
               "  half way up; counterbore 11 mm, 6.5 deep, from the front.",
               "Fit: back face on the plate front, top flush with the plate's top edge;",
               "  two M6 x 30 cap screws into the plate.",
               "The M12 x 70 jack screw goes up through it, head below, lock nut",
               "  under the block; its end bears on the top flange 22 mm above.",
               "Check: the jack screw turns freely through the full thread."],
        **base))

    # 105 hub enclosure, drilled; drawn base down so the front view shows the base holes
    body = C["body"].shape
    view = b.Pos(0, 0, 0) * b.Rot(-90, 0, 0) * b.Pos(0, -D["hub_y0"], -hzc) * body
    out.append(bv.component_sheet(
        Part("Hub enclosure body", body, COL["body"]), [M["plate"], M["pens"]],
        dwg_no="BRP-DWG-105", title="BridgePulse hub enclosure: drilling sketch",
        material="Bought die-cast aluminium box, IP67, 170 x 64 x 110 mm",
        view_shape=view, inset_view=(20, -65),
        notes=["Drawn lying on its back with the lid off: the top view looks into the box",
               "  at the base; the front view shows the bottom face.",
               "Base, from the base's centre: four 5.5 mm holes at 72 each side, 42 above",
               "  and below (the hub screws).",
               "Base: eight 3.2 mm holes for the board spacers and standoffs, countersunk",
               "  outside so the M3 heads sit flush (positions in the hub holes picture).",
               "Bottom face, on its centre line, sideways from the centre:",
               "  60 left: 12.5 mm (steel probe gland, M12)",
               "  30 left and 30 right: 16.5 mm (gauge glands, M16)",
               "  centre: 16.5 mm (M12 panel connector, M16 thread)",
               "  60 right: 12.5 mm (air probe gland, M12). Left and right as seen from the lid.",
               "Deburr inside and out; clean the lid gasket groove of chips."],
        **base))

    # 106 dummy gauge coupon
    cp = win(C["coupons"].shape, -200, 200, -800, -400, 1100, 1300)
    out.append(bv.component_sheet(
        Part("Dummy gauge coupon", cp, COL["coupons"]), [part("Girder", win(CTX["girders"], -120, 140, -720, -560, 1180, 1330), COL["girder"]),
                                                          part("Feet", win(C["feet"].shape, -120, 140, -720, -560, 1180, 1330), COL["feet"]),
                                                          part("Plate", win(C["plate"].shape, -120, 140, -720, -560, 1180, 1330), COL["plate"])],
        dwg_no="BRP-DWG-106", title="BridgePulse dummy gauge coupon (make 2): making sketch",
        material="Steel flat bar 25 x 6 mm, the same steel grade as the girder if known",
        view_shape=b.Pos(-P["coupon_x"], D["web_face"] + P["coupon_out"], -FT) * cp, inset_view=(30, -60),
        notes=["Cut two 40 mm lengths of 25 x 6 mm steel flat bar.",
               "Grind one 40 x 25 face flat and clean to bright metal; this is where",
               "  the dummy gauge goes. Round the edges lightly.",
               "Bond a gauge of the same type and batch as the active gauge to the",
               "  middle of the bright face, the same way round as the active gauge.",
               "Solder its leads, coat it with the same coating as the active gauge,",
               "  and fit a cover patch.",
               "Fit: set it on the flange top, its centre 35 out from the web face,",
               "  on a bed of neutral-cure silicone, so it takes the steel's",
               "  temperature but none of its strain. Never glue it rigidly.",
               "Check: the coupon can be lifted by hand once the silicone has cured."],
        **base))

    # 107 temperature probe (made: potted sensor in a sheath)
    pr = C["steel_probe"].shape
    out.append(bv.component_sheet(
        Part("Temperature probe", pr, COL["probe"]), [part("Girder", win(CTX["girders"], -230, -30, -720, -560, 1180, 1300), COL["girder"]), part("Flange clip", C["probe_clip"].shape, COL["clips"]), part("Lead", win(C["probe_leads"].shape, -230, -30, -720, -560, 1180, 1330), COL["lead"])],
        dwg_no="BRP-DWG-107", title="BridgePulse temperature probe (make 2): making sketch",
        material="Stainless sheath 7 x 60 mm, TMP1826 class sensor on a carrier, potting epoxy",
        view_shape=b.Pos(-P["t_steel_x"], -(D["tip"] + 3.5 + 6.5), -(FT + 3.5)) * pr, inset_view=(25, -70),
        notes=["Make two, both the same. Solder the sensor carrier to a 3-core sealed",
               "  outdoor lead (1-Wire: data, ground and supply), 2 m for the steel",
               "  probe and 3 m for the air probe.",
               "Push the carrier to the closed end of the sheath, sensor face down,",
               "  with a dab of thermal paste between the sensor and the sheath end.",
               "Fill the sheath with potting epoxy from the closed end up, with no",
               "  air pockets; fit heat-shrink with adhesive over the sheath mouth.",
               "Steel probe: lies on the bottom flange top, 6.5 from the tip, held by",
               "  a spring-steel flange clip with thermal paste under it.",
               "Air probe: hangs on its lead between the girders, in shade.",
               "Check each probe in ice water: 0 degC within 0.5 degC (R5)."],
        **base))
    return out


# ----------------------------------------------------------------- hole layouts
def layouts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    INK, MUT, AC = "#111827", "#4B5563", "#0F766E"
    res = []
    pw, ph = P["plate_w"], D["plate_h"]
    pz0 = D["plate_z0"]
    hzc = D["hub_zc"]
    sx, sz = P["hub_screws"]
    fz = D["foot_screw_z"] - pz0
    jz = ph - P["tab"][2] / 2
    holes = ([(x, hzc - pz0 + dz, 5.0, "M5 tapped") for x in (-sx, sx) for dz in (-sz, sz)]
             + [(s * (P["clamp_x"] + dx), fz, 6.0, "M6 tapped") for s in (-1, 1) for dx in (-10, 10)]
             + [(dx, jz, 6.0, "M6 tapped") for dx in (-12, 12)]
             + [(P["pad_eye"][0] + dx, ph - P["pad_eye"][1], 5.0, "pad eye") for dx in (-(P["pad_eye_size"][0] / 2 - 5), P["pad_eye_size"][0] / 2 - 5)])
    fig = plt.figure(figsize=(9.5, 10), dpi=150)
    ax = fig.add_axes([0.1, 0.08, 0.6, 0.82]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(Rectangle((-pw / 2, 0), pw, ph, fc="#F5F5F4", ec=INK, lw=1.2))
    ax.plot([0, 0], [-4, ph + 6], color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    # outlines of what sits on the front face
    ax.add_patch(Rectangle((-85, hzc - 55 - pz0), 170, 110, fc="none", ec="#94A3B8", lw=0.8, ls="--"))
    ax.text(0, hzc - pz0 + 5, "hub base sits here", ha="center", fontsize=7.5, color="#64748B")
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * P["clamp_x"] - 20, 0), 40, D["flange_top"] + P["foot"][1] - pz0, fc="none", ec="#94A3B8", lw=0.8, ls="--"))
    ax.add_patch(Rectangle((-20, ph - 30), 40, 30, fc="none", ec="#94A3B8", lw=0.8, ls="--"))
    ax.text(0, ph - 41, "jack block", ha="center", fontsize=7, color="#64748B")
    pbx, _, pbh, _ = P["pad_eye_size"]
    ax.add_patch(Rectangle((P["pad_eye"][0] - pbx / 2, ph - P["pad_eye"][1] - pbh / 2), pbx, pbh, fc="none", ec="#94A3B8", lw=0.8, ls="--"))
    ax.text(P["pad_eye"][0], ph - P["pad_eye"][1] - pbh / 2 - 5, "pad eye", ha="center", va="top", fontsize=7, color="#64748B")
    ax.text(P["clamp_x"], 26, "foot block", ha="center", fontsize=7, color="#64748B")
    xs, zs = set(), set()
    for x, z, dia, kind in holes:
        ax.add_patch(plt.Circle((x, z), dia / 2, fc="white", ec=INK, lw=1))
        ax.plot([x - dia / 2 - 2, x + dia / 2 + 2], [z, z], color=MUT, lw=0.4); ax.plot([x, x], [z - dia / 2 - 2, z + dia / 2 + 2], color=MUT, lw=0.4)
        if kind != "pad eye":
            xs.add(round(abs(x), 1))
        zs.add(round(z, 1))
    for xx in [h[0] for h in holes if h[3] == "pad eye"]:
        ax.plot([xx, xx], [0, -7], color=AC, lw=0.4, ls=":")
    pe_xs = sorted(abs(h[0]) for h in holes if h[3] == "pad eye")
    ax.text(-(pe_xs[0] + pe_xs[1]) / 2, -10, f"{pe_xs[0]:g} and {pe_xs[1]:g}\n(left only)", ha="center", va="top", fontsize=7.5, color=AC)
    for i, x in enumerate(sorted(xs)):
        yl = -10 - 9 * (i % 2)
        ax.plot([x, x], [0, yl + 3], color=AC, lw=0.4, ls=":")
        ax.text(x, yl, f"{x:g}", ha="center", va="top", fontsize=7.5, color=AC)
    ax.text(0, -32, "sideways from the centre line, mm (pairs are the same each side)", ha="center", fontsize=8, color=MUT)
    for i, z in enumerate(sorted(zs)):
        xl = -pw / 2 - 6 - 16 * (i % 2)
        ax.plot([xl + 2, -pw / 2], [z, z], color=AC, lw=0.4, ls=":")
        ax.text(xl, z, f"{z:g}", ha="right", va="center", fontsize=7.5, color=AC)
    ax.text(-pw / 2 - 44, ph / 2, "up from the bottom edge, mm", rotation=90, ha="center", va="center", fontsize=8, color=MUT)
    ax.set_xlim(-pw / 2 - 50, pw / 2 + 5); ax.set_ylim(-38, ph + 8)
    fig.text(0.04, 0.975, "Mounting plate: hole positions", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 0.95, f"Seen from the front (the face the hub sits on). Plate {pw:.0f} x {ph:.1f} x 8 mm. Figures in mm, from the model.",
             fontsize=8.5, color=MUT, va="top")
    key = ["Hub screws: M5 tapped,", "  drill 4.2 (4 holes)", "Foot block screws: M6", "  tapped, drill 5.0 (4)",
           "Jack block screws: M6", "  tapped, drill 5.0 (2)", "Pad eye screws: M5", "  tapped, drill 4.2 (2),", "  left side only", "",
           "Every hole goes right", "through. The back face lies", "flat on the girder web:", "no screw may stand out", "behind it."]
    fig.text(0.72, 0.86, "What each hole is", fontsize=9, fontweight="bold", color=INK, va="top")
    for i, t in enumerate(key):
        fig.text(0.72, 0.83 - i * 0.024, t, fontsize=8, color=INK, va="top")
    fig.text(0.04, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.96, 0.015, REPO, fontsize=7, color=AC, ha="right", family="monospace")
    fig.savefig(OUT / "plate-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "plate-holes.png")

    # hub: base (outside) and bottom face
    hx, hy, hz = P["hub"]
    fig = plt.figure(figsize=(11, 7.6), dpi=150)
    ax = fig.add_axes([0.04, 0.33, 0.6, 0.55]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(Rectangle((-hx / 2, -hz / 2), hx, hz, fc="#F3F4F6", ec=INK, lw=1.2))
    ax.plot([0, 0], [-hz / 2 + 3, hz / 2 - 3], color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    ax.plot([-hx / 2 + 3, hx / 2 - 3], [0, 0], color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    pts = []
    for x in (-sx, sx):
        for z in (-sz, sz):
            pts.append((-x, z, 5.5, "M5"))       # seen from outside the base the left and right swap
    ax_, _, az_ = P["acc_board"]; acx, acz = P["acc_xz"]
    gx_, _, gz_ = P["sig_board"]; gcx, gcz = P["sig_xz"]
    for xx, zz, w_, h_ in ((acx, acz, ax_, az_), (gcx, gcz, gx_, gz_)):
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                pts.append((-(xx + s1 * (w_ / 2 - 4)), zz + s2 * (h_ / 2 - 4), 3.2, "M3"))
        ax.add_patch(Rectangle((-(xx + w_ / 2), zz - h_ / 2), w_, h_, fc="none", ec="#94A3B8", lw=0.7, ls="--"))
    ax.text(-acx, acz + az_ / 2 + 3, "accelerometer board", ha="center", fontsize=6.8, color="#64748B")
    ax.text(-gcx, gcz + gz_ / 2 + 3, "signal board", ha="center", fontsize=6.8, color="#64748B")
    for x, z, dia, k in pts:
        ax.add_patch(plt.Circle((x, z), dia / 2, fc="white", ec=INK, lw=1))
        if k == "M5":
            ax.text(x, z - 7 if z > 0 else z + 7, f"5.5\n{x:+g}, {z:+g}", ha="center", va="top" if z > 0 else "bottom",
                    fontsize=6.5, color=AC, linespacing=1.1)
    ax.text(0, -hz / 2 - 3, "Base, seen from outside (the face that goes on the plate): left and right are\nreversed from the lid side; + is to the right in this view.",
            ha="center", va="top", fontsize=7.5, color=MUT)
    xs3 = sorted({round(x, 1) for x, z, d_, k in pts if k == "M3"})
    zs3 = sorted({round(z, 1) for x, z, d_, k in pts if k == "M3"})
    ax.text(0, -hz / 2 - 25, "M3 countersunk holes (3.2): across " + ", ".join(f"{v:g}" for v in xs3) + "; up "
            + ", ".join(f"{v:+g}" for v in zs3), ha="center", fontsize=7.2, color=AC)
    ax.set_xlim(-hx / 2 - 8, hx / 2 + 8); ax.set_ylim(-hz / 2 - 32, hz / 2 + 6)
    # bottom face
    bx = fig.add_axes([0.04, 0.06, 0.6, 0.2]); bx.set_aspect("equal"); bx.set_axis_off()
    dd = hy - P["lid_t"]
    bx.add_patch(Rectangle((-hx / 2, 0), hx, dd, fc="#F3F4F6", ec=INK, lw=1.2))
    bx.add_patch(Rectangle((-hx / 2, dd), hx, P["lid_t"], fc="white", ec=MUT, lw=0.8, ls="--"))
    names = {"g16": ("gauge gland", 16.5), "g12": ("probe gland", 12.5), "m12": ("connector", 16.5)}
    for k, (x, kind) in P["pens"].items():
        nm, dia = names[kind]
        bx.add_patch(plt.Circle((x, dd / 2), dia / 2, fc="white", ec=INK, lw=1))
        bx.text(x, dd + P["lid_t"] + 2, f"{dia:g}\n{x:+g}", ha="center", va="bottom", fontsize=6.5, color=AC, linespacing=1.1)
    bx.text(0, -4, "Bottom face, seen from below, base edge at the bottom; + to the right as seen from the lid side.\n"
            f"Holes on the face's centre line, {dd / 2:g} from the base.", ha="center", va="top", fontsize=7.5, color=MUT)
    bx.set_xlim(-hx / 2 - 8, hx / 2 + 8); bx.set_ylim(-20, dd + P["lid_t"] + 22)
    fig.text(0.03, 0.97, "Hub enclosure: holes in the base and the bottom face", fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.935, "Figures in mm from the model, measured from the centre lines of each face.", fontsize=8.5, color=MUT, va="top")
    key = ["Base", "  4 x 5.5: hub screws to the plate", "  8 x 3.2, countersunk outside:", "  board spacers and standoffs", "",
           "Bottom face (from the lid side)", "  60 left: steel probe gland, M12", "  30 left: near gauge gland, M16",
           "  centre: M12 panel connector", "  30 right: far gauge gland, M16", "  60 right: air probe gland, M12", "",
           "Seal each countersunk M3 with", "thread sealant: the plate covers", "the heads once the hub is on."]
    for i, t in enumerate(key):
        fig.text(0.68, 0.86 - i * 0.04, t, fontsize=8.3, color=INK, va="top", fontweight="bold" if t in ("Base", "Bottom face (from the lid side)") else None)
    fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.97, 0.015, REPO, fontsize=7, color=AC, ha="right", family="monospace")
    fig.savefig(OUT / "hub-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "hub-holes.png")
    return res


# ----------------------------------------------------------------- joints
def joints():
    out = []
    G = i_girder(P, -P["gy"], -400, 400)
    cx = P["clamp_x"]
    # 01 foot block over the root fillet: cut through an M6 screw, seen along the span
    wf, tip = D["web_face"], D["tip"]
    fz = D["foot_screw_z"]
    box_ = (cx - 10, cx + 10, -720, -590, 1185, 1265)
    out.append(jnt([
        (part("Girder web, root fillet and flange", win(G, *box_), COL["girder"]), (cx + 10, wf + 4, 1235)),
        (part("Mounting plate, on the web", win(C["plate"].shape, *box_), COL["plate"]), (cx + 10, wf - 4, 1258)),
        (part("Foot block; its chamfer clears the fillet", win(C["feet"].shape, *box_), COL["feet"]), (cx + 10, wf - 22, 1220)),
        (part("M6 cap screw into the plate", win(C["foot_screws"].shape, *box_), COL["bolt"]), (cx + 10, wf - 20, fz)),
                (part("Jaw under the flange", win(C["jaws"].shape, *box_), COL["jaws"]), (cx + 10, -680, 1195))],
        OUT / "joint-01.png", "Joint 1: foot block, plate and bottom flange (cut through an M6 screw)",
        subtitle="Seen along the span. The plate stops 22 mm above the flange; the block's chamfer clears the root fillet",
        elev=4, azim=10, size=(8, 6)))
    # 02 jaw, packer and bolt at the flange tip, cut through the bolt
    yb = D["bolt_y"]
    box_ = (cx - 25, cx, -715, -650, 1180, 1240)
    out.append(jnt([
        (part("Bottom flange", win(G, *box_), COL["girder"]), (cx, -665, 1206)),
        (part("Foot block tail", win(C["feet"].shape, *box_), COL["feet"]), (cx, -665, 1219)),
        (part("Packer, flange thickness less 0.5 mm", win(C["packers"].shape, *box_), COL["packers"]), (cx, yb - 6.5, 1206)),
        (part("Steel jaw, tapped M10", win(C["jaws"].shape, *box_), COL["jaws"]), (cx, -675, 1195)),
        (part("M10 bolt and washer", win(C["foot_bolts"].shape, *box_), COL["bolt"]), (cx, yb, 1230))],
        OUT / "joint-02.png", "Joint 2: the clamp at the flange tip (cut through the bolt)",
        subtitle="Tightening the bolt pulls the jaw up under the flange and the tail down on top; nothing below the jaw",
        elev=2, azim=12, size=(8, 6)))
    # 03 jack block and jack screw under the top flange, cut through the screw
    jy = D["jack_y"]
    pz1 = D["plate_z1"]
    box_ = (-30, 0, -660, -590, 1460, 1560)
    out.append(jnt([
        (part("Top flange and web", win(G, *box_), COL["girder"]), (0, -640, 1553)),
        (part("Mounting plate", win(C["plate"].shape, *box_), COL["plate"]), (0, wf - 4, 1480)),
        (part("Jack block, tapped M12", win(C["jack_block"].shape, *box_), COL["jack_block"]), (0, -645, 1500)),
        (part("M12 jack screw", win(C["jack"].shape, *box_), COL["bolt"]), (0, jy, 1536)),
        (part("Lock nut and screw head under the block", win(C["jack"].shape, -30, 0, -660, -590, 1460, pz1 - 30), COL["bolt"]), (0, jy - 6, 1488))],
        OUT / "joint-03.png", "Joint 3: jack block and jack screw under the top flange (cut through the screw)",
        subtitle="The screw bears on the flange 26 mm out from the web, clear of the root fillet; two M6 screws hold the block",
        elev=8, azim=8, size=(8, 6)))
    # 04 hub base on the plate, cut through a hub screw
    zs = D["hub_zc"] - P["hub_screws"][1]
    sx_ = P["hub_screws"][0]
    y0 = D["hub_y0"]
    box_ = (40, sx_, -690, -595, zs - 25, zs + 30)
    out.append(jnt([
        (part("Girder web", win(G, *box_), COL["girder"]), (sx_, wf + 4, zs + 25)),
        (part("Mounting plate, tapped M5", win(C["plate"].shape, *box_), COL["plate"]), (sx_, wf - 4, zs + 20)),
        (part("Hub base and bottom wall", win(C["body"].shape, *box_), COL["body"]), (sx_, y0 - 2, zs + 22)),
        (part("Lid", win(C["lid"].shape, *box_), COL["lid"]), (sx_, D["hub_y1"] + 3, zs + 15)),
        (part("M5 screw, bonded sealing washer", win(C["hub_screws"].shape, *box_), COL["bolt"]), (sx_, y0 - 7, zs)),
        (part("Probe gland nut on the floor", win(C["probe_glands"].shape, *box_), COL["pglands"]), (sx_ - 12, D["body_yc"], D["hub_z0"] + 6))],
        OUT / "joint-04.png", "Joint 4: hub base on the plate (cut through the lower right hub screw)",
        subtitle="The screw goes in from inside the box, sealing washer under its head; its tip stops 2 mm short of the web",
        elev=8, azim=12, size=(8, 6)))
    # 05 bottom face from below
    hz0 = D["hub_z0"]
    byc = D["body_yc"]
    box_ = (-90, 90, -690, -600, hz0 - 25, hz0 + 10)
    out.append(jnt([
        (part("Hub bottom face", win(S("body", "lid"), *box_), COL["body"]), (-75, byc, hz0)),
        (part("Gauge gland, M16 (2)", win(C["glands"].shape, *box_), COL["glands"]), (30, byc, hz0 - 16)),
        (part("Probe gland, M12 (2)", win(C["probe_glands"].shape, *box_), COL["pglands"]), (60, byc, hz0 - 14)),
        (part("M12 5-pin panel connector", win(C["connector"].shape, *box_), COL["connector"]), (0, byc - 8, hz0 - 14)),
        (part("Mounting plate", win(C["plate"].shape, *box_), COL["plate"]), (-85, D["web_face"] - 8, hz0 - 15))],
        OUT / "joint-05.png", "Joint 5: the hub's bottom face, seen from below and in front",
        subtitle="Five penetrations in one row: probe, gauge, connector, gauge, probe; 9 mm or more between them",
        elev=-35, azim=-40, size=(8, 6)))
    # 06 gauge under the flange and dummy coupon on top, cut across the girder at midspan
    box_ = (-10, 20, -700, -560, 1185, 1262)
    yco = -(P["gy"] + P["girder"][3] / 2 + P["coupon_out"])
    out.append(jnt([
        (part("Bottom flange, root fillet and web", win(G, *box_), COL["girder"]), (20, -598, 1240)),
        (part("Active gauge under its cover", win(C["patches"].shape, *box_), COL["patches"]), (20, -600, 1196)),
        (part("Dummy coupon on silicone", win(C["coupons"].shape, *box_), COL["coupons"]), (20, yco, 1217)),
        (part("Mounting plate (stops above the fillet)", win(C["plate"].shape, *box_), COL["plate"]), (20, wf - 4, 1250))],
        OUT / "joint-06.png", "Joint 6: active gauge and dummy coupon (cut across the south girder at midspan)",
        subtitle="The active gauge is bonded under the flange on the girder's centre line; the coupon only rests on silicone",
        elev=6, azim=10, size=(8, 6)))
    # 07 steel probe and its clip at the flange tip
    tx = P["t_steel_x"]
    box_ = (tx - 40, tx + 45, -705, -650, 1190, 1230)
    out.append(bv.joint([
        part("Bottom flange", win(G, *box_), COL["girder"]),
        part("Steel temperature probe", win(C["steel_probe"].shape, *box_), COL["probe"]),
        part("Spring-steel flange clip", win(C["probe_clip"].shape, *box_), COL["clips"]),
        part("Probe lead", win(C["probe_leads"].shape, *box_), COL["lead"])],
        OUT / "joint-07.png", "Joint 7: steel temperature probe on the bottom flange",
        subtitle="Seen from the front, below the deck. The clip pushes the sheath down on a smear of thermal paste",
        elev=25, azim=-60, size=(8, 6)))
    # 08 cables at the flange tip, with a clip
    nx = P["cable_x"]
    box_ = (nx - 30, nx + 30, -705, -575, 1180, 1290)
    out.append(bv.joint([
        part("Bottom flange and web", win(G, *box_), COL["girder"]),
        part("Near gauge cable", win(C["near_cable"].shape, *box_), COL["cable"]),
        part("Flange clip and cable tie", win(C["cable_clips"].shape, *box_), COL["clips"]),
        part("Gauge cover", win(C["patches"].shape, *box_), COL["patches"])],
        OUT / "joint-08.png", "Joint 8: gauge cable round the flange tip",
        subtitle="Seen from below and in front. The cable runs 2 mm under the flange and is tied to a push-on flange clip",
        elev=-30, azim=-55, size=(8, 6)))
    # 09 FieldNode plate on the square post, cut at the lower band and seen from above
    post = CTX["post"]
    zb = D["fn_z0"] + P["fn_band_dz"][0]
    pyc, fb = D["post_y"], D["fn_back"]
    box_ = (-110, 110, -830, -720, zb - 8, zb + 6)
    out.append(jnt([
        (part("Handrail post, 50 mm square", win(post, *box_), COL["post"]), (-20, pyc, zb + 6)),
        (part("FieldNode back plate (slot each side)", win(C["fieldnode"].shape, *box_), COL["fieldnode"]), (-80, fb + 1.5, zb + 6)),
        (part("Long band clamp, round the post", win(C["fn_bands"].shape, *box_), "#475569"), (25.4, pyc, zb + 6)),
        (part("Band across the plate front", win(C["fn_bands"].shape, -60, 60, -810, -802, zb - 8, zb + 6), "#475569"), (45, fb - 0.4, zb + 6)),
        (part("Worm-drive housing behind the post", win(C["fn_bands"].shape, -15, 15, -748, -720, zb - 8, zb + 6), "#334155"), (0, pyc + 33, zb + 6))],
        OUT / "joint-09.png", "Joint 9: FieldNode on the square post (cut at the lower band, seen from above)",
        subtitle="V-blocks left off: the back plate bears flat on the post; the band goes round the post and through both slots",
        elev=88, azim=-90, size=(8, 6)))
    # 10 lanyard girder clamp on the bottom flange tip, with the lanyard's thimble eye
    lcx = P["lan_clamp_x"]
    tip = D["tip"]
    box_ = (lcx - 60, lcx + 60, -725, -600, 1180, 1290)
    ss_y = tip + 18
    out.append(jnt([
        (part("Bottom flange", win(G, *box_), COL["girder"]), (lcx + 50, -640, FT)),
        (part("Girder clamp, hooked on the flange tip", win(C["lan_clamp"].shape, *box_), COL["lanyard"]), (lcx - 20, tip - 5, FT + 12)),
        (part("Set screw and lock nut, on the flange top", win(C["lan_screw"].shape, *box_), COL["bolt"]), (lcx, ss_y, FT + 33)),
        (part("Wire lanyard, thimble eye round the clamp's eye", win(C["lanyard"].shape, *box_), "#475569"), (lcx, LAN["cl_bar_y"] - 5.5, LAN["cl_eye_z"] + 12))],
        OUT / "joint-10.png", "Joint 10: lanyard girder clamp on the bottom flange",
        subtitle=f"Hooked on the flange tip {LAN['clear_x']:.0f} mm along the span from the nearer foot clamp; nothing is drilled",
        elev=18, azim=-60, size=(8, 6)))
    return out


# ----------------------------------------------------------------- assembly steps
def steps():
    M = made()
    out = []
    g = girder_seg(-320, 320)

    def st(n, done, new, title, sub, **kw):
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    def mv(p, e):
        return Part(p.name, p.shape, p.color, None, tuple(e), p.alpha)

    pl = M["plate"]
    st(1, [pl], [mv(M["feet"], (0, -90, 0))], "foot blocks onto the plate",
       "Back face of each block on the plate's front, chamfer down; two M6 x 30 cap screws each", elev=15, azim=-55)
    import build123d as b
    jack_down = part("Jack block, jack screw (wound down), M6 screws",
                     S("jack_block", "jack_screws") + b.Pos(0, 0, -24) * C["jack"].shape, COL["jack_block"])
    st(2, [pl, M["feet"]], [mv(jack_down, (0, -90, 0))], "jack block and jack screw onto the plate",
       "Top flush with the plate's top edge; two M6 x 30 screws. Wind the jack screw down below the block top",
       elev=15, azim=-55, label_done=False)
    st(3, [M["body"]], [mv(M["pens"], (0, 0, -70)), mv(M["stand"], (0, -110, 0))],
       "glands, connector, spacers and standoffs into the hub",
       "Penetrations from below, seal outside, nut inside. Spacers inside on M3 countersunk screws from outside the base",
       elev=-12, azim=-60, label_done=False)
    st(4, [M["body"], M["pens"], M["stand"]], [mv(M["acc"], (0, -150, 0)), mv(M["sig"], (0, -150, 0))],
       "boards into the hub, then wire them",
       "Accelerometer board on its four spacers, signal board on its standoffs; wire as the wiring diagram shows",
       elev=48, azim=-75, label_done=False)
    mount = [pl, M["feet"], part("Jack block", S("jack_block", "jack_screws") + b.Pos(0, 0, -24) * C["jack"].shape, COL["jack_block"])]
    st(5, [g], [mv(part("Plate with foot blocks and jack block", S("plate", "feet", "foot_screws", "jack_block", "jack_screws") + b.Pos(0, 0, -24) * C["jack"].shape, "#0F766E"), (0, -160, 0))],
       "plate onto the girder",
       "Back of the plate flat on the web, foot blocks standing on the bottom flange, midway along the span",
       elev=15, azim=-60)
    st(6, [g] + mount, [mv(part("Jaws and packers", S("jaws", "packers"), COL["jaws"]), (0, 0, -70)),
                        mv(part("M10 bolts", C["foot_bolts"].shape, COL["bolt"]), (0, 0, 70))],
       "clamp the foot blocks to the flange",
       "Jaw under the flange, packer on the jaw beside the tip, bolt down through tail and packer; snug only",
       elev=-12, azim=-50, label_done=False)
    clamps = part("Clamps", S("jaws", "packers", "foot_bolts"), COL["jaws"])
    wtop = (-130, 130, -720, -480, 1440, 1562)
    st(7, [part("Girder, top flange", win(g.shape, *wtop), COL["girder"]), part("Plate", win(pl.shape, *wtop), COL["plate"]),
           part("Jack block", win(S("jack_block", "jack_screws"), *wtop), COL["jack_block"])],
       [mv(part("Jack screw, wound up to the flange", C["jack"].shape, COL["bolt"]), (0, 0, -24))],
       "jack screw up to the top flange",
       "Wind the screw up until it bears, then a further quarter turn; tighten the lock nut, then the clamp bolts",
       elev=-10, azim=-60, label_done=False)
    fitted = [g, pl, M["feet"], clamps, part("Jack", S("jack_block", "jack", "jack_screws"), COL["jack_block"])]
    hub = part("Hub with boards, lid off", S("body", "glands", "probe_glands", "connector", "acc_spacers", "sig_standoffs", "acc", "sig"), COL["body"])
    st(8, fitted, [mv(hub, (0, -150, 0)), mv(M["hub_screws"], (0, -260, 0))],
       "hub onto the plate",
       "Base flat on the plate; four M5 x 12 screws from inside the box, sealing washer under each head",
       elev=15, azim=-60, label_done=False)
    lan_new = [mv(part("Pad eye and two M5 screws", S("pad_eye", "pad_eye_screws"), COL["lanyard"]), (0, -90, 0)),
               mv(part("Girder clamp, set screw and lock nut", S("lan_clamp", "lan_screw"), "#7F1D1D"), (0, -90, 0)),
               mv(part("Wire lanyard", C["lanyard"].shape, "#475569"), (0, -150, 60))]
    st(9, fitted + [hub], lan_new, "lanyard and its girder clamp",
       "Pad eye on the plate above the hub; clamp hooked on the flange tip 150 mm or more from the foot clamps; lanyard between them",
       elev=15, azim=-60, label_done=False)
    lanyard = part("Lanyard", S("pad_eye", "pad_eye_screws", "lanyard", "lan_clamp", "lan_screw"), "#9CA3AF")
    hubin = part("Hub", S("body", "glands", "probe_glands", "connector", "acc", "sig"), COL["body"])
    gz = [g, pl, M["feet"], clamps, fitted[-1], hubin, lanyard]
    st(10, gz, [mv(part("Active gauge under its cover", win(C["patches"].shape, -100, 100, -700, -500, 1100, 1300), COL["patches"]), (0, 0, -80)),
               mv(part("Dummy coupon", win(C["coupons"].shape, -100, 100, -700, -500, 1100, 1300), COL["coupons"]), (0, 0, 60))],
       "strain gauge and dummy coupon (south girder; the north girder is the same)",
       "Paint removed only with the owner's permission; gauge bonded under the flange; coupon on silicone",
       elev=-25, azim=-60, label_done=False)
    near = win(S("near_cable", "far_cable", "probe_leads", "cable_clips"), -200, 200, -720, -480, 1150, 1340)
    sprobe = S("steel_probe", "probe_clip")
    st(11, gz + [part("Gauges", win(S("patches", "coupons"), -100, 100, -700, -500, 1100, 1300), "#9CA3AF")],
       [mv(part("Steel probe under its flange clip", sprobe, COL["probe"]), (0, -40, 0)),
        mv(part("Gauge cables, probe leads, flange clips", near, COL["cable"]), (0, 0, -35))],
       "steel probe, cables and clips",
       "Probe under its clip on the flange; cables tied to flange clips, into their glands from below; glands tightened",
       elev=10, azim=-55, label_done=False)
    st(12, gz + [part("Cables", near + sprobe, "#9CA3AF")], [mv(part("Hub lid", C["lid"].shape, "#0F766E"), (0, -120, 0))], "close the lid",
       "Fresh desiccant pack inside; gasket clean, no wire across it; lid screws tightened evenly in a cross pattern",
       elev=15, azim=-60, label_done=False)
    post = part("Post stub, 50 mm square", win(CTX["post"], -100, 100, -900, -700, D["fn_z0"] - 200, D["fn_z0"] + 700), COL["post"])
    st(13, [post], [mv(part("FieldNode core (V-blocks left off)", C["fieldnode"].shape, COL["fieldnode"]), (0, -150, 0)),
                    mv(part("Long band clamps (2)", C["fn_bands"].shape, "#475569"), (0, 120, 0))],
       "FieldNode core onto the post",
       "Back plate flat on the post's face; each band round the post, through both slots and across the plate front",
       elev=18, azim=-50, label_done=False)
    fn_full = part("FieldNode", S("fieldnode", "fn_bands"), "#9CA3AF")
    wide = win(S("fn_cable", "air_probe", "probe_leads", "far_cable"), -300, 300, -1000, 700, 1100, 2100)
    st(14, [g, part("North girder offcut", i_girder(P, P["gy"], -320, 320), COL["girder"]), part("Post", CTX["post"], "#9CA3AF"),
            fn_full, part("Monitor at the girder", S("plate", "feet", "body", "lid", "jack_block", "pad_eye", "lanyard", "lan_clamp"), "#9CA3AF")],
       [part("M12 cable up the post to the FieldNode port", C["fn_cable"].shape, COL["cable"]),
        part("Far gauge cable between the girders", win(C["far_cable"].shape, -300, 300, -480, 700, 1100, 2100), "#C2410C"),
        part("Air probe hung from the far cable", S("air_probe") + win(C["probe_leads"].shape, -300, 300, -480, 700, 1300, 1600), COL["probe"])],
       "cable to the FieldNode, far gauge cable and air probe",
       "M12 cable clipped up the post to the FieldNode port; far cable across between the girders, air probe hung from it",
       elev=22, azim=-125, label_done=False)
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.2), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 72); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 70, "BridgePulse prototype: block-level wiring of the sensor hub", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 66.6, "Bought modules wired at block level on the signal board; no circuit board is laid out. Stranded copper; "
            "ferrules on every screw terminal.", fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, REPO, fontsize=7, color="#0F766E", ha="right", family="monospace")
    ax.add_patch(FancyBboxPatch((30, 13), 64, 47, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(31.5, 58.8, "Inside the hub (signal board and accelerometer board)", fontsize=8, color=MUT, va="top")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=9, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 4.3, sub, ha="center", va="top", fontsize=7.2, color=MUT, linespacing=1.3)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7.2, color=color, ha=ha, va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY, GRN = "#B91C1C", "#1D4ED8", "#6B7280", "#047857"
    blk(98, 42, 19, 14, "FieldNode port", "M12 5-pin via the\npanel connector:\n5 V rail, RS-485", "#115E59")
    blk(74, 44, 15, 12, "5 V to 3.3 V", "buck converter", "#16A34A")
    blk(74, 27, 15, 11, "RS-485", "transceiver\nmodule", "#2563EB")
    blk(50, 38, 16, 18, "Controller", "RP2040 class\nboard, microSD\nsocket, 32 GB\nindustrial card", "#0F766E")
    blk(50, 16, 16, 12, "Bridge ADC", "24-bit, ADS1220\nclass, 2 channels", "#2563EB")
    blk(33, 42, 14, 12, "Accelerometer", "ADXL355 class,\nSPI", "#0F766E")
    blk(33, 22, 14, 14, "Excitation", "switch and\ncompletion resistors\n2 x 10 k, 0.1 %", "#7C3AED")
    blk(3, 16, 18, 15, "Strain half-bridges", "near and far: active\ngauge + dummy on\ncoupon, 4-core cable", "#C2410C")
    blk(3, 42, 18, 12, "Temperature probes", "steel and air,\n1-Wire, 3-core lead", "#7C3AED")
    # power
    wire([(98, 52), (89, 52)], RED); lab(93.5, 54, "5 V, 0.5 mm²", RED, "center")
    wire([(74, 50), (66, 50)], RED); lab(70, 52, "3.3 V", RED, "center")
    wire([(81.5, 44), (81.5, 38)], RED); lab(82.2, 41, "3.3 V", RED)
    wire([(60, 38), (60, 28)], RED, 1.2); lab(60.6, 33, "3.3 V", RED)
    wire([(50, 48), (47, 48)], BLU, 1.2); lab(48.5, 50.2, "SPI", BLU, "center")
    wire([(54, 38), (54, 28)], BLU, 1.2); lab(53.4, 33, "SPI", BLU, "right")
    wire([(98, 45), (93, 45), (93, 32), (89, 32)], BLU); lab(93.6, 38.5, "RS-485 A/B,\n0.25 mm²", BLU)
    wire([(74, 32), (66, 32), (66, 38)], BLU, 1.2); lab(70, 30, "UART", BLU, "center")
    wire([(50, 40), (40, 40), (40, 36)], GRY, 1.2); lab(41, 38.2, "enable", GRY)
    wire([(21, 28), (33, 28)], GRN); lab(22, 30.2, "excitation, 0.25 mm²", GRN)
    wire([(21, 19), (50, 19)], GRN); lab(24, 17.4, "signals, 0.25 mm²", GRN)
    wire([(21, 48), (26, 48), (26, 62), (62, 62), (62, 56)], GRY); lab(28, 62, "1-Wire data, ground, 3.3 V; 4.7 k pull-up", GRY)
    ax.text(3, 7.0, "Red: power. Blue: data buses. Green: bridge excitation and signals (shields to ground at the hub end only). "
            "Grey: control and 1-Wire.", fontsize=7.2, color=MUT)
    ax.text(3, 4.2, "Extra-low voltage only: 5 V at the port, 3.3 V inside. Gauge leads twisted; probe leads away from the excitation pair.",
            fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    what = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring"]
    fns = {"overview": overview, "sheets": sheets, "sheet101": lambda: sheets(101), "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring}
    for w in what:
        r = fns[w]()
        print(w, "->", r)
