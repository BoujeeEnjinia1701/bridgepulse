---
doc_id: BRP-DDR-001
title: BridgePulse TRL 2 review decisions
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
  change: Record the TRL 2 review recommendations adopted for TRL 3 work under Amish's 2026-09-25 instruction, and the items that remain open
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** proposed. The recommendations in items D1 to D11 are adopted for TRL 3 work pending Amish's review; items O1 to O3 remain "Proposed, awaiting Amish".

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed ten items as "Proposed, awaiting Amish", and the design precis BRP-PRC-001 v0.2 listed eight key design choices, all marked proposed. On 2026-09-25 Amish asked for this batch of Design Molecule repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carried a recommendation is therefore adopted as recommended for TRL 3 work, open for his review. Items without a recommendation stay open. Nothing here is recorded as decided or approved by Amish.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in BRP-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items adopted for TRL 3 work.*

| # | Item | Adopted recommendation | Status |
| --- | --- | --- | --- |
| D1 | Budget and R12 (review item 1) | Option (a): keep `budget_usd` at $250 and redefine R12 as "BridgePulse-specific parts $250 or less", with the FieldNode core costed in its own repo and the complete-system cost always stated beside it. No new budget figure was recommended | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D2 | Excitation (review item 2) | Ambient vibration only, no shaker or impact hammer, for TRL 3; revisit if quiet footbridges give no clear peaks | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D3 | Recording pattern (review item 3) | Hourly 10 minute windows rather than continuous recording | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D4 | Layout (review item 4) | Separate sensor hub on the girder; FieldNode core on a handrail post | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D5 | Strain gauges (review item 5) | Foil gauge half-bridges with dummy gauges, for cost, with drift checked early | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D6 | Accelerometers (review item 6) | One accelerometer at midspan; a second at quarter span kept as a later option | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D7 | Hub microcontroller (review item 7) | RP2040 class, for cost and tooling | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D8 | Alert policy and public view (review item 9) | Flags go only to the owner's engineer; the public CityTwin view shows monitoring status only | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D9 | Temperature-compensated trend (precis choice 4) | A frequency band learned from the bridge's own baseline, with at least four weeks of data before any flag and a full year to cover seasons, instead of fixed limits | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D10 | Shared lab components (precis choice 7) | Built on FieldNode (power, radio, one M12 sensor port), TwinKit and CityTwin | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D11 | Pitch and problem | The TRL 2 note recommended no change: the figures found support them. The pitch and problem lines in `project.yaml` and `README.md` are unchanged | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |

*Table 2. Items that remain open.*

| # | Item | Status |
| --- | --- | --- |
| O1 | FieldNode sensor port pinout and protocol (review item 8). No recommendation was made; it is to be agreed with the FieldNode project, whose own pinout is also open (FND-DDR-001, O2). For TRL 3 work this repo assumes FieldNode's candidate (pin 1 switched rail, 2 data A, 3 ground, 4 data B, 5 analog) with RS-485 on pins 2 and 4 and the rail at 5 V; this is a working assumption, not a choice. | Proposed, awaiting Amish and the FieldNode project |
| O2 | First host bridge and co-design partner (review item 10). No preference stated and no recommendation made. | Proposed, awaiting Amish |
| O3 | Data ownership and what is published beyond monitoring status (precis open question 7). No recommendation was made. | Proposed, awaiting Amish |

## Consequences

- `project.yaml`: only the TRL fields and the evidence list change. `budget_usd` stays at $250, and the pitch and problem are unchanged (D11).
- BRP-PRB-001, BRP-PRC-001 and BRP-REQ-001 are revised to v0.3. The design choices in the precis are no longer described as "proposed"; they are adopted for TRL 3 work pending Amish's review.
- Requirement R12 is redefined per D1: the target is BridgePulse-specific parts of $250 or less, with the complete cost including the FieldNode core stated beside it. No other target changes as a result of these decisions.
- The TRL 3 calculations (BRP-CAL-001) led to design changes within these decisions: the mounting plate now stands on the bottom flange and is jacked against the top flange, so that the hub's mounting resonance clears the measured band; the hub is powered from FieldNode's switched 5 V rail and is off between records; it post-processes each record from the microSD card; and the frequency is estimated by a curve fit rather than peak picking.
- BRP-CAL-001 finds R2 not met on the example footbridge because walkers' mass shifts the frequency, and R7 at risk in US915 and AS923. The responses to these are proposed in `docs/REVIEW.md` and are not decided by this record.
- TRL 4 is on hold by Amish's instruction. Nothing in this record authorizes building or testing.
