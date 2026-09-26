---
doc_id: BRP-REQ-001
title: BridgePulse requirements
project: BridgePulse
doc_type: Requirements
version: "0.4"
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
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: R12 redefined per BRP-DDR-001 D1; status of every requirement from BRP-CAL-001; interface assumptions for FieldNode
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002); R2 method (load gating), R5 verification, R7 restated with an 11-byte reduced summary; status from BRP-CAL-001 v0.2
---

# BridgePulse requirements

These are first-pass requirements for the concept. Targets are proposals for review, not yet validated with bridge owners or inspectors, and will be revised after co-design sessions (see BRP-PRB-001). Status is now judged by calculation in BRP-CAL-001 against the parametric model and the priced BOM; "met on paper" is not a verification by test.

**Reference installation.** A steel or concrete footbridge or short-span road bridge of 5 to 30 m span, monitored at midspan, in a climate from −20 to +50 °C, with LoRaWAN coverage and no mains power. The worked example is the 7 m steel footbridge in BRP-PRC-001.

**Changes in v0.3.** R12 is redefined to cost the BridgePulse-specific parts, with the FieldNode core costed in its own repo and the complete cost stated beside it (BRP-DDR-001, D1; decided by Amish, 2026-09-25: go with recommendation). No other target changes.

**Changes in v0.4 (BRP-DDR-002).** R2 keeps its target; its method now gates out the time when people are on the span, backed by a load regression in TwinKit, and is to be checked on recorded data before any change to the target. R5 keeps its target; verification adds an ice-point check, and the probe is now TMP1826 class. R7 is restated so that an 11-byte reduced summary is used wherever the data rate in use limits the payload to 11 bytes. Statuses follow BRP-CAL-001 v0.2.

Table 1. Requirements and status at TRL 3 (BRP-CAL-001 v0.2, Table 5).

| ID | Requirement | Target | Verification | Status at TRL 3 |
| --- | --- | --- | --- | --- |
| R1 | Measure bridge acceleration | 3 axes; noise density 25 µg/√Hz or less; band 0.5 to 60 Hz | Datasheet; later bench noise test | Met by design (22.5 µg/√Hz; 62.5 Hz filter corner) |
| R2 | Track natural frequencies | Every mode with a clear peak below 60 Hz, at least the first vertical mode; bin width 0.02 Hz or less per hourly record; repeatability 0.2 % (1σ) or better over a day of steady temperature | Spectral and load-gating simulation (BRP-CAL-001, B); then recorded data | At risk: with the time when people are on the span gated out, 0.015 % or less in simulation (1 to 20 crossings per record); ungated, walker mass gives 1.5 to 3.1 % |
| R3 | Flag structural change | Flag a sustained shift of 1 % or more in a tracked frequency, after temperature compensation, within 14 days; one false flag per bridge per year or fewer | Detection statistics (BRP-CAL-001, C); then public benchmark data and a field baseline | Not verifiable at TRL 3: needs a daily residual of 0.75 % or less after temperature and load compensation |
| R4 | Measure strain | 2 channels; range ±1,000 µε; resolution 2 µε or better; drift 5 µε per month or less after temperature compensation | ADC noise calculation; later outdoor drift test | Not verifiable at TRL 3 for drift; resolution (0.09 µε RMS) and range met on paper |
| R5 | Measure temperature | Steel surface and shaded air; ±0.5 °C or better, checked against a reference | Datasheet; ice-point check at 0 °C and CalRig chamber check | Met on paper: TMP1826 class, ±0.3 °C from −40 to +105 °C on the datasheet |
| R6 | Stay within the FieldNode energy budget | Average draw 30 mW or less at the FieldNode sensor port | Power calculation; later current logging | Met on paper (16.9 mW) |
| R7 | Send and keep the data | One summary per hour of 48 bytes or less, within LoRaWAN regional limits at the data rate in use, with an 11-byte reduced summary (first frequency, its amplitude, two strain means, steel temperature, status) wherever the limit is 11 bytes; raw records kept on site for 12 months or more | Payload and airtime calculation; storage calculation | Met on paper: 36 bytes, or 11 bytes at US915 DR0 and AS923 DR2 (AS923 limit assumed); 22 months on 32 GB |
| R8 | Fit without harming the structure | No drilling, welding or cutting; strain gauges only on an area of paint removed and recoated with the owner's permission; fitted by two trained people in 4 h or less from below or beside the deck | Fitting sequence estimate; later trial fit | Not verifiable at TRL 3 for time (2.8 h estimate); no drilling or welding met by design |
| R9 | Keep clear of what passes under and over the bridge | Nothing more than 15 mm below the girder soffit; nothing on the deck side except the FieldNode on a handrail post, with tamper-resistant fasteners | Model check | Met on paper (10 mm; hub inside the girder outline) |
| R10 | Survive outdoors | Hub IP67, FieldNode IP65; operate from −20 to +50 °C; 5 years with one gauge recoat and no cell replacement | Datasheets and design review; later environmental checks | At risk: FieldNode heat (FND-CAL-001) and gauge coating life |
| R11 | Protect privacy | No cameras or microphones; only structural readings leave the device | Design review | Met by design |
| R12 | Affordable | BridgePulse-specific parts $250 or less, with the complete cost including the FieldNode core stated beside it | Priced BOM (`bom/bom.csv`) | At risk: $248.00 (0.8 % margin); complete $374.00 |
| R13 | Present results responsibly | Every output labeled as monitoring data that supports inspection; no pass or fail safety rating anywhere in the system | Review of dashboard and report templates | Met by design intent; not yet implemented |

## Requirements not met or at risk

No requirement is now shown as not met.

- **R2 (repeatability) at risk:** on a light footbridge the mass of each walker lowers the first mode by up to 6.3 %. Gating out the time when someone is on the span meets 0.2 % in simulation, but the footfall model is idealized and the method must be checked on recorded data (TRL 4, on hold).
- **R3 (change detection) not verifiable at TRL 3:** it depends on modeling temperature and any remaining load effect to a daily residual of 0.75 % or less.
- **R10 and R12 at risk:** FieldNode heat and coating life, and a $2.00 cost margin on indicative prices.
- **R4 and R8 not verifiable at TRL 3:** gauge drift and fitting time need tests or a trial fit.

## Assumptions

- The accelerometer follows the ADXL355 datasheet summary ([Analog Devices](https://www.analog.com/en/products/adxl355.html)); a different part must meet R1.
- The FieldNode core offers 100 mW average for sensors as its design value (115 mW ceiling, FND-CAL-001) and two sealed M12 5-pin ports with a switched rail. BridgePulse assumes RS-485 and a 5 V rail on FieldNode's candidate pinout, which is still open (BRP-DDR-001, O1).
- A temperature-compensated frequency baseline needs at least four weeks of data before any flag, following the approach of [Peeters and De Roeck (2001)](https://doi.org/10.1002/1096-9845%28200102%2930:2%3C149::AID-EQE1%3E3.0.CO;2-Z).
- Steel modulus 210 GPa for converting strain to stress. The other calculation assumptions are in BRP-CAL-001, Table 1.
