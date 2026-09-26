---
doc_id: BRP-PRB-001
title: BridgePulse problem statement
project: BridgePulse
doc_type: Problem statement
version: "0.3"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Problem, users, context, constraints, prior work and open questions for TRL 2
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Budget constraint per BRP-DDR-001 D1; example bridge frequency and cost from BRP-CAL-001; open question on people's mass added
---

# BridgePulse problem statement

Small bridges and footbridges are inspected by eye at long intervals, and deterioration between visits is found late or not at all. Owners of these structures (towns, counties, park services and rural access programs) rarely have the budget for commercial structural health monitoring, so there is no record of how a bridge behaves between one inspection and the next.

## The problem in numbers

- In the United States, 41,685 of 624,193 bridges (6.7 %) were rated in poor condition in 2025 ([FHWA, National Bridge Inventory](https://www.fhwa.dot.gov/bridge/nbi/no10/condition25.cfm)). The routine inspection interval under the National Bridge Inspection Standards is up to 24 months, and some bridges may go 48 or, under a risk-based method, 72 months between routine inspections ([23 CFR 650.311](https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-650/subpart-C/section-650.311)).
- In Great Britain, 2,928 of 73,208 council-maintained road bridges (4 %) were substandard in 2023, with an estimated maintenance backlog of £6.8 billion ([RAC Foundation, 2024](https://www.racfoundation.org/media-centre/changing-weather-patterns-worrying-bridge-engineer)).
- In Japan, about 37 % of roughly 730,000 road bridges were 50 years old or more in March 2023, rising to about 54 % by 2030 ([MLIT](https://www.mlit.go.jp/sogoseisaku/maintenance/02research/02_01.html)).
- Inspection findings only help if they lead to action. The Fern Hollow Bridge in Pittsburgh collapsed on January 28, 2022; the NTSB found that corrosion and section loss caused the failure and that the city had failed to act on repeated maintenance recommendations in inspection reports ([NTSB, HWY22MH003](https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx)).

## Users and context

| User | Need |
| --- | --- |
| Bridge owner's engineer (town, county, park service, rural roads agency) | A low-cost signal, between inspections, that a particular bridge has changed and should be looked at sooner |
| Bridge inspector | A trend record (natural frequency, strain range, temperature) to take on site and compare with what is seen |
| Rural access and trail bridge programs | A way to check a sample of footbridges they built years ago without a site visit to each one |
| Researchers and students | An open, documented platform for vibration-based structural health monitoring on real structures |
| Residents and bridge users | Confidence that the bridge they cross is being watched, through CityTwin, without the monitor collecting anything about them |

**Target structures.** Footbridges and short-span road bridges with spans of roughly 5 to 30 m, in steel, concrete or timber, where the first vertical modes are expected to lie between about 1 and 50 Hz (estimate, to confirm per bridge). The worked example in the media is a 7 m steel footbridge on two I-girders; its first vertical mode is 23.9 Hz by a simple beam calculation, and one walker at midspan lowers it by about 6 % (BRP-CAL-001).

**Operating environment.** Outdoors, under or beside a deck over water or a road: rain, splash, condensation, freeze and thaw, UV on the solar panel, birds and vandalism. No mains power on site. Radio coverage by LoRaWAN, either a public network or the lab's TwinKit gateway.

## Constraints

- Garage-buildable prototype. The project budget in `project.yaml` is $250 USD for the BridgePulse-specific parts, with the FieldNode core costed in its own repo (BRP-DDR-001, D1, adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review). The BridgePulse-specific parts cost $244 and the complete monitor $370 (BRP-CAL-001).
- Built on the lab's FieldNode core for power, enclosure and radio; readings go to TwinKit and CityTwin.
- No drilling or welding of the structure. Strain gauges need a small area of paint removed and recoated, which needs the owner's permission.
- Installation from below or beside the deck without closing a road bridge to traffic where possible; work at height and over water follows the owner's rules.
- The monitor supports inspection by qualified engineers; it never replaces it and never issues a safety rating.
- Only structural readings leave the device. There are no cameras or microphones.

## Prior work

- **Vibration-based damage detection.** Loss of stiffness lowers natural frequencies, but normal changes from temperature, humidity and boundary conditions can be as large as those from damage. The one-year monitoring of the Z24 bridge in Switzerland, before it was damaged on purpose, is the reference case: black-box models of eigenfrequency against temperature were fitted to healthy data, and new data outside their confidence bands pointed to a cause other than temperature ([Peeters and De Roeck, 2001](https://doi.org/10.1002/1096-9845%28200102%2930:2%3C149::AID-EQE1%3E3.0.CO;2-Z)). BridgePulse follows the same approach at low cost.
- **Low-noise MEMS accelerometers.** Parts such as the ADXL355 (22.5 µg/√Hz noise density, 200 µA in measurement mode) make ambient vibration measurement affordable ([Analog Devices](https://www.analog.com/en/products/adxl355.html)).
- **Commercial monitoring systems.** Wireless structural monitoring systems for bridges are sold commercially, but they are priced and supported for large asset owners and are closed. There is no widely used open design for small bridges that we have found; this needs a proper review at TRL 3.
- **Why small footbridges matter.** In rural Nicaragua, seasonal floods cut household labor market income by about 18 % where there was no bridge, and new footbridges removed that loss ([Brooks and Donovan, 2020](https://doi.org/10.3982/ECTA15828)). Keeping such bridges in service matters as much as building them.

## Out of scope

- Load rating, safety rating or any statement that a bridge is safe.
- Long-span, cable-supported or major highway bridges, which need engineered monitoring systems.
- Scour, bearing and foundation monitoring (possible later add-ons, for example with FloodGauge on the same stream).
- Cameras, audio, vehicle or pedestrian identification.

## Open questions

- [ ] Which owners would host a first installation, and on what kind of bridge?
- [ ] Is ambient excitation (wind, footfall, traffic) enough to identify the first modes of a quiet footbridge with a MEMS accelerometer?
- [ ] How large are temperature-driven frequency changes on small bridges, especially with asphalt surfacing or frozen bearings, compared with a 1 % damage signal?
- [ ] On light footbridges, the mass of the people crossing changes the frequency by more than the 1 % change the monitor must detect (BRP-CAL-001). Can the method separate the two, or should the first installations favor heavier bridges?
- [ ] Who receives an alert, and what is the agreed action when one is raised?
- [ ] Is paint removal for strain gauges acceptable to owners, and is old paint likely to contain lead?

## User research and co-design

This design is for communities the author is not part of, so requirements come from the people who will use it.

- [ ] Identify a local partner organization (Helpful Engineering network, NGO or university)
- [ ] Run co-design sessions with intended users; record who, where and what was learned
- [ ] Validate load, distance, terrain and cost assumptions in the field
- [ ] Revise requirements (REQ) from findings before freezing the design
