"""BridgePulse general arrangement sheet BRP-DWG-001, Rev P2 (TRL 3).

Run from the repo root:  python cad/src/sheets.py
Writes cad/drawings/BRP-DWG-001.svg, .pdf and .png from the parametric model in cad/src/model.py
with .kit/drawing.py. Dimensions come from PARAMS and derived(), so they follow any parameter
change. The concept blueprint in media/ is BRP-DWG-010. The timber deck and the handrails are left
off the views for clarity; the midspan post that carries the FieldNode core is shown.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from drawing import Sheet, _viewbox, _t, M, TB_Y, INK, MUTED  # noqa: E402
from model import PARAMS as P, derived, installed, hub_group, i_girder  # noqa: E402

DATE = "2026-09-25"


def safe_project_views(part, workdir, line_weight=0.35):
    """Same views as drawing.project_views, but edge by edge, so that a degenerate edge from the
    hidden-line projection is skipped instead of stopping the export."""
    from build123d import ExportSVG, LineType, Unit
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    bb = part.bounding_box()
    c = bb.center(); d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    setups = {"front": ((c.X, c.Y - d, c.Z), (0, 0, 1)), "top": ((c.X, c.Y, c.Z + d), (0, 1, 0)),
              "right": ((c.X + d, c.Y, c.Z), (0, 0, 1)), "iso": ((c.X + d, c.Y - d, c.Z + d * 0.8), (0, 0, 1))}
    out, skipped = {}, 0
    for name, (origin, up) in setups.items():
        visible, hidden = part.project_to_viewport(origin, up, (c.X, c.Y, c.Z))
        ex = ExportSVG(unit=Unit.MM, line_weight=line_weight)
        ex.add_layer("Visible", line_color=0x111827)
        ex.add_layer("Hidden", line_color=0x6B7280, line_type=LineType.ISO_DASH, line_weight=line_weight / 2)
        for layer, edges in (("Visible", visible), ("Hidden", hidden if name != "iso" else [])):
            for e in edges:
                try:
                    ex.add_shape(e, layer=layer)
                except (AssertionError, ValueError, ZeroDivisionError):
                    skipped += 1
        p = workdir / f"{name}.svg"
        ex.write(str(p))
        out[name] = p
    print(f"projected views; skipped {skipped} degenerate edges")
    return out


def ortho_cells(sheet, views, names=("front", "top", "right")):
    """Repeat Sheet.add_ortho's layout arithmetic to find where each view lands (x, y, w, h)."""
    ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
    gap, lab = 14, 12
    dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
    fw, fh = dims["front"]; tw, th = dims["top"]; rw, rh = dims["right"]
    k = sheet.scale
    ax += (aw - (k * (max(fw, tw) + rw) + gap)) / 2
    ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab)) / 2
    colw = k * max(fw, tw)
    front_y = ay + k * th + lab + gap
    row_h = k * max(fh, rh)
    return {"top": (ax, ay, colw, k * th), "front": (ax, front_y, colw, row_h),
            "right": (ax + colw + gap, front_y, k * rw, row_h)}


def dim_h(x1, x2, y, text):
    a = 1.4
    return [f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x1:.2f} {y:.2f} l{a} -0.5 l0 1 Z" fill="{INK}"/>',
            f'<path d="M{x2:.2f} {y:.2f} l{-a} -0.5 l0 1 Z" fill="{INK}"/>',
            _t((x1 + x2) / 2, y - 1.0, text, 2.3, 400, INK, "middle", mono=True)]


def dim_v(x, y1, y2, text, side=-1):
    a = 1.4
    cx, cy = x + side * 1.0, (y1 + y2) / 2
    return [f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x:.2f} {y1:.2f} l-0.5 {a} l1 0 Z" fill="{INK}"/>',
            f'<path d="M{x:.2f} {y2:.2f} l-0.5 {-a} l1 0 Z" fill="{INK}"/>',
            f'<g transform="rotate(-90 {cx:.2f} {cy:.2f})">{_t(cx, cy, text, 2.3, 400, INK, "middle", mono=True)}</g>']


