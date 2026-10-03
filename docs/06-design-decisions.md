---
doc_id: BRP-DEC-001
title: BridgePulse design decisions register
project: BridgePulse
doc_type: Design decisions register
version: "0.4"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Register opened; open decisions gathered from the decision records, the review note and the build plan work
- version: "0.2"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target
- version: "0.3"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Amish approved the recommendations for all open decisions 1 to 11 on 2026-10-02 (BRP-DDR-004 accepted, P12 subject to FieldNode); moved to decisions made"
- version: "0.4"
  date: '2026-10-02'
  author: Amish Chadha
  change: "Approved follow-ups carried out: lanyard clamp and installation banding priced; value engineering restated (USD 275.00, USD 25.00 over the target); girder clamp rating added to the items to confirm"
---

# BridgePulse design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

None. All open decisions were decided on 2026-10-02.

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The host girder's clear web height, flange thickness and root fillet radius | They set the plate length (clear height less 44 mm), the packer length (flange thickness less 0.5 mm) and whether the 22 mm fillet gap and 12 mm chamfer are enough (fillet up to about 20 mm) | BRP-DDR-004, P1 and P2 |
| 2 | The enclosure's base wall thickness and flatness at the four screw points and eight spacer points | The M5 sealing washers and the countersunk M3 screws need a flat, sound wall of about 4 mm | BRP-DDR-004, P4 and P5 |
| 3 | Gland clamping ranges against the real cables: M16 for the gauge cables, M12 for the probe leads | Each gland seals only within its range | BRP-DDR-004, P6 |
| 4 | Flange clip grip ranges: 12.7 mm flange for the cable clips, about 20 mm (flange plus sheath) for the probe clip | A clip outside its range will not hold | BRP-DDR-004, P7 and P11 |
| 5 | The FieldNode band clamp length (about 300 to 330 mm round the 50 mm square post) and that the FieldNode project accepts mounting without V-blocks | The bands must close with adjustment to spare; the interface is FieldNode's, and P12 was accepted on 2026-10-02 subject to this confirmation | BRP-DDR-004, P12; BRP-CAL-001, H8 |
| 6 | The FieldNode core's current cost and mass ($126.00 and 2.41 kg are copied from FND-CAL-001) | FieldNode's own build plan may have changed them; they feed the complete-monitor cost and the post load | BRP-CAL-001, H1 and K |
| 7 | The RP2040 class board's rated temperature range (assumed -20 to +85 °C) and the ADC noise figure (assumed) | They underpin R10 and R4 | BRP-CAL-001, D and J |
| 8 | The girder clamp's working load limit (100 kg or more), the lanyard's breaking load (about 4.8 kN assumed for 3 mm 7 x 7 stainless) and the flange thickness range of the clamp | They set the margin on the 1.20 kN peak if the mount lets go; the lanyard must be fitted with 25 mm of slack or less | BRP-CAL-001, H4a and H4c |

## Value engineering

Value-engineering target: USD 250.00. Estimated cost of the constructable design: USD 275.00 (USD 25.00 over the target). The target is a hypothetical control target, not a limit, and covers the BridgePulse-specific parts (BRP-DDR-001, D1); the complete monitor with the FieldNode core is USD 401.00.

Main cost drivers (BRP-CAL-001, K): the mounting plate, foot blocks, jaws, packers, jack block and lanyard anchor (line 4, $59.00), the industrial microSD card ($20.00), the strain gauge half-bridges, and the TMP1826 class probes ($6.00 each). The parts added for construction (BRP-DDR-004) account for $4.00 of the estimate, the lanyard anchor decided on 2026-10-02 (girder clamp, pad eye and made-up wire lanyard) $19.00 and the stainless banding for installed units (line 10) $4.00.

Savings worth trying:

- A consumer high-endurance microSD card rated -25 to +85 °C in place of the industrial card, saving about $10, if its datasheet covers the range (BRP-DDR-004, A1). On its own it no longer closes the gap.
- A cheaper accelerometer breakout that still meets R1 (BRP-DDR-002).
- Quotes at TRL 4, which may move the indicative prices either way.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D11: budget covers the BridgePulse-specific parts, ambient excitation, hourly 10 minute records, hub on the girder and FieldNode on a post, foil half-bridges with dummies, one accelerometer, RP2040 class controller, engineer-only alerts, temperature-compensated trend, shared lab components, pitch unchanged | Amish: "i accept all your recommendations, go with them across all repos." | BRP-DDR-001, BRP-DDR-002 |
| 2026-09-25 | D12 to D15: load gating with a load regression in TwinKit; 11-byte reduced summary; TMP1826 class probes with an ice-point check; no cost change now, with named savings if quotes come in higher | Amish, same instruction | BRP-DDR-002 |
| 2026-09-27 | Far gauge cable's vertical runs moved inboard of the bottom flanges in the model | Amish: "resolve the challenges for ConePro, BridgePulse, Grainguard and WellSense." | BRP-DDR-003 |
| 2026-10-02 | Design for construction accepted: the changes P1 to P12 of BRP-DDR-004 and their knock-on changes, as made, with P12 (FieldNode on the square post without V-blocks) subject to the FieldNode project confirming that mount | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-004, A5 and Tables 1 and 2 |
| 2026-10-02 | Lanyard anchor: a second, independent bought girder clamp with a stated load rating on the bottom flange, at least 150 mm along the span from the foot clamps, with a stainless wire lanyard; it is to be added to BOM line 4 | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-004, A2 |
| 2026-10-02 | Tamper resistance (R9): stainless banding with a one-way crimped buckle on installed units, worm-drive bands on the bench; FieldNode is asked to adopt the same rule for all its post installations | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-004, A3; BRP-REQ-001, R9 |
| 2026-10-02 | Far gauge cable support between the girders: decided at the site survey; along a cross frame or diaphragm near midspan where there is one, otherwise a tensioned 3 mm stainless catenary wire between two flange clamps | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-004, A4 |
| 2026-10-02 | FieldNode sensor port: the FieldNode candidate adopted as the shared standard (pin 1 switched 5 V rail, pins 2 and 4 RS-485 A and B, pin 3 ground, pin 5 analog) with Modbus RTU as the protocol; FieldNode is asked to record it as decided for every adopting project | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-001, O1; BRP-DDR-002, O1 |
| 2026-10-02 | First host bridge and co-design partner: kept open under the portfolio rule and chosen, when the area is picked, as a 5 to 15 m steel footbridge on rolled I-girders whose owner (a city, park service or university) will share inspection records. First candidate to approach: a university campus footbridge with a civil engineering department | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-001, O2 |
| 2026-10-02 | Data ownership: the bridge owner owns all raw and processed data; the project publishes only monitoring status, and releases datasets for research only with the owner's written consent, under an open licence such as CC BY 4.0 | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-001, O3 |
| 2026-10-02 | LoRaWAN region: the region of the first host bridge; until then the bench unit is built for US915 if it is built and tested in North America | Amish: "i approve your recommendations for all 555 open decisions." | BRP-DDR-002, O4 |
| 2026-10-02 | Clear window in the hub lid: a render aid only; the build uses the plain die-cast lid | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 1 |
| 2026-10-02 | Parts left out of the appearance model (north gauge, air probe, FieldNode and post) accepted; FieldNode has its own renders | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 2 |
| 2026-10-02 | Cable routes in the appearance model: closed, since BRP-DDR-004 set the routes; the appearance model follows the constructable model's routes when the renders are next updated | Amish: "i approve your recommendations for all 555 open decisions." | `docs/REVIEW.md`, 2026-09-26, item 3; BRP-DDR-004, P10 and P11 |
