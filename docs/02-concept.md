---
doc_id: BRP-PRC-001
title: BridgePulse design precis
project: BridgePulse
doc_type: Design precis
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
  change: Concept for TRL 2; architecture, first-order numbers, safety and open questions
---

# BridgePulse design precis

## Summary

BridgePulse is a clamp-on monitor for small bridges and footbridges. A sensor hub bolted to a girder at midspan records ambient vibration, strain and temperature for 10 minutes every hour, works out the bridge's natural frequencies and strain statistics on board, and sends a short summary through a FieldNode core over LoRaWAN to TwinKit or CityTwin. Over weeks the system learns how the frequencies move with temperature; a sustained shift outside that band is flagged to the bridge owner's engineer as a reason to inspect sooner. It is a research prototype that supports inspection, never a safety rating.

First-order estimates (to be checked at TRL 3): about 15 mW average draw, about 0.015 Hz spectral resolution per hourly record, about 36 bytes per hourly uplink, about 1.4 GB per month of raw records kept on a microSD card, and about $342 in parts including the FieldNode core ($216 for the BridgePulse-specific parts).

![Figure 1. BridgePulse on an example 7 m steel footbridge](../media/hero.png)

*Figure 1. Concept render. The monitor clusters at midspan: sensor hub on the south girder, FieldNode core on the handrail post. Grey parts are the existing bridge and a 1.75 m person for scale.*

## How it works

