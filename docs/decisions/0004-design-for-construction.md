---
doc_id: BRP-DDR-004
title: BridgePulse design for construction
project: BridgePulse
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review
- version: "0.2"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target; R12 wording only, no number changed
---

# 0004: Design for construction

- **Date:** 2026-09-30
- **Status:** Draft. Every change in Table 1 was made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review. The items in Table 3 are "Proposed, awaiting Amish" and are carried in the design decisions register (BRP-DEC-001).

## Context

On 2026-09-30 Amish asked for every repo to get an illustrated prototype build plan, and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The TRL 3 model of BRP-CAL-001 v0.2 showed what BridgePulse does and how stiff its mount must be, but several parts could not be made, fixed or fitted as drawn. The biggest was that a rolled IPE 360 girder has 18 mm root fillets where its web meets its flanges, and the concept plate stood exactly in that corner.

The changes below keep what the monitor does: the same hub, boards, sensors, positions at midspan, hub height, jack-screw principle, "no drilling" rule and FieldNode link. The hub's front face is still 9 mm inside the flange tip line and nothing hangs more than 10 mm below the soffit (R9, 15 mm). Nothing here changes the pitch or the safety case. Every change is in `cad/src/model.py`, which now builds each component separately and runs 75 constructability checks (`python cad/src/model.py --check`): parts that must touch do touch, with no overlap, and parts that must stay apart keep the stated clearance. All 75 pass. The girders in the model now carry their root fillets.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | The 8 mm plate stood on the bottom flange with its back on the web. The IPE 360 root fillet (18 mm radius) rises 3 mm at the plate's front face and 18 mm at the web, so the plate would have rested on the fillet edge, not on the flange or flat on the web. The same corner existed under the top flange. | The plate is 22 mm short of each flange: 200 × 290.6 × 8 mm (the clear web height less 44 mm), lying flat on the web between the fillets. It stands on two foot blocks instead of on its own edge. | Keeps the plate on the web and the hub where the concept put it (same height, 9 mm inside the flange tip). 22 mm clears an 18 mm fillet with margin and suits other rolled sections up to about 20 mm. |
| P2 | The two "flange-tip clamps" were a block beside the plate foot with no fixing to the plate, a spacer and a jaw joined by a bolt just outside the flange tip, with nothing outside the tip for the jaw to bear on, so the jaw would tilt about the tip. The bolt's head and nut were not shown and would have hung below the soffit. | Each foot block is one stepped piece sawn from 100 × 40 mm aluminium bar: a tall end screwed to the plate's front face by two M6 cap screws (counterbored), a 12 mm tail on the flange top running 23 mm past the tip, and a 12 mm chamfer over the root fillet. Under the flange, a 40 × 45 × 10 mm steel jaw, tapped M10, reaches 22 mm in from the tip; a steel packer, 0.5 mm shorter than the flange is thick, stands on the jaw outside the tip; an M10 × 35 bolt comes down through the tail and the packer into the jaw and ends 1.2 mm inside it. | A classic flange clamp: tightening pulls the jaw up under the flange and the tail down on top, with both ends of the jaw bearing. Nothing but the 10 mm jaw is below the soffit (was 8 mm), still within R9. The foot blocks carry the jack's reaction into the flange through the M6 screws. |
| P3 | The jack "tab" (40 × 30 × 10 mm) had no fixing to the plate and only 10 mm of thread, and the M12 jack screw sat wholly inside the 22 mm gap under the top flange, with no room for a head, a spanner or a lock. | A jack block, 40 × 30 × 30 mm aluminium, screwed to the top of the plate's front face by two M6 cap screws, tapped M12 the full 30 mm. An M12 × 70 stainless screw goes up through it, head and lock nut below the block, its end bearing on the top flange 26 mm out from the web. | 30 mm of thread in aluminium, a spanner from below, a lock nut to hold the preload, and a bearing point clear of the top root fillet. |
| P4 | The hub enclosure had no fixing to the plate. | Four M5 screws from inside the box, through the base into tapped holes in the plate, each with a bonded sealing washer under its head; their tips stop 2 mm short of the web. The base lies flat on the plate. | The base is clamped to the plate at four points, which couples the accelerometer to the plate as the stiffness calculation assumes, and the box stays sealed. |
| P5 | The signal board stood on two standoffs along its bottom edge only, 6 mm above the gland nuts; the accelerometer board was "bonded and screwed" to the base with nothing between. | Accelerometer board on four 5 mm metal spacers and signal board (92 × 68 mm) on four 14 mm standoffs, all on M3 countersunk screws from outside the base, sealed with thread sealant and covered by the plate once the hub is on. | Four-point fixings for both boards; every board edge 10 mm or more from the M5 screws, so a screwdriver reaches them with the boards fitted, and 12 mm or more above the gland nuts. |
| P6 | The two temperature probe leads had no way into the hub: the concept had two glands, both used by gauge cables. | Five penetrations in one row on the bottom face: M12 gland (steel probe), M16 gland (near gauge), M12 5-pin panel connector, M16 gland (far gauge), M12 gland (air probe), at 60, 30 and 0 mm each side of centre. | Every penetration sealed with a standard part; 9 mm or more between neighbours outside and inside. |
| P7 | The steel probe was a 14 × 15 mm boss stuck to the web with no fixing (the open REVIEW item of 2026-09-26). | The probe is the 7 × 60 mm sheath of BOM line 6, lying on the bottom flange top 6.5 mm in from the tip, held down by a push-on spring-steel flange clip with thermal paste under it. | No drilling and no adhesive on the structure; the flange is the steel the gauges measure, and the clip comes off for the ice-point check. |
| P8 | The air probe hung on a lead that ended in mid-air 13 mm below the top flange. | It hangs on its own lead from the far gauge cable where that cable crosses between the girders, 110 mm below it, and its lead runs beside the far cable to the hub. | Uses a support that is already there and keeps the probe in shade, away from the steel (240 mm). |
| P9 | The dummy coupons sat on the flange top 12.5 mm from the web, over the root fillet, with no fixing; bonded rigidly they would be strained with the girder and stop being dummies. | Each coupon (40 × 25 × 6 mm steel) is centred 35 mm out from the web, clear of the fillet, and set on a bed of neutral-cure silicone. | It shares the flange's temperature but not its strain, which is what a dummy gauge needs. |
| P10 | The gauge cover patches (90 × 45 mm) overlapped the near gauge cable where it starts and the far gauge cable where it runs under the south flange. | Cover patch 60 × 40 mm, which still covers a foil gauge and its solder tabs; the cables run 6 mm or more clear of the covers. | Nothing passes through anything else. |
| P11 | Cables were held by "UV-stable clips" with nothing to clip to, since nothing may be drilled. The cable to the FieldNode ran up inside the handrail post's outline and ended under the antenna rather than a sensor port. | Five push-on spring-steel flange clips (one for the steel probe, four for cables) with cable ties. The M12 cable rises beside the post, 6 mm clear of it, and plugs into the FieldNode's port B. | Standard clips that grip a flange edge without drilling; the cable reaches a real port. |
| P12 | The FieldNode's V-blocks are made for round poles and would bear on the corners of the 50 mm square handrail post (BRP-CAL-001, H8, which asked FieldNode to review it). In this repo's model the FieldNode panel also faced the post, and the bracket arms started in mid-air beside the back plate. | On the square post the V-blocks are left off: the back plate bears flat on the post's face, and two band clamps one size longer (band about 300 to 330 mm) go round the post, through the plate's slots and across its front. The panel now faces away from the post, as FieldNode's own model has it, and the bracket envelope starts on the back plate. | The same approach FieldNode adopted for wall mounting (FND-DDR-003, A2): no new part, and the flat face is a better seat than a V on a square post. The FieldNode core itself is unchanged and is built to its own plan, FND-BLD-001. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | 3.21 kg on the girder (was 3.34 kg): hub 0.99 kg, plate 1.25 kg, foot blocks, jaws, packers, jack and fixings 0.97 kg (BRP-CAL-001 v0.3, H1). | Shorter plate; the clamp parts are now counted in their own materials; two more glands. |
| Mount stiffness | Out-of-plane mode 135 to 271 Hz (was 126 to 253 Hz), still above the 120 Hz target (H2). | The plate between its supports is shorter. |
| Cost | Line 1 $22.00 (+$2.00, two probe glands), line 4 $40.00 (+$2.00, foot blocks, jaws, packers, jack block and screws). BridgePulse-specific parts $252.00 against the $250 value-engineering target (`budget_usd`): **over the target by $2.00** (K1). The target is unchanged; see Table 3, A1. | Parts added for construction. |
| Depth below the soffit | 10 mm worst (jaws and cables), against 15 mm; R9 stays met on paper (H5). | Jaw is 10 mm thick so the M10 thread engages fully. |
| Drawings | BRP-DWG-001 Rev P5; making sketches BRP-DWG-101 to 107 added. | Follows the model. |
| Documents | BRP-CAL-001 v0.3, BRP-REQ-001 v0.5, BRP-PRC-001 v0.5, `bom/bom.csv`, `bom/bom-notes.md`. Requirement count: 1 over the value-engineering target (R12), 2 at risk (R2, R10), 3 not verifiable at TRL 3, 4 met on paper, 3 met by design. | Follows the model. |
| Appearance model | `cad/src/product_model.py` and the photoreal renders still show the concept plate, tab, clamps, probe boss and glands; they need updating on Amish's Mac, where Blender is. | Renders are made there. |

