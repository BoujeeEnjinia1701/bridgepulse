---
doc_id: BRP-CAL-001
title: BridgePulse sizing calculations
project: BridgePulse
doc_type: Calculation
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (bridge dynamics, excitation and frequency precision by simulation, change detection statistics, strain, temperature, power, data and uplink, mounting stiffness and clearance, installation time, outdoor life, cost)
---

# BridgePulse sizing calculations

On paper, BridgePulse can measure what it sets out to measure, but on a light footbridge the people crossing it get in the way of the answer. Of its thirteen requirements, five are met (two by calculation, three by design), four are at risk, three cannot be verified at TRL 3, and one is not met. The miss is R2, the day-to-day repeatability of the tracked frequency. The instrument itself is good enough: a simulation of the hourly record shows that, with a curve fit in place of simple peak picking, the scatter from sensor noise is 0.05 % at a modest 100 µg of bridge response, close to the theoretical floor. But on the 7 m example footbridge one 75 kg walker adds enough mass to lower the first mode by about 5 % while they cross, so the hourly estimate moves with who happened to walk over, and the 0.2 % target would need about 26 single crossings every hour. R3, the 1 % change detection, then depends on how well a model can remove that effect together with temperature; this note sets the target that model must meet (a daily residual of 0.75 % or less), which only field data can confirm. The calculations also changed the mounting: the TRL 2 plate, held only at the bottom flange, would have resonated at about 77 Hz, too close to the measured band, so the plate now stands on the bottom flange and is jacked against the top flange (126 to 253 Hz). Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [A3], is the line of that script's output that carries it.

> **Safety:** These are first-principles estimates for a paper proof of concept. They say nothing about whether any bridge is safe. BridgePulse supports inspection by qualified engineers and never replaces it. Installation is work at height, over water or near traffic, and may disturb lead paint; see BRP-PRC-001, Safety.

## Scope and method