1. **Sense.** A low-noise 3-axis MEMS accelerometer, rigidly fixed inside the hub against the girder web, picks up the bridge's response to wind, footfall and traffic. Two strain gauge half-bridges under the bottom flanges of both girders at midspan measure bending strain. Two temperature probes measure the steel and the shaded air under the deck.
2. **Record.** Once an hour the hub wakes, powers the gauges and samples for 600 s: acceleration at 250 Hz on three axes, strain at 20 Hz on two channels, temperature once a minute. The raw record goes to a microSD card so an engineer can download it later.
3. **Reduce.** The hub computes averaged spectra (Welch method, about 65 s segments with 50 % overlap) and picks the peaks of the first modes below 60 Hz, their amplitudes, the RMS acceleration, and the strain minimum, maximum and mean on each channel.
4. **Send.** The summary, about 36 bytes, passes over a sealed M12 cable to the FieldNode core, which sends it as one LoRaWAN uplink per hour.
5. **Learn and flag.** TwinKit stores the series and fits frequency against steel temperature over a baseline period, following the approach of the Z24 bridge study ([Peeters and De Roeck, 2001](https://doi.org/10.1002/1096-9845%28200102%2930:2%3C149::AID-EQE1%3E3.0.CO;2-Z)). A frequency that stays outside the confidence band for a set period, or a step in the strain baseline, raises a flag to the owner's engineer. TwinKit can also show the measured frequency next to the value calculated from the bridge model.
6. **Act.** The engineer decides whether to inspect. The public CityTwin view shows only that the bridge is monitored and when data last arrived (proposed).

![Figure 2. Hourly data flow](../media/flow.png)

*Figure 2. Hourly data flow. Values are estimates.*

## Main components

Numbers match the exploded view (Figure 3) and `bom/bom.csv`.

| No. | Component | Role |
| --- | --- | --- |
| 1 | Sensor hub enclosure, die-cast aluminium, IP67, about 170 × 110 × 64 mm | Stiff, sealed housing that couples the accelerometer to the girder |
| 2 | Accelerometer board, ADXL355 class | 3-axis, 22.5 µg/√Hz noise density, 200 µA in measurement mode ([Analog Devices](https://www.analog.com/en/products/adxl355.html)) |
| 3 | Signal board: 24-bit bridge ADC (ADS1220 class), low-power microcontroller (RP2040 class, proposed), microSD, gauge excitation switch | Sampling, spectra, features, raw storage |
| 4 | Mounting plate and two beam clamps, stainless steel | Holds the hub against the web by clamping the bottom flange; no drilling |
| 5 | Strain gauge half-bridges (2): each an active 350 Ω foil gauge on the flange plus a dummy gauge on an unstrained coupon of the same steel, with protective coating and cover | Bending strain at midspan of each girder, temperature-compensated |
| 6 | Temperature probes (2), sealed digital type | Steel and shaded air temperature for frequency compensation |
| 7 | Sensor cables, shielded, with M12 connectors and glands | Gauges to hub, hub to FieldNode |
| 8 | FieldNode core: IP65 enclosure, 6 W panel as sun hood, LiFePO4 cell, MPPT charger, LoRaWAN radio, pole clamps | Power, radio and mounting shared across the lab's outdoor projects |

![Figure 3. Exploded view](../media/exploded.png)

*Figure 3. Exploded view with BOM numbers. The girder and post are existing structure.*

![Figure 4. Sensor hub cutaway](../media/cutaway.png)

*Figure 4. Cutaway of the sensor hub. The accelerometer board is fixed to the base of the enclosure on the web side so it moves with the girder.*

## First-order numbers

All values are estimates at TRL 2 and will be checked by calculation at TRL 3.

### Example bridge: natural frequency

For the 7 m example footbridge, treat the deck as a simply supported beam of two IPE 360 class girders:

- Span between bearings L ≈ 6.4 m; E = 210 GPa; I ≈ 16,270 cm⁴ per girder, so EI ≈ 6.8 × 10⁷ N m² for two girders.
- Mass per meter m ≈ 172 kg/m (girders about 114 kg/m, timber deck about 38 kg/m, rails about 20 kg/m).
- f₁ = (π / 2L²) √(EI / m) ≈ 0.0384 × √(3.97 × 10⁵) ≈ **24 Hz**.

The second vertical mode of a simple beam is four times the first, about 97 Hz, outside the 60 Hz band. On this short span only the first vertical mode and possibly a torsional mode are tracked; longer spans bring more modes into the band. Assumptions: pinned supports, no composite action from the timber deck, no pedestrians on the deck.

### Measurement resolution

- Accelerometer output rate 250 Hz with the internal low-pass filter at about 62.5 Hz; usable band about 0.5 to 60 Hz.
- Welch segments of 16,384 samples (65.5 s) give a bin width of about **0.015 Hz**; a 600 s record gives about 17 averaged segments with 50 % overlap.
- Accelerometer noise in one bin: 22.5 µg/√Hz × √0.015 Hz ≈ **2.8 µg**. Across the whole band it is about 180 µg RMS. A clear peak therefore needs a modal response of a few tens of µg or more in that bin; whether quiet footbridges reach this is open question 1.
- With peak interpolation, the random error of one hourly frequency estimate should be a small fraction of a bin (about 0.01 % at 24 Hz, about 0.1 % at 2 Hz). The real limit is environmental: temperature, bearing friction and surfacing stiffness change the frequency far more than the measurement noise does. The 1 % detection target (REQ R3) therefore depends on the temperature model and is **not yet demonstrated**.

### Strain

- Half-bridge with one active gauge and a dummy, gauge factor about 2.0, 3.3 V excitation: output about 1.65 µV per µε.
- Target resolution 2 µε (about 0.4 MPa in steel), to be checked against the ADC's noise at 20 samples per second at TRL 3.
- Example bridge: a crowd load of 5 kN/m² over the 1.5 m deck gives a midspan moment of about 38 kN m, about 21 MPa or **about 100 µε** in each girder. One 80 kg pedestrian at midspan gives only about 3 µε, close to the resolution. Strain on stiff short bridges is small; its main value is spotting a step in the baseline or a change in how the load splits between the two girders.
- Only changes from the day of installation can be measured. Dead-load strain already in the steel is not visible.

### Power and data

| Load during the 600 s window | Estimate |
| --- | --- |
| Microcontroller at reduced clock | about 33 mW |
| Accelerometer | about 0.7 mW |
| 24-bit ADC | about 1.4 mW |
| Gauge excitation, two 700 Ω half-bridges at 3.3 V | about 31 mW |
| microSD writes (average) | about 10 mW |
| Regulator losses (about 10 %) | about 8 mW |
| **Total while recording** | **about 84 mW** |

With one 600 s window per hour (duty 1/6) and about 0.3 mW asleep, the average is **about 15 mW**, or about 0.36 Wh per day. FieldNode's README gives about 115 mW average for sensors, so the hub uses about an eighth of that allowance.

Raw data: 600 s × 250 Hz × 3 axes × 4 bytes ≈ 1.8 MB, plus about 0.1 MB of strain and temperature, so about 1.9 MB per hour, 46 MB per day and **1.4 GB per month**. A 32 GB card holds about 23 months.

Uplink payload per hour: three mode frequencies and amplitudes (12 bytes), RMS acceleration on three axes (6 bytes), strain minimum, maximum and mean on two channels (12 bytes), two temperatures (4 bytes) and status (2 bytes): **about 36 bytes**.

### Cost and mass

About $342 in parts including the FieldNode core (about $126 from the FieldNode README), of which about $216 is BridgePulse-specific. This is **over the $250 project budget**; see `docs/REVIEW.md` for the proposed options. Mass on the bridge is about 0.6 kg for the hub and clamps plus about 1.7 kg for the FieldNode core.

## Key design choices (all proposed, awaiting Amish)

1. **Ambient vibration only.** No shaker or impact hammer; wind, footfall and traffic excite the bridge. Simple and passive, but weak on very quiet bridges.
2. **Separate hub on the girder, FieldNode on a post.** The accelerometer must be on the structure, while the panel needs sun and the radio needs a clear view; putting both in one box would compromise one of them.
3. **Hourly 10 minute windows rather than continuous recording.** Keeps power at about 15 mW and still gives 24 frequency estimates a day. Continuous recording would catch every heavy vehicle but would need about 84 mW.
4. **Temperature-compensated trend, not fixed limits.** A frequency band learned from the bridge's own baseline, with at least four weeks of data before any flag and a full year to cover seasons.
5. **Foil gauge half-bridges with a dummy on a coupon.** Cheaper and easier to fit than weldable or vibrating-wire gauges, at the cost of long-term drift, which must be checked.
6. **One accelerometer at midspan.** Enough for the first vertical and torsional modes. A second unit at quarter span would add mode shape information later.
7. **Built on FieldNode, TwinKit and CityTwin.** The hub connects to one FieldNode M12 sensor port; the pinout and protocol need agreement with the FieldNode project.
8. **Engineer-only alerts.** Flags go to the owner's engineer; the public CityTwin view shows only monitoring status.

## Safety

> **Safety:** BridgePulse is a research prototype. It supports but never replaces inspection by qualified engineers, and a "no change" result never means a bridge is safe. Owners must not defer or skip inspections because a monitor is fitted.

> **Safety:** Installation is work at height, often over water or traffic. Install only with the owner's written permission, with trained crews, fall protection, a rescue plan for work over water, and traffic management as local rules require. Never work alone.

> **Safety:** Old steel bridges may be coated with lead or other hazardous paint. Test before removing any paint for strain gauges; if lead is present, use a trained contractor and local abatement rules. Gauge adhesives and coatings are chemicals: follow their safety data sheets, use gloves and eye protection and ventilate.

> **Safety:** The FieldNode core contains a lithium iron phosphate cell. Use the fused, protected pack and cold-charge lockout specified by FieldNode and never mount a damaged pack.

> **Safety:** Nothing may be drilled, welded or cut into the structure. Clamps must be checked so they cannot loosen and fall onto people, vehicles or boats below; use a secondary lanyard on the hub.

> **Safety:** Fit tamper-resistant fasteners on the post-mounted FieldNode so the public cannot pull it off or hang from it, and keep cables out of reach from the deck.

## Open questions

- [ ] 1. Is ambient excitation enough to identify the first modes of a quiet footbridge above the accelerometer's noise, or is a second, lower-noise sensor option needed?
- [ ] 2. How much do frequencies move with temperature on small steel, concrete and timber bridges, and can a model trained on four weeks of data hold across seasons?
- [ ] 3. What drift do foil strain gauges show outdoors over a year with the proposed coating?
- [ ] 4. Which FieldNode port pinout and serial protocol will the hub use?
- [ ] 5. What is the alert rule (size of shift, duration) and who receives it?
- [ ] 6. Can temperature probes and the hub's temperature drift be checked in the CalRig chamber before deployment?
- [ ] 7. Who owns the data, and what is published openly through CityTwin?
