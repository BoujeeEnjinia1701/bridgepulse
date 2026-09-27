---
doc_id: BRP-DDR-003
title: BridgePulse far gauge cable route between the girders
project: BridgePulse
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-27'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-27'
  author: Amish Chadha
  change: Record Amish's decision to move the far gauge cable's vertical runs inboard of the bottom flanges in cad/src/model.py (REVIEW.md, session 2026-09-26, item 4)
---

# 0003: Far gauge cable route between the girders

- **Date:** 2026-09-27
- **Status:** accepted. Decided by Amish on 2026-09-27.

## Context

While routing cables for the product appearance model (`docs/REVIEW.md`, session 2026-09-26, item 4), the review found a modelling error in `cad/src/model.py`. The far gauge cable, which runs from the north girder's gauge across to the hub on the south girder, rose and fell between the girders at |y| = 522 mm. The inner edges of the bottom flanges are at |y| = 515 mm (girder centerline 600 mm less half the 170 mm flange), so the modelled 8 mm diameter cable ran 11 mm into each bottom flange. The error was in the sign of two terms in `inner_n`, not in the design intent, which is a cable clipped under each flange and rising clear of it.

## Options considered

1. Change `inner_n` in `cad/src/model.py` from `gy - bf / 2 + r + 3` to `gy - bf / 2 - r - 3`, placing the vertical runs one cable radius plus 3 mm inboard of the inner flange edges (recommended in the review).
2. Leave `model.py` as it is and correct only the appearance model (the state after 2026-09-26).

## Decision

Option 1. Decided by Amish on 2026-09-27. Amish's instruction: "resolve the challenges for ConePro, BridgePulse, Grainguard and WellSense."

The formula now lives in one function, `far_cable_inner()` in `cad/src/model.py`, which `build_parts()` uses for `inner_n` and `cad/src/product_model.py` imports for its own far gauge cable, so the two models cannot drift apart again.

## Consequences

- The far gauge cable's vertical runs are at |y| = 508 mm. Its surface is 3 mm inboard of each inner flange edge; the solid overlap between the cables and the girders in the model is zero (was 1,277 mm³ for the far cable alone), and the closest approach anywhere is the intended 2 mm under the flange where the cable is clipped.
- Every other dimension and interface is unchanged. No change to the BOM, the budget, the requirements or the calculations: the calc note does not use the cable route, and the clearance below the soffit (R9) is set by the cable runs under the flanges, which did not move.
- Regenerated from `model.py`: `cad/step/*.step`, `cad/stl/*.stl`, the concept media in `media/`, and drawing BRP-DWG-001, now Rev P3.
- The appearance model already used |y| = 508 mm, so the photoreal renders (`media/render-*.png`) do not change.
- Other open items from the 2026-09-26 review (lid window, parts left out, cable routes shortened and moved, probe sheath size) remain "Proposed, awaiting Amish".
- TRL stays at 3; TRL 4 remains on hold.