def ext(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.13"/>'


def leader(x1, y1, x2, y2, text, anchor="start"):
    return [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.15"/>',
            f'<circle cx="{x1:.2f}" cy="{y1:.2f}" r="0.5" fill="{INK}"/>',
            _t(x2 + (1 if anchor == "start" else -1), y2 + 0.8, text, 2.1, 400, INK, anchor)]


def main():
    from build123d import Compound
    D = derived(P)
    work = ROOT / "cad" / "drawings" / "_views"
    asm = installed(P, deck=False)
    views = safe_project_views(asm, work)
    bb = asm.bounding_box()
    det = Compound(children=[hub_group(P), i_girder(P, -P["gy"], -150, 150)])
    dviews = safe_project_views(det, work / "detail")
    dbb = det.bounding_box()
    s = Sheet(project="BridgePulse", title="General arrangement at midspan", dwg_no="BRP-DWG-001", rev="P2",
              author="Amish Chadha", date=DATE, scale=0.05, theme="technical",
              material="6061 Al plate; bought-in parts per bom/bom.csv. PRELIMINARY, NOT FOR FABRICATION",
              revisions=[("P1", "Preliminary GA for TRL 3 (from cad/src/model.py)", DATE, "AC"),
                         ("P2", "Probe note per BRP-DDR-002", DATE, "AC")])
    k = s.scale
    # front and right views only (a top view shows little but the two girders); placed by hand so
    # that detail A fits beside them
    fw, fh = [v * k for v in _viewbox(Path(views["front"]).read_text())[2:]]
    rw, rh = [v * k for v in _viewbox(Path(views["right"]).read_text())[2:]]
    fy = 90.0
    c = {"front": (32.0, fy, fw, fh), "right": (32.0 + fw + 22.0, fy, rw, rh)}
    for n in ("front", "right"):
        x, y, w, h = c[n]
        s.add_svg(views[n], x, y, w, h, scale=k, label=f"{n} view", sublabel="Scale 1:20")
    L = [_t(M + 6, M + 14, "PRELIMINARY, NOT FOR FABRICATION", 3.2, 600, "#B45309")]
    z0 = P["g_z0"]

    # right view (from +X): +Y to the right, Z up
    x, y, w, h = c["right"]
    Yr = lambda my: x + (my - bb.min.Y) * k
    Zr = lambda mz: y + h - (mz - bb.min.Z) * k
    L.append(f'<line x1="{Yr(bb.min.Y) - 4:.2f}" y1="{Zr(z0):.2f}" x2="{Yr(bb.max.Y) + 4:.2f}" y2="{Zr(z0):.2f}" stroke="{MUTED}" stroke-width="0.13" stroke-dasharray="3 1 0.6 1"/>')
    L.append(_t(Yr(bb.max.Y) + 4, Zr(z0) + 3.2, "SOFFIT", 1.9, 600, MUTED, "end"))
    L.append(f'<line x1="{Yr(-P["deck"][1] / 2):.2f}" y1="{Zr(D["deck_top"]):.2f}" x2="{Yr(P["deck"][1] / 2):.2f}" y2="{Zr(D["deck_top"]):.2f}" stroke="{MUTED}" stroke-width="0.25" stroke-dasharray="1.5 1"/>')
    L.append(_t(Yr(P["deck"][1] / 2), Zr(D["deck_top"]) - 1.2, "DECK (NOT SHOWN)", 1.9, 600, MUTED, "end"))
    yd = Zr(D["deck_top"] + 120)
    L += [ext(Yr(-P["gy"]), Zr(D["deck_z0"]) - 1, Yr(-P["gy"]), yd - 1), ext(Yr(P["gy"]), Zr(D["deck_z0"]) - 1, Yr(P["gy"]), yd - 1)]
    L += dim_h(Yr(-P["gy"]), Yr(P["gy"]), yd, f"{2 * P['gy']:.0f} girder centers")
    xd = Yr(bb.min.Y) - 5
    L += [ext(Yr(D["post_y"]) - 2, Zr(D["fn_z0"]), xd - 1, Zr(D["fn_z0"])), ext(Yr(D["post_y"]), Zr(D["deck_top"]), xd - 1, Zr(D["deck_top"]))]
    L += dim_v(xd, Zr(D["fn_z0"]), Zr(D["deck_top"]), f"{P['fn_base_above_deck']:.0f}")
    L += [ext(Yr(D["post_y"]), Zr(D["post_top"]), xd - 7, Zr(D["post_top"]))]
    L += dim_v(xd - 6, Zr(D["post_top"]), Zr(D["deck_top"]), f"{P['post'][2]:,.0f} post")
    L += leader(Yr(D["fn_front"]), Zr(D["fn_z0"] + 100), Yr(D["fn_front"]) + 14, Zr(D["fn_z0"] + 700), "FIELDNODE CORE, ITEM 8")
    L += leader(Yr(P["gy"]), Zr(z0 + 250), Yr(P["gy"]) - 6, Zr(z0 + 900), "EXISTING GIRDER (NOT IN BOM)", "end")
    L += leader(Yr(-P["gy"] - 40), Zr(z0 + 190), Yr(bb.min.Y) - 3, Zr(z0 - 150), "HUB, SEE DETAIL A", "end")

    # front view (from -Y): X to the right
    x, y, w, h = c["front"]
    X = lambda mx: x + (mx - bb.min.X) * k
    Zf = lambda mz: y + h - (mz - bb.min.Z) * k
    L.append(_t(X(0), Zf(bb.max.Z) - 2, "MIDSPAN", 1.9, 600, MUTED, "middle"))
    L.append(_t(M + 22, fy - 12, "DECK AND HANDRAILS OMITTED FOR CLARITY; HUB AND FIELDNODE ON THE -Y (SOUTH) SIDE", 2.0, 600, MUTED))

    # detail A: right view of the hub on the south girder, 1:5
    ks = 0.25
    dvx, dvy, dvw, dvh = _viewbox(Path(dviews["right"]).read_text())
    ax0, ay0 = 32.0 + fw + 22.0 + rw + 28.0, 62.0
    s.add_svg(dviews["right"], ax0, ay0, scale=ks, label="Detail A: hub on south girder", sublabel="Right view, scale 1:4")
    bw, bh = dvw * ks, dvh * ks
    Yd = lambda my: ax0 + (my - dbb.min.Y) * ks
    Zd = lambda mz: ay0 + bh - (mz - dbb.min.Z) * ks
    xl = Yd(dbb.min.Y) - 5
    L += [ext(Yd(D["web_face"] - P["plate_t"]), Zd(D["plate_z1"]), xl - 1, Zd(D["plate_z1"])),
          ext(Yd(D["web_face"] - P["plate_t"]), Zd(D["plate_z0"]), xl - 1, Zd(D["plate_z0"]))]
    L += dim_v(xl, Zd(D["plate_z1"]), Zd(D["plate_z0"]), f"{D['plate_h']:.0f} plate")
    L += [ext(Yd(D["hub_y1"]), Zd(D["hub_zc"]), xl - 9, Zd(D["hub_zc"])), ext(Yd(D["tip"]), Zd(z0), xl - 9, Zd(z0))]
    L += dim_v(xl - 8, Zd(D["hub_zc"]), Zd(z0), f"{P['hub_zc']:.0f} hub center")
    yt = Zd(dbb.max.Z) - 6
    L += [ext(Yd(D["hub_y1"]), Zd(D["hub_zc"] + P["hub"][2] / 2), Yd(D["hub_y1"]), yt - 1),
          ext(Yd(D["web_face"]), Zd(D["deck_z0"] - P["girder"][2]), Yd(D["web_face"]), yt - 1)]
    L += dim_h(Yd(D["hub_y1"]), Yd(D["web_face"]), yt, f"{D['web_face'] - D['hub_y1']:.0f}")
    L += leader(Yd(D["tip"]), Zd(z0 - 4), Yd(dbb.max.Y) + 6, Zd(z0 + 40), f"CLAMP JAW, {z0 - dbb.min.Z:.0f} BELOW SOFFIT")
    L += leader(Yd(D["hub_y1"]) + 2, Zd(D["hub_zc"]), Yd(dbb.max.Y) + 6, Zd(D["hub_zc"] + 60), "HUB, ITEMS 1 TO 3")
    L += leader(Yd(D["web_face"] - P["plate_t"] / 2), Zd(D["plate_z0"] + 60), Yd(dbb.max.Y) + 6, Zd(D["plate_z0"] + 110), "PLATE, ITEM 4")
    L += leader(Yd(0 - P["gy"]), Zd(D["plate_z1"] + 10), Yd(-P["gy"]) + 10, Zd(D["plate_z1"] + 50), f"M{P['jack_d']:.0f} JACK SCREW")

    s._layers += L
    s.add_svg(views["iso"], 304, 40, 112, 110, label="Isometric view", sublabel="Not to scale; deck omitted")
    s.add_notes("Main dimensions and interfaces (mm)", [
        f"Hub {P['hub'][0]:.0f} x {P['hub'][1]:.0f} x {P['hub'][2]:.0f} IP67, {D['hub_inside_tip']:.0f} inside the flange tip line",
        f"Plate {P['plate_w']:.0f} x {D['plate_h']:.0f} x {P['plate_t']:.0f} Al on the bottom flange, jack to the top flange",
        f"Two flange-tip clamps at x = +/-{P['clamp_x']:.0f}; nothing drilled or welded",
        f"Gauge covers under each flange at midspan; 10 max below soffit (R9: 15)",
        f"FieldNode on the post, base {P['fn_base_above_deck']:.0f} above deck; M12 5-pin, RS-485, 5 V",
        "Probes (item 6) TMP1826 class in 7 dia sheaths; steel on web, air in shade",
        f"Example girders IPE 360 class at {2 * P['gy']:.0f} centers, span {P['bearing_span']:,.0f}",
        f"Third-angle; front view from -Y; {P['seg']:.0f} segment at midspan (x = 0)",
    ], x=276, y=166, width=146)
    out = s.save(ROOT / "cad" / "drawings" / "BRP-DWG-001")
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {out} and .pdf, .png at scale 1:{1 / k:g}; detail A box {bw:.0f} x {bh:.0f} mm")


if __name__ == "__main__":
    main()
