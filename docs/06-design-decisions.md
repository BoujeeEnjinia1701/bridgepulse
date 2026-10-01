---
doc_id: BRP-DEC-001
title: BridgePulse design decisions register
project: BridgePulse
doc_type: Design decisions register
version: "0.1"
status: Draft
date: '2026-09-30'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Register opened; open decisions gathered from the decision records, the review note and the build plan work
---

# BridgePulse design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Accept the design for construction (foot blocks and clamps, jack block, hub fixing, five penetrations, probe and coupon fixing, cable clips, FieldNode on the square post) | Accept; accept with changes | Accept | Every component of the build plan | BRP-DDR-004, A5 |
| 2 | Budget: the BridgePulse-specific parts are $252.00 against $250 (R12 not met by $2.00) | Raise `budget_usd` to $255; take the saving named in BRP-DDR-002 (consumer high-endurance microSD card rated -25 to +85 °C); wait for quotes at TRL 4 | Take the card saving, if its datasheet covers -25 to +85 °C | The microSD card in the signal board | BRP-DDR-004, A1; BRP-CAL-001 v0.3, K |
| 3 | Lanyard anchor on the bridge (second retention path in the safety case) | A second, independent beam clamp on the bottom flange; the handrail post; a cross frame where there is one | Independent beam clamp, added to BOM line 4 | Lanyard hole in the plate; one bought clamp | BRP-DDR-004, A2 |
| 4 | Tamper resistance of the FieldNode core on a public footbridge (R9) | Stainless banding with a one-way crimped buckle; worm-drive bands with tamper-resistant screws; a lockable cover | Crimped banding for installations, worm-drive bands on the bench; FieldNode to decide for all post installations | The two band clamps on the post | BRP-DDR-004, A3; BRP-REQ-001, R9 |
| 5 | Support for the far gauge cable where it crosses between the girders | Along a cross frame or diaphragm; a tensioned catenary wire between two flange clamps; decide at the site survey | Decide at the site survey, preferring a cross member near midspan | Far gauge cable route and the air probe's hanging point; not part of the bench build | BRP-DDR-004, A4 |
| 6 | FieldNode sensor port pinout and protocol | To be agreed with the FieldNode project; this repo assumes its candidate (pin 1 switched rail, pins 2 and 4 RS-485, pin 3 ground, 5 V) | None yet | Wiring of the M12 panel connector | BRP-DDR-001, O1; BRP-DDR-002, O1 |
| 7 | First host bridge and co-design partner | Open | None yet | Girder section, plate length, packer length, cable support | BRP-DDR-001, O2 |
| 8 | Data ownership and what is published beyond monitoring status | Open | None yet | Not part of the build | BRP-DDR-001, O3 |
| 9 | LoRaWAN region for the first installation | Region of the first host bridge | None in this repo; the 11-byte summary makes R7 independent of it | FieldNode radio and antenna variant | BRP-DDR-002, O4; FND-DDR-001, O1 |
| 10 | Clear window in the hub lid in the appearance model | Render aid only, build with the plain die-cast lid; gasketed window if a status light must be read on site | Render aid only | None (the build uses the plain lid) | REVIEW 2026-09-26, item 1 |
| 11 | Parts left out of the appearance model (north gauge, air probe, FieldNode and post) | Accept; add them | Accept; FieldNode has its own renders | Renders only | REVIEW 2026-09-26, item 2 |
| 12 | Cable routes in the appearance model (far cable crossing at +100 mm, FieldNode cable at -130 mm) | Adopt in the model; keep the model's routes | Superseded by BRP-DDR-004: the appearance model should follow the routes in `cad/src/model.py` when it is next updated | Renders only | REVIEW 2026-09-26, item 3; BRP-DDR-004, P10 and P11 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The host girder's clear web height, flange thickness and root fillet radius | They set the plate length (clear height less 44 mm), the packer length (flange thickness less 0.5 mm) and whether the 22 mm fillet gap and 12 mm chamfer are enough (fillet up to about 20 mm) | BRP-DDR-004, P1 and P2 |
| 2 | The enclosure's base wall thickness and flatness at the four screw points and eight spacer points | The M5 sealing washers and the countersunk M3 screws need a flat, sound wall of about 4 mm | BRP-DDR-004, P4 and P5 |
| 3 | Gland clamping ranges against the real cables: M16 for the gauge cables, M12 for the probe leads | Each gland seals only within its range | BRP-DDR-004, P6 |
| 4 | Flange clip grip ranges: 12.7 mm flange for the cable clips, about 20 mm (flange plus sheath) for the probe clip | A clip outside its range will not hold | BRP-DDR-004, P7 and P11 |
| 5 | The FieldNode band clamp length (about 300 to 330 mm round the 50 mm square post) and that the FieldNode project accepts mounting without V-blocks | The bands must close with adjustment to spare; the interface is FieldNode's | BRP-DDR-004, P12; BRP-CAL-001, H8 |
| 6 | The FieldNode core's current cost and mass ($126.00 and 2.41 kg are copied from FND-CAL-001) | FieldNode's own build plan may have changed them; they feed the complete-monitor cost and the post load | BRP-CAL-001, H1 and K |
| 7 | The RP2040 class board's rated temperature range (assumed -20 to +85 °C) and the ADC noise figure (assumed) | They underpin R10 and R4 | BRP-CAL-001, D and J |

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D11: budget covers the BridgePulse-specific parts, ambient excitation, hourly 10 minute records, hub on the girder and FieldNode on a post, foil half-bridges with dummies, one accelerometer, RP2040 class controller, engineer-only alerts, temperature-compensated trend, shared lab components, pitch unchanged | Amish: "i accept all your recommendations, go with them across all repos." | BRP-DDR-001, BRP-DDR-002 |
| 2026-09-25 | D12 to D15: load gating with a load regression in TwinKit; 11-byte reduced summary; TMP1826 class probes with an ice-point check; no cost change now, with named savings if quotes come in higher | Amish, same instruction | BRP-DDR-002 |
| 2026-09-27 | Far gauge cable's vertical runs moved inboard of the bottom flanges in the model | Amish: "resolve the challenges for ConePro, BridgePulse, Grainguard and WellSense." | BRP-DDR-003 |
