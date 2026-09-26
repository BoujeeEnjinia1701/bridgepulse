# BridgePulse

![TRL 2](https://img.shields.io/badge/TRL-2%20of%209-0F766E) ![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/hardware-CERN--OHL--S--2.0-111827) ![Software: MIT](https://img.shields.io/badge/software-MIT-111827)

**Area:** Smart Cities · **TRL:** 2 of 9 (concept formulated) · **Prototype budget:** about $250 USD · **Difficulty:** 3 of 5

A vibration and strain monitor for small bridges and footbridges that tracks natural frequency and strain over time to flag changes that need inspection.

![BridgePulse concept](media/hero.png)

[Interactive 3D model](media/viewer.html) · [Concept blueprint (PDF)](media/concept-blueprint.pdf) · [Review note](docs/REVIEW.md)

## Concept rationale

A bridge's natural frequencies depend on its stiffness, so a loss of stiffness from corrosion, cracking or a failing bearing shows up as a small, lasting drop in frequency, and a change in how load is carried shows up in strain. The difficulty is that temperature moves the frequencies too. The Z24 bridge study showed that a model of frequency against temperature, learned from the healthy bridge, can separate the two ([Peeters and De Roeck, 2001](https://doi.org/10.1002/1096-9845%28200102%2930:2%3C149::AID-EQE1%3E3.0.CO;2-Z)). BridgePulse applies that idea with one clamp-on sensor hub at midspan, hourly 10 minute records and a learned temperature band, so the owner's engineer gets a reason to inspect sooner rather than a stream of raw data.

It is open and garage-buildable because the owners of small bridges, such as towns, counties, park services and rural access programs, are the ones least able to pay for commercial monitoring. Low-noise MEMS accelerometers now cost tens of dollars, the hub clamps on without drilling, and power, radio and data handling come from the lab's shared FieldNode, TwinKit and CityTwin projects. Open design files and open methods also let engineers check how a flag was raised, which matters more than the hardware.

## Burning platform

Bridge stock is large, aging and inspected at long intervals. In the United States, 41,685 of 624,193 bridges (6.7 %) were in poor condition in 2025 ([FHWA](https://www.fhwa.dot.gov/bridge/nbi/no10/condition25.cfm)), and routine inspections may be 24, 48 or, under a risk-based method, up to 72 months apart ([23 CFR 650.311](https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-650/subpart-C/section-650.311)). In Japan, about 37 % of roughly 730,000 road bridges were 50 years old or more in 2023, rising to about 54 % by 2030 ([MLIT](https://www.mlit.go.jp/sogoseisaku/maintenance/02research/02_01.html)).

Findings also have to reach someone who acts. The Fern Hollow Bridge in Pittsburgh collapsed in January 2022 after the city failed to act on repeated maintenance recommendations in its inspection reports ([NTSB](https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx)). A monitor cannot replace inspection or funding, but a clear, early signal on a specific bridge can help put limited inspection time where it is needed.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| Municipal and county public works | Watching footbridges and short road bridges between routine inspections, and after floods or vehicle strikes |
| Parks, trails and recreation | Timber and steel trail bridges that see few inspections and many visitors |
| Rural access and humanitarian programs | Checking a sample of trail bridges built years earlier without a site visit to each one |
| Rail and transit operators | Station footbridges and pedestrian overbridges |
| Forestry and mining | Haul road and forestry bridges carrying heavy, irregular loads |
| Universities and training | An open platform for teaching and research in vibration-based structural health monitoring |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| United States | 41,685 bridges were rated poor in 2025 ([FHWA](https://www.fhwa.dot.gov/bridge/nbi/no10/condition25.cfm)); many are small, locally owned structures. |
| Great Britain | 2,928 council-maintained road bridges were substandard in 2023, with a £6.8 billion backlog; councils also report growing concern about flooding and scour ([RAC Foundation](https://www.racfoundation.org/media-centre/changing-weather-patterns-worrying-bridge-engineer)). |
| Japan | The share of road bridges 50 years old or more is set to rise from about 37 % to about 54 % between 2023 and 2030 ([MLIT](https://www.mlit.go.jp/sogoseisaku/maintenance/02research/02_01.html)). |
| Nicaragua and Central America | Floods cut labor income by about 18 % in villages without a footbridge, and new bridges removed that loss ([Brooks and Donovan, 2020](https://doi.org/10.3982/ECTA15828)); keeping existing footbridges in service protects that gain. |
| Rwanda and East Africa | Trail bridge programs report a preliminary annual return of about 49 % on trail bridges in Rwanda and similar settings ([Fika, formerly Bridges to Prosperity](https://fika.org/measuring-roi-for-trail-bridges/)), so a growing stock of footbridges will need low-cost ways to check them. |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It feeds CityTwin. The trigger in the wider world is the gap between inspection and action shown by the 2022 Fern Hollow Bridge collapse ([NTSB](https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx)) and the fast-aging bridge stock in countries such as Japan.

## Problem

Many small bridges are inspected rarely, and deterioration is found late. Their owners seldom have the budget for commercial monitoring, so there is no record of how a bridge behaves between inspections. See the [problem statement](docs/01-problem.md).

## Concept

A vibration and strain monitor for small bridges and footbridges that tracks natural frequency and strain over time to flag changes that need inspection. A sensor hub clamped to a girder at midspan records 10 minutes of acceleration, strain and temperature every hour, extracts the natural frequencies and strain statistics on board, and sends about 36 bytes per hour through a FieldNode core over LoRaWAN to TwinKit or CityTwin. A temperature-compensated baseline, learned over weeks, flags lasting changes to the owner's engineer.

First-order estimates (to be checked at TRL 3): about 15 mW average draw, about 0.015 Hz spectral resolution per record, about 1.4 GB of raw records per month kept on site, and about $342 in parts including the FieldNode core ($216 BridgePulse-specific), which is over the $250 budget. The 1 % frequency shift detection target is not yet demonstrated. See the [requirements](docs/03-requirements.md) for what is and is not met.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Sensor hub: IP67 die-cast aluminium enclosure clamped to the girder, no drilling
- Low-noise 3-axis MEMS accelerometer (ADXL355 class)
- Signal board with 24-bit bridge ADC, low-power microcontroller and microSD card
- Two strain gauge half-bridges with temperature-compensating dummy gauges
- Two temperature probes (steel and air)
- Shielded sensor cables with M12 connectors
- FieldNode core (shared lab component): 6 W panel, LiFePO4 cell, MPPT charger and LoRaWAN radio

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> A research prototype; it supports but never replaces inspection by qualified engineers, and a "no change" result never means a bridge is safe. Install only with the asset owner's permission, by trained crews, with fall protection, a rescue plan for work over water and traffic management as local rules require. Test old paint for lead before removing any for strain gauges. The FieldNode core contains a lithium iron phosphate cell; use its protected, fused pack. Nothing is drilled or welded into the structure, and every clamped part carries a secondary lanyard.

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Documentation

Controlled documents follow the portfolio [documentation standard](.kit/STANDARDS.md). Each carries a document ID (BRP-PRC-001 for the precis), a version and a revision history. Branded PDFs are built with `python .kit/render.py` and attached to GitHub Releases when a document is tagged, for example `BRP-PRC-001/v1.0`.

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Smart cities set.