*Table 3. Proposed, awaiting Amish.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | R12: the estimated cost is $2.00 over the $250 value-engineering target on indicative prices. | Savings worth trying: (a) take the first saving already named in BRP-DDR-002, a consumer high-endurance microSD card rated -25 to +85 °C, in place of the industrial card; (b) a cheaper accelerometer breakout that still meets R1; (c) leave it until quotes at TRL 4. | (a), if the chosen card's datasheet covers -25 to +85 °C, since it keeps R10 and saves about $10. |
| A2 | The lanyard (the safety case's second retention path) has a hole in the plate but no anchor on the bridge: nothing may be drilled, the deck sits on the top flange and a loop cannot pass round a flange. | (a) a second, independent bought beam clamp on the bottom flange at least 150 mm along the span, with the lanyard to it; (b) to the handrail post; (c) to a cross frame or diaphragm where the bridge has one. | (a): independent of the foot clamps and the same on every bridge; it would add a bought clamp to BOM line 4. |
| A3 | R9 asks for tamper-resistant fasteners on the post-mounted FieldNode; worm-drive band clamps undo with a screwdriver. | (a) stainless banding with a one-way crimped buckle for installations, worm-drive bands on the bench; (b) worm-drive bands with tamper-resistant screws; (c) a lockable cover. | (a). FieldNode should decide it for all its post installations. |
| A4 | Where the far gauge cable crosses between the girders it needs support; the example bridge has no cross member in the model, and fixings into the deck count as drilling. | (a) run it along the nearest cross frame or diaphragm; (b) a tensioned 3 mm stainless catenary wire between two flange clamps; (c) decide at the site survey with the owner. | (c), preferring (a) wherever the bridge has a cross member near midspan. Depends on the first host bridge (BRP-DDR-001, O2). |
| A5 | Accept the changes of Table 1. | (a) accept; (b) accept with changes. | (a). |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan BRP-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`); the open items above are in the design decisions register BRP-DEC-001, not in the plan.
- R12 moves from at risk to over the value-engineering target ($2.00 over); every other requirement keeps its status.
- The photoreal renders (`media/render-*.png`), `media/card.png`, `media/social-preview.png` and the appearance model `cad/src/product_model.py` still show the concept mount and need updating on Amish's Mac.
- The FieldNode project is asked to confirm the square-post interface (no V-blocks, longer bands) and its own current mass and cost; nothing in the FieldNode repo is changed here.
- TRL stays at 3; TRL 4 remains on hold. Nothing in this record authorizes building, testing or buying.