The note checks every requirement in BRP-REQ-001 v0.3 against the design in BRP-PRC-001 v0.3 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS`, `derived()` and part solids, so the girder section, plate, hub position, clearances and part volumes used here are the ones in the STEP files and in drawing BRP-DWG-001. It also reads `bom/bom.csv` and `budget_usd` in `project.yaml`. Run it from the repo root with `python docs/04-calcs/sizing.py`; it takes about 10 s, most of it the simulation in section B, which uses a fixed random seed so its figures repeat exactly.

The design case is the example bridge of BRP-PRC-001: a 7 m steel footbridge, 6.4 m between bearings, on two IPE 360 class girders at 1.2 m centers with a 50 mm timber deck, monitored at midspan, with a FieldNode core on the midspan handrail post reporting hourly over LoRaWAN.

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Bridge | Simply supported, pinned bearings, no composite action from the deck; girder section from the model's rectangles (no root fillets); steel 210 GPa, 7,850 kg/m³; timber deck 500 kg/m³; rails and posts 20 kg/m | Screening model; the catalog IPE 360 is slightly stiffer [A1] |
| Temperature | Steel modulus falls by 0.03 % per kelvin | Typical for structural steel near room temperature; assumed |
| Damping | 1 % of critical in the first vertical mode | Assumed; light steel footbridges are often lower, which would sharpen the peak |
| Footfall | 75 kg walker at 2 Hz and 1.3 m/s; an effective heel-strike impulse of 2 N·s on a mode above 10 Hz | Order-of-magnitude assumption, to be measured |
| Accelerometer | ADXL355 class, 22.5 µg/√Hz, white; 250 Hz output data rate with the filter corner at 62.5 Hz | Maker's product page (BRP-PRB-001) |
| Spectra | Hann window, 16,384-point segments, 50 % overlap over a 600 s record | As BRP-PRC-001 |
| Strain | Gauge factor 2.0; 350 Ω gauges; 3.3 V excitation; ADC noise 0.15 µV RMS at 20 SPS and gain 128; gauge-to-dummy thermal mismatch 1 µε/K | ADS1220 class; the noise figure is assumed because the maker's product page does not state one |
| Power | 5 V switched rail from the FieldNode port, 85 % buck in the hub, 90 % FieldNode rail converters; the hub is off between records | FieldNode D5 and FND-CAL-001 |
| Radio | 13 bytes of LoRaWAN overhead; 125 kHz, coding rate 4/5, 8-symbol preamble, explicit header; regional payload limits of the LoRaWAN Regional Parameters (EU868, US915, AS923) | Standard values; the regional limits were not checked against the source in this session |
| Wind | 35 m/s gust, air 1.225 kg/m³, drag 1.3 on the FieldNode enclosure; 52.2 N on its panel | FND-CAL-001 |

## A. Example bridge dynamics (R2, R3)

- **Section and mass.** One girder from the model's rectangles has I = 15,524 cm⁴ and W = 862 cm³, about 5 % below the catalog IPE 360 [A1]. The span carries 167 kg/m, and EI for the two girders is 6.52 × 10⁷ N·m² [A2].
- **First mode.** f₁ = (π / 2L²) √(EI / m) = 23.9 Hz; the second vertical mode is 96 Hz, outside the band, so only the first vertical mode (and possibly a torsional mode) is tracked on this span. The modal mass is 535 kg [A3]. The TRL 2 estimate of 24 Hz stands.
- **What a 1 % shift means.** Frequency goes with the square root of stiffness, so a lasting 1 % drop in frequency is a 2 % loss of bending stiffness [A4].
- **Temperature.** The change of the steel modulus alone moves the frequency by 0.015 % per kelvin, 1.05 % over the -20 to +50 °C range of the requirements [A5]. That is as large as the target, so compensation is needed even before bearings, deck and surfacing, whose effects cannot be computed on paper.
- **People on the deck.** The example bridge is light, so the people on it change its frequency. One walker at midspan lowers f₁ by 6.3 %, and by 3.3 % averaged over a crossing; a crowd of one person per square meter lowers it by 22.7 % [A6]. On a road bridge with 20 t of modal mass one walker moves it by only 0.19 % [A7]. Mass loading is therefore a footbridge problem first.

## B. Excitation, noise and frequency precision (R1, R2)

- **Footfall.** Each heel strike rings the 23.9 Hz mode up to about 57 mg, decaying with a 0.66 s time constant; while someone walks near midspan the response is about 29 mg RMS. A crossing takes 4.9 s [B1].
- **Resolution and noise.** The 600 s record gives 17 averaged segments with a bin width of 0.0153 Hz [B2]. Sensor noise is 2.8 µg in one bin and 177 µg RMS over the whole band [B3]. The mode's half-power bandwidth is 0.48 Hz, 31 bins wide, so the bin width is not what limits precision; a peak 10 dB above the noise needs about 62 µg RMS of modal response [B4].
- **Simulation.** The script simulates 60 hourly records at each of five levels of random modal response, adds the accelerometer's noise, and estimates the frequency two ways: by picking the highest bin and interpolating, as the TRL 2 concept proposed, and by fitting a single-degree-of-freedom spectrum to the 3 Hz around the peak.

*Table 2. Scatter of the hourly frequency estimate from sensor noise alone, 1σ [B5].*

| Modal response (RMS) | Peak found | Peak picking | SDOF curve fit |
| --- | --- | --- | --- |
| 10 µg | 20 % of records | 0.807 % | 0.488 % |
| 30 µg | 100 % | 0.359 % | 0.103 % |
| 100 µg | 100 % | 0.265 % | 0.053 % |
| 300 µg | 100 % | 0.264 % | 0.040 % |
| 1,000 µg | 100 % | 0.220 % | 0.032 % |

- **Change of method.** Peak picking never reaches the 0.2 % of R2, however strong the signal, because the averaged spectrum is still noisy across the 31 bins of the peak. The curve fit reaches 0.2 % from 30 µg RMS [B6] and approaches the theoretical floor for a randomly excited mode, √(ζ / 2πfT) = 0.033 % [B6a]. The reduce step in BRP-PRC-001 now uses the curve fit.
- **Mass loading.** Because each crossing both excites the mode and loads it, the hourly estimate is weighted toward the moments when someone is near midspan: an energy-weighted crossing lowers it by 5.3 %, and the spread of walker masses (50 to 100 kg) adds 1.01 % of scatter per crossing [B7]. The scatter falls with traffic, to 0.45 % at 5 crossings an hour and 0.23 % at 20 [B8]. R2 would need about 26 single crossings every hour, and fails outright when two people cross together, which biases that hour by 10.5 % [B9].
- **R2 is not met** on the example footbridge. Ways to meet it are set out in `docs/REVIEW.md` as proposals: gating out segments with a person on the span (from the acceleration envelope or the strain step), fitting frequency against a load indicator, or restricting the 0.2 % target to bridges whose modal mass is large compared with a walker. R1 is met by design on the datasheet.

## C. Change detection statistics (R3)

- **Test.** One false flag per year from a daily test needs a one-sided threshold of z = 2.78, and 90 % detection adds z = 1.28 [C1].
- **What the temperature and load model must achieve.** Comparing a moving mean of daily frequencies with the baseline, the daily residual left after compensation must be no larger than the values in Table 3 [C2].

*Table 3. Largest daily residual (1σ) that still detects a 1 % shift [C2].*

| Window after the shift | 4-week baseline | 1-year baseline |
| --- | --- | --- |
| 7 days | 0.58 % | 0.65 % |
| 14 days (R3) | 0.75 % | 0.90 % |

- **Budget.** A 0.5 K temperature reading error costs only 0.0075 % [C3]. Random walker scatter averages down to 0.09 % over a day at 5 crossings an hour, but a systematic change in traffic does not: a 10 % change in the share of hours with two people on the span shifts the daily mean by 0.53 % [C3], most of the 0.75 % allowance. The statistics also assume independent days, which is optimistic.
- **R3 cannot be verified at TRL 3.** It is achievable if temperature and load together can be modeled to a daily residual of 0.75 % or less. Whether they can is a question for field data or for public benchmark data such as the Z24 record; no such data were analyzed in this session.

## D. Strain (R4)

- **Sensitivity.** A half-bridge with one active and one dummy gauge gives 1.65 µV per µε at 3.3 V [D1].
- **Resolution and range.** At the assumed ADC noise, one sample resolves 0.09 µε RMS, 0.60 µε peak to peak, well inside the 2 µε target; ±1,000 µε is ±1.65 mV, 6 % of the ±25.8 mV full scale at gain 128 [D2], so gain can come down if a bridge strains more.
- **What there is to see.** A 5 kN/m² crowd gives 19.2 kN·m per girder, 22.3 MPa, 106 µε; one walker at midspan gives 3.2 µε [D3]. The TRL 2 figures (about 100 µε and 3 µε) stand. The strain channel is therefore a good load indicator for the gating proposed in section B, but only just for one person.
- **Aliasing.** Dynamic strain in the 23.9 Hz mode is 1.08 µε at the heel-strike peak; sampled at 20 SPS it would alias to 3.9 Hz but stays below the resolution [D4].
- **Drift.** A 1 µε/K mismatch between gauge and dummy with 2 K between flange and coupon gives 2 µε of apparent strain [D5], and each gauge dissipates 7.8 mW, so a 20 s warm-up now precedes each record [D6]. Long-term drift of a coated foil gauge outdoors cannot be estimated on paper. **R4 is not verifiable at TRL 3** for drift; resolution and range are met on paper.

## E. Temperature (R5)

- The DS18B20 class probe is specified at ±0.5 °C from -10 to +85 °C on the maker's page, with no accuracy stated from -20 to -10 °C [E1]. The effect of that error on the frequency compensation is negligible [E2]. **R5 is at risk** below -10 °C; CalRig's chamber does not reach that range (CLR-CAL-001), so an ice-point check and a second reference would be needed.

## F. Power (R6)

*Table 4. Loads while recording [F1].*

| Load | mW at 3.3 V |
| --- | --- |
| Microcontroller at reduced clock | 33.0 |
| Accelerometer | 0.7 |
| 24-bit ADC | 1.4 |
| Gauge excitation, two 700 Ω half-bridges | 31.1 |
| Bridge completion resistors | 1.1 |
| microSD writes (average) | 10.0 |
| RS-485 transceiver | 1.7 |
| **Total** | **79.0** |

- **Recording.** 79.0 mW at 3.3 V is 92.9 mW at the FieldNode port through the 85 % buck [F2]. The TRL 2 figure of 84 mW did not count the converter or the RS-485 link.
- **Average.** Each hour the hub records for 620 s (with the warm-up) and processes for 60 s; then FieldNode switches the rail off, so the hub has no sleep current. The average is **16.9 mW** at the port, 18.8 mW from the FieldNode cell, 0.41 Wh a day [F3]. The TRL 2 figure of about 15 mW stands within its precision. Continuous recording would need 93 mW, and the hourly windows use 17 % of FieldNode's 100 mW sensor allowance [F4]. **R6 is met on paper.**
- **Processing.** The FFTs take about 29 Mflop, about 29 s at an assumed 1 Mflop/s in software floating point, plus about 6 s to read the record back from the card; working one axis at a time from the card needs 224 kB of the RP2040's 264 kB of RAM [F5]. Computing all three axes live would not fit, which is why the hub post-processes from the card.

## G. Data, storage and uplink (R7)

- **Raw data.** 1.90 MB per hour, 46 MB per day, 1.39 GB per month; a 32 GB card holds 22 months [G1], writing 16.7 GB (0.52 full-card writes) a year [G2]. An industrial card is specified for temperature, not wear.
- **Summary.** The hourly summary is 36 bytes [G3], unchanged from TRL 2.
- **Airtime.** At 49 bytes on air an uplink takes 98 ms at SF7, 329 ms at SF9, 575 ms at SF10 and 2,302 ms at SF12; 24 a day use 13.8 s at SF10 and 55.2 s at SF12, over the 30 s a day that FieldNode's R9 allows on The Things Network [G4].
- **Regional limits.** The summary fits every EU868 data rate (51 bytes at SF10 to SF12) but not US915 DR0 or AS923 DR2 with dwell time (11 bytes); both allow 53 bytes one step faster, at SF9 [G5]. A reduced 11-byte summary for those rates is proposed [G6]. **R7 is at risk** until the region is chosen (FND-DDR-001, O1). On-site storage is met.

## H. Mounting, mass and clearance (R8, R9)

- **Mass.** The hub weighs 0.87 kg, the plate 1.35 kg and the jack, tab and clamps 1.12 kg: 3.34 kg on the girder [H1]. The TRL 2 figure of 0.6 kg for hub and clamps was far too low. The FieldNode core weighs 2.41 kg by its own calculation, not the 1.7 kg quoted at TRL 2.
- **Stiffness of the mount.** The accelerometer must move with the girder up to 60 Hz, so the hub's own mounting resonance should be above about 120 Hz. The new plate, 200 × 313 × 8 mm aluminium, stands on the bottom flange and is wedged against the top flange by an M12 jack screw; with the hub 177 mm above its foot it resonates out of plane between 126 Hz (ends pinned) and 253 Hz (ends fixed) [H2]. The TRL 2 arrangement, a plate clamped only to the bottom flange with the hub 190 mm up, would resonate at about 77 Hz [H3], close enough to the band to distort it. This is the main design change of this note.
- **Retention.** The clamp jaws hook under the flange tip and the jack screw bears on the top flange; the lanyard is a second path [H4]. Aluminium on painted steel needs isolating washers; the plate is hard anodized.
- **Clearance (R9).** Below the soffit there are only the clamp jaws (8 mm), the gauge covers (6 mm) and the cables that wrap the south flange (10 mm), against the 15 mm limit [H5]. The hub sits 9 mm inside the flange tip line, inside the girder outline [H6]. **R9 is met on paper.**
- **FieldNode on the post.** A 35 m/s gust puts 52.2 N on the panel and 29 N on the enclosure, a 60 N·m moment and 7.2 MPa in a 50 × 3 mm post, about a twentieth of what a 1 kN load at the rail top would cause [H7]. FieldNode's V-blocks are designed for round poles; the square post's 70.7 mm diagonal is at the 71 mm upper fit [H8]. This interface needs FieldNode's review; nothing in FieldNode is changed here.

## I. Installation time (R8)

Nine tasks take 320 person-minutes. The critical path is the gauge work by one fitter: access and briefing, paint removal at two sites, bonding, wiring and coating, then testing and clean up, 170 min or 2.8 h, while the second fitter fits the plate, hub, FieldNode and cables in 90 min [I1]. This assumes a lead test on an earlier visit and a fast-curing coating. **R8 cannot be verified at TRL 3** for time, which needs a trial fit; the no-drilling part is met by design.

## J. Outdoor life (R10)

The hub (IP67) hangs in shade under the deck, and its parts are rated for the range except at the edges: the RP2040 class controller is assumed to be rated -20 to +85 °C and the industrial card -25 to +85 °C. The weak points are elsewhere: FieldNode's interior reaches 58.7 to 73.3 °C on a 45 °C day without a shield, which FND-CAL-001 reports as not met, and the life of the gauge coating is unknown [J1]. **R10 is at risk.**

## K. Cost (R12)

The BOM has nine lines, all priced. Under R12 as redefined in BRP-DDR-001 (D1), the BridgePulse-specific parts cost $244.00 against the $250 budget, a margin of $6.00 (2.4 %). The FieldNode core adds $126.00, costed in its own repo, for a complete monitor of $370.00, which is $120.00 over $250 [K1]. The TRL 3 changes added a separate industrial microSD card ($20), the RS-485 and buck converter modules and the jack-screw plate. **R12 is at risk** because the prices are indicative and the margin is thin.

## L. Results against every requirement

*Table 5. Requirement status from this note [L].*

| ID | Requirement | Value | Target | Status |
| --- | --- | --- | --- | --- |
| R2 | Track natural frequencies | Bin 0.0153 Hz; sensor-noise scatter 0.053 % at 100 µg (curve fit); walker-mass scatter 0.45 % at 5 crossings per hour | Bin 0.02 Hz; 0.2 % (1σ) over a steady day | **Not met** on the example footbridge |
| R5 | Measure temperature | ±0.5 °C from -10 to +50 °C; not specified below -10 °C | ±0.5 °C over -20 to +50 °C | At risk |
| R7 | Send and keep the data | 36 bytes hourly; 22 months on 32 GB; fits EU868 at every rate, US915 and AS923 only at SF9 or faster | 48 bytes within regional limits; 12 months on site | At risk |
| R10 | Survive outdoors | Hub in shade; FieldNode heat not met in its own repo; coating life unknown | IP67 and IP65; -20 to +50 °C; 5 years | At risk |
| R12 | Affordable | $244.00 BridgePulse-specific; $370.00 complete | $250 BridgePulse-specific parts | At risk (2.4 % margin) |
| R3 | Flag structural change | Achievable if the daily residual after compensation is 0.75 % or less | 1 % within 14 days; one false flag per year | Not verifiable at TRL 3 |
| R4 | Measure strain | 0.09 µε RMS; ±1,000 µε uses 6 % of full scale; drift unknown | 2 µε; ±1,000 µε; 5 µε per month | Not verifiable at TRL 3 (drift); resolution and range met on paper |
| R8 | Fit without harming the structure | No drilling or welding; 2.8 h estimate | No drilling; 4 h for two people | Not verifiable at TRL 3 (time); fixing met by design |
| R6 | Stay within the FieldNode energy budget | 16.9 mW average at the port | 30 mW | Met on paper |
| R9 | Keep clear of what passes under and over | 10 mm below the soffit; hub inside the girder outline | 15 mm | Met on paper |
| R1 | Measure bridge acceleration | 22.5 µg/√Hz, 3 axes, 250 Hz output, 62.5 Hz filter corner | 25 µg/√Hz; 0.5 to 60 Hz | Met by design (datasheet) |
| R11 | Protect privacy | No camera or microphone | Structural readings only | Met by design |
| R13 | Present results responsibly | Wording rule in the precis; not yet implemented | No safety rating anywhere | Met by design |

Counts: 1 not met, 4 at risk, 3 not verifiable at TRL 3, 2 met on paper, 3 met by design.

## Checks against the TRL 2 figures

*Table 6. TRL 2 claims (BRP-PRC-001 v0.2) against this note.*

| TRL 2 claim | This note | Action |
| --- | --- | --- |
| First mode about 24 Hz; second about 97 Hz; EI about 6.8 × 10⁷ N·m²; about 172 kg/m | 23.9 Hz; 96 Hz; 6.52 × 10⁷ N·m² from the model's rectangles; 167 kg/m | Precis updated |
| Bin width about 0.015 Hz; about 17 segments; 2.8 µg in one bin; about 180 µg over the band | 0.0153 Hz; 17; 2.8 µg; 177 µg | Stands |
| Random error of one hourly estimate about 0.01 % at 24 Hz with peak interpolation | 0.22 to 0.27 % by peak picking; 0.03 to 0.05 % by curve fit | Method changed to a curve fit; precis updated |
| Frequency not affected by people (not considered) | One walker lowers f₁ by up to 6.3 % | R2 not met; precis updated; proposals in `docs/REVIEW.md` |
| 1.65 µV per µε; crowd about 100 µε; one pedestrian about 3 µε | 1.65 µV per µε; 106 µε; 3.2 µε | Stands |
| About 84 mW recording, about 15 mW average, 0.36 Wh per day | 92.9 mW at the port; 16.9 mW; 0.41 Wh | Precis updated |
| 1.9 MB per hour; 46 MB per day; 1.4 GB per month; about 23 months on 32 GB | 1.90 MB; 46 MB; 1.39 GB; 22 months | Precis updated |
| About 36 bytes per uplink; regional limits not checked | 36 bytes; does not fit US915 DR0 or AS923 DR2 | Reduced payload proposed |
| Hub and clamps about 0.6 kg; FieldNode about 1.7 kg | 3.34 kg on the girder; FieldNode 2.41 kg | Precis updated |
| Hub about 12 mm below the soffit | 10 mm (clamp jaw 8 mm) | Stands |
| About $342 complete; $216 BridgePulse-specific | $370.00 complete; $244.00 BridgePulse-specific | BOM notes and precis updated |
