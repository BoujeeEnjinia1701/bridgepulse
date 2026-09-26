---
doc_id: BRP-REQ-001
title: BridgePulse requirements
project: BridgePulse
doc_type: Requirements
version: "0.2"
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
  change: First measurable requirements for TRL 2, with status against the concept estimates
---

# BridgePulse requirements

These are first-pass requirements for the concept. Targets are proposals for review, not yet validated with bridge owners or inspectors, and will be checked by calculation at TRL 3 and revised after co-design sessions (see BRP-PRB-001). Status is judged against the estimates in BRP-PRC-001; "met on estimate" is not a verification.

**Reference installation.** A steel or concrete footbridge or short-span road bridge of 5 to 30 m span, monitored at midspan, in a climate from −20 to +50 °C, with LoRaWAN coverage and no mains power. The worked example is the 7 m steel footbridge in BRP-PRC-001.

Table 1. Requirements and status at TRL 2.

| ID | Requirement | Target | Verification (TRL 3 or later) | Status at TRL 2 |
| --- | --- | --- | --- | --- |
| R1 | Measure bridge acceleration | 3 axes; noise density 25 µg/√Hz or less; band 0.5 to 60 Hz | Datasheet; later bench noise test | Met on datasheet (22.5 µg/√Hz) |
| R2 | Track natural frequencies | Every mode with a clear peak below 60 Hz, at least the first vertical mode; bin width 0.02 Hz or less per hourly record; repeatability 0.2 % (1σ) or better over a day of steady temperature | Spectral calculation; later field data | Bin width met by design (about 0.015 Hz); repeatability not verified |
| R3 | Flag structural change | Flag a sustained shift of 1 % or more in a tracked frequency, after temperature compensation, within 14 days; one false flag per bridge per year or fewer | Analysis of public benchmark data (for example Z24), then field baseline | **Not demonstrated**; depends on excitation and the temperature model |
| R4 | Measure strain | 2 channels; range ±1,000 µε; resolution 2 µε or better; drift 5 µε per month or less after temperature compensation | ADC noise calculation; later outdoor drift test | Resolution plausible on estimate; drift not verified |
| R5 | Measure temperature | Steel surface and shaded air; ±0.5 °C or better, checked against a reference | Datasheet; CalRig chamber check | Not verified |
| R6 | Stay within the FieldNode energy budget | Average draw 30 mW or less at the FieldNode sensor port | Power calculation; later current logging | Met on estimate (about 15 mW) |
| R7 | Send and keep the data | One summary per hour of 48 bytes or less, within LoRaWAN regional limits at the data rate in use; raw records kept on site for 12 months or more | Payload design; storage calculation | Met on estimate (about 36 bytes; about 23 months on 32 GB); regional limits not checked |
| R8 | Fit without harming the structure | No drilling, welding or cutting; strain gauges only on an area of paint removed and recoated with the owner's permission; fitted by two trained people in 4 h or less from below or beside the deck | Fitting sequence review; later trial fit | Met by design for drilling and welding; fitting time not verified |
| R9 | Keep clear of what passes under and over the bridge | Nothing more than 15 mm below the girder soffit; nothing on the deck side except the FieldNode on a handrail post, with tamper-resistant fasteners | Model check | Met in the concept model (about 12 mm) |
| R10 | Survive outdoors | Hub IP67, FieldNode IP65; operate from −20 to +50 °C; 5 years with one gauge recoat and no cell replacement | Datasheets and design review; later environmental checks | Not verified |
| R11 | Protect privacy | No cameras or microphones; only structural readings leave the device | Design review | Met by design |
| R12 | Affordable | Complete system, including the FieldNode core, $250 or less in parts | Priced BOM (`bom/bom.csv`) | **Not met**: about $342 in total; about $216 without the FieldNode core |
| R13 | Present results responsibly | Every output labeled as monitoring data that supports inspection; no pass or fail safety rating anywhere in the system | Review of dashboard and report templates | Met by design intent; not yet implemented |

## Requirements not met or at risk

- **R12 (cost) not met:** about $342 against $250. Options are set out in `docs/REVIEW.md`.
- **R3 (change detection) not demonstrated:** it depends on quiet bridges giving a usable signal and on a temperature model that holds across seasons.
- **R2, R4, R5 and R10 not verified:** they rest on datasheets and estimates only.

## Assumptions

- The accelerometer follows the ADXL355 datasheet summary ([Analog Devices](https://www.analog.com/en/products/adxl355.html)); a different part must meet R1.
- The FieldNode core offers about 115 mW average for sensors, as stated in its README, and a sealed M12 sensor port.
- A temperature-compensated frequency baseline needs at least four weeks of data before any flag, following the approach of [Peeters and De Roeck (2001)](https://doi.org/10.1002/1096-9845%28200102%2930:2%3C149::AID-EQE1%3E3.0.CO;2-Z).
- Steel modulus 210 GPa for converting strain to stress.
