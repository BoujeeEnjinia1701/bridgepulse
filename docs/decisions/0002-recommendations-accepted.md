---
doc_id: BRP-DDR-002
title: BridgePulse recommendations accepted
project: BridgePulse
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002); record every newly decided item, what changed in the repo and the items still open
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Every item below that carried a recommendation is decided by Amish, 2026-09-25: go with recommendation. Items without a recommendation remain "Proposed, awaiting Amish".

## Context

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Before that, the TRL 2 review items were recorded in BRP-DDR-001 as adopted for TRL 3 work, open for his review, and the TRL 3 review (`docs/REVIEW.md`, session 2026-09-25, TRL 3) added four new items. Where a recommendation offered several options, the recommended option is the decision. The portfolio stays at TRL 3; TRL 4 is on hold by Amish's instruction, so any decided item that needs a build, test, measurement or purchase is recorded as decided but on hold.

## Options considered

The options for each item are those in `docs/REVIEW.md` (sessions 2026-09-25, /populate and TRL 3) and in BRP-DDR-001.

## Decision

*Table 1. Items decided by Amish, 2026-09-25: go with recommendation.*

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| D1 to D11 | BRP-DDR-001 items (budget and R12, ambient excitation, hourly windows, hub on girder and FieldNode on post, foil half-bridges, one accelerometer, RP2040 class controller, engineer-only alerts, temperature-compensated trend, shared lab components, no change to pitch or problem) | As recommended in BRP-DDR-001 | Status wording in BRP-DDR-001 (v0.2), BRP-PRB-001, BRP-PRC-001, BRP-REQ-001 and `bom/bom-notes.md`. `budget_usd` stays at $250, which covers the BridgePulse-specific parts (D1: the recommendation redefined what the budget covers, applied to R12 at v0.3; no new figure). Pitch and problem unchanged (D11) |
| D12 | R2 and people's mass (TRL 3 review item 4) | Options (a) and (b) together: gate out record segments while someone is on the span, found from the strain step or acceleration envelope, and regress each hourly frequency on a load indicator in TwinKit; R2 stays at 0.2 % until the method is checked on recorded data | Firmware rule in BRP-PRC-001 v0.4 (gate from the strain step with 0.25 s either side; accept a fit only if the peak is 10 dB above noise with plausible damping; otherwise report "no clear peak"). BRP-CAL-001 v0.2 simulates it: scatter 0.015 % or less against 1.5 to 3.1 % ungated. R2 moves from not met to at risk; target unchanged (BRP-REQ-001 v0.4). The check on recorded footfall is TRL 4: decided, on hold. The regression runs in TwinKit (cross-repo action) |
| D13 | Reduced payload (TRL 3 review item 5) | Adopt an 11-byte summary for data rates limited to 11 bytes (US915 DR0, AS923 DR2 with dwell time), used once the region is known | R7 restated in BRP-REQ-001 v0.4; summary defined in BRP-PRC-001 v0.4 and BRP-CAL-001 v0.2, section G (first frequency, its amplitude, two strain means, steel temperature, status with gated seconds; 371 ms at SF10). The hub picks it when FieldNode reports an 11-byte limit, so R7 is met on paper whichever region is chosen. The region itself stays open in FieldNode |
| D14 | Cold-range temperature (TRL 3 review item 6) | Ice-point check plus a probe specified over the full range, since one fits the cost margin | Item 6 is now a TMP1826 class 1-Wire probe potted in a stainless sheath, ±0.3 °C from −40 to +105 °C on the maker's page, $6.00 each (was a DS18B20 class probe at $4.00). R5 verification adds an ice-point check; R5 moves from at risk to met on paper. BOM, BOM notes, BRP-PRC-001 v0.4, BRP-CAL-001 v0.2 (section E) and drawing BRP-DWG-001 Rev P2 (probe note) updated. The ice-point and CalRig checks are TRL 4: decided, on hold |
| D15 | Cost margin (TRL 3 review item 7) | No change now; if quotes come in higher, the first savings are a consumer high-endurance card and a cheaper accelerometer breakout that still meets R1 | Recorded in `bom/bom-notes.md` and BRP-CAL-001 v0.2, section K. With D14 the BridgePulse-specific parts are $248.00 (was $244.00), a $2.00 margin (was $6.00); complete monitor $374.00 (was $370.00). Obtaining quotes is purchasing (TRL 4): on hold |

*Table 2. Items that remain open.*

| # | Item | Status |
| --- | --- | --- |
| O1 | FieldNode sensor port pinout and protocol. No recommendation was made; the FieldNode candidate pinout remains a working assumption | Proposed, awaiting Amish and the FieldNode project |
| O2 | First host bridge and co-design partner. No preference stated | Proposed, awaiting Amish |
| O3 | Data ownership and what is published beyond monitoring status. No recommendation was made | Proposed, awaiting Amish |
| O4 | LoRaWAN region for the first installation (FND-DDR-001, O1). No recommendation in this repo; D13 makes R7 independent of it | Proposed, awaiting Amish |

## Consequences

- Requirement status (BRP-CAL-001 v0.2): 0 not met, 3 at risk (R2, R10, R12), 3 not verifiable at TRL 3 (R3, R4, R8), 4 met on paper (R5, R6, R7, R9), 3 met by design (R1, R11, R13). Before: 1 not met, 4 at risk, 3 not verifiable, 2 met on paper, 3 met by design.
- `project.yaml`: only the evidence list gains this record; `budget_usd` stays at $250, with `trl: 3` and `trl_target: 3`.
- Cross-repo actions, listed in `docs/REVIEW.md`: TwinKit to host the load regression of D12; FieldNode to review mounting its V-block clamps on a 50 mm square handrail post and to report the payload limit of the data rate in use to the sensor port (D13); FieldNode pinout (O1). No other repo is edited here.
- TRL 4 remains on hold by Amish's instruction. Nothing in this record authorizes building, testing, measuring or purchasing.
