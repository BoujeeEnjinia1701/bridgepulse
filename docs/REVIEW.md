# Review note: BridgePulse

## Session 2026-09-25: /populate to a strong TRL 2

### What was done

- `docs/01-problem.md` (BRP-PRB-001 v0.2): problem with cited figures (FHWA, 23 CFR 650.311, RAC Foundation, MLIT, NTSB), users, target structures, operating environment, constraints, prior work (Z24 study, ADXL355, Brooks and Donovan), out of scope, open questions; co-design checklist kept.
- `docs/02-concept.md` (BRP-PRC-001 v0.2): how it works, numbered components, example bridge frequency, measurement resolution, strain, power, data, cost, eight proposed design choices, safety section, open questions.
- `docs/03-requirements.md` (BRP-REQ-001 v0.2): 13 measurable requirements (R1 to R13) with targets, verification method and status at TRL 2.
- `cad/src/concept_media.py`: massing model of a 7 m steel footbridge (context, grey) with the monitor at midspan, eight BOM-numbered parts, a 1.75 m person standing on the deck, and a separate cutaway of the sensor hub. `scale_figure=False` with the person as a context part, because the kit's automatic figure would stand at the girder soffit and clip through the bridge.
- `media/`: `hero.png`, `concept-blueprint` (PNG, PDF, SVG), `exploded.png` with callouts 1 to 8, `cutaway.png` (sensor hub), `flow.png` (hourly data flow, estimates), `model.glb` and `viewer.html`. All images were checked by eye; temporary `media/_views*` folders are removed by the script.
- `bom/bom.csv`: eight lines numbered to match the exploded view, indicative USD prices; `bom/bom-notes.md` updated with totals.
- `README.md`: hero image and links line, expanded Concept rationale, Burning platform, Where it could be used (6 industries, 5 regions), What sparked the idea; Problem, Concept, Key components and Safety brought in line with the concept.
- `docs/pdf/`: branded PDFs of the three controlled documents.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| First vertical mode, 7 m example footbridge | about 24 Hz | Inside R2 band |
| Spectral bin width per hourly record | about 0.015 Hz | R2 met by design |
| Accelerometer noise in one bin | about 2.8 µg | R1 met on datasheet |
| Strain from a crowd on the example bridge | about 100 µε; one pedestrian about 3 µε | R4 resolution 2 µε |
| Average power draw | about 15 mW (about 84 mW while recording) | R6 met on estimate |
| Uplink per hour | about 36 bytes | R7 met on estimate |
| Raw data on site | about 1.4 GB per month; about 23 months on 32 GB | R7 met on estimate |
| Parts cost, complete | about $342 ($216 BridgePulse-specific, $126 FieldNode core) | **R12 not met** |

Requirements not met or at risk:

- **R12 (cost) not met:** about $342 against the $250 budget, 37 % over.
- **R3 (1 % change detection) not demonstrated:** it depends on quiet bridges giving a usable ambient signal and on a temperature model that holds across seasons.
- **R2 repeatability, R4 drift, R5 accuracy and R10 durability not verified:** they rest on datasheets and estimates.
- **R7 regional payload limits not checked** for each LoRaWAN region.

### Proposed, awaiting Amish

1. **Budget (R12).** Options: (a) keep $250 and redefine R12 as "BridgePulse-specific parts $250 or less", treating the FieldNode core as a shared component costed in its own repo; (b) raise `budget_usd` to $350; (c) cut cost with a cheaper accelerometer, which would likely fail R1. Recommendation: (a), with the complete system cost always stated beside it. `project.yaml` is unchanged.
2. **Ambient vibration only**, no shaker or impact hammer. Recommendation: yes for TRL 3; revisit if quiet footbridges give no clear peaks.
3. **Hourly 10 minute windows** rather than continuous recording (about 15 mW against about 84 mW). Recommendation: windows.
4. **Separate sensor hub on the girder, FieldNode on a handrail post.** Recommendation: yes.
5. **Foil gauge half-bridges with dummy gauges** rather than weldable or vibrating-wire gauges. Recommendation: foil for cost, with drift checked early.
6. **One accelerometer at midspan**, with a second at quarter span as a later option. Recommendation: one.
7. **Microcontroller class for the hub** (RP2040 class proposed; alternatives are an STM32 with a floating-point unit or doing only raw capture in the hub). Recommendation: RP2040 class for cost and tooling.
8. **FieldNode sensor port pinout and protocol** to be agreed with the FieldNode project; nothing in FieldNode is changed here.
9. **Alert policy and public view.** Flags only to the owner's engineer; CityTwin shows monitoring status only. Recommendation: yes.
10. **First host bridge and partner** for co-design (a town, park service or university footbridge).

`project.yaml` pitch and problem were left unchanged; the figures found support them.

### Safety concerns

- False reassurance: owners might defer inspections because a monitor shows "no change". All outputs must say the data supports inspection and is never a safety rating (R13).
- Work at height, over water and near traffic during installation.
- Lead or other hazardous paint on older steel bridges when preparing strain gauge areas; gauge adhesives and coatings are chemicals.
- Falling parts: clamps loosening onto people, vehicles or boats below; secondary lanyards are specified.
- Tampering with the post-mounted FieldNode; the LiFePO4 cell inside it.

### Problems and notes

- The legacy `cad/src/model.py` placeholder is untouched (TRL 3 work).
- The strain gauge callout (5) in the exploded view sits between the two gauge patches because both girders' gauges are one BOM line.
- No named open-source bridge monitor was found in the time available; the prior-work review should be extended at TRL 3.
- WebSearch was unavailable this session; every cited figure was checked by fetching the source page directly. A Morbi (India) footbridge figure and a German bridge figure were left out because their primary sources could not be fetched.

### Recommended next step

Review this note and the media, then decide items 1 and 8 in particular. If approved, run `/advance-trl3` to check the frequency, noise, strain and power estimates by calculation (including a test of the detection method on published Z24 data), and produce the parametric model and drawing sheet.

## Session 2026-09-25: TRL 3

On 2026-09-25 Amish asked for this batch of repos to go through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's TRL 2 items one by one, so every item that carried a recommendation is adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review. This session ran `/advance-trl3` on that basis and stopped at TRL 3.

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (BRP-DDR-001 v0.1, status proposed): eleven items adopted as recommended for TRL 3, open for Amish's review (D1 to D11), and three left open (O1 to O3).
- `docs/04-calcs/01-sizing.md` (BRP-CAL-001 v0.1) and `docs/04-calcs/sizing.py`: bridge dynamics and mass loading, excitation and a Monte Carlo simulation of the hourly frequency estimate, change detection statistics, strain, temperature, power, data and LoRaWAN airtime, mounting stiffness, mass and clearance, installation time, outdoor life and cost, with a status for every requirement. The script imports the model, reads the BOM and `project.yaml`, and prints every number the note quotes (fixed random seed).
- `cad/src/model.py`: parametric build123d model (hub enclosure with glands, accelerometer and signal boards, jacked mounting plate with tab, jack screw and two flange-tip clamps, gauge covers and dummy coupons, temperature probes, cable runs, FieldNode core massing on the midspan post; the example bridge as context). Exports `cad/step/` and `cad/stl/` for `bridgepulse-assembly`, `sensor-hub` and `bridgepulse-installed`.
- `cad/src/sheets.py` and `cad/drawings/BRP-DWG-001.svg`, `.pdf`, `.png`: general arrangement at Rev P1 (front and right views at 1:20, detail A of the hub at 1:4, isometric), marked "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". BRP-DWG-001 was free because the concept blueprint is BRP-DWG-010. The deck and handrails are left off the views for clarity.
- `bom/bom.csv` (nine lines, all priced with a supplier or supplier type) and `bom/bom-notes.md`: $244.00 BridgePulse-specific, $370.00 complete.
- `cad/src/concept_media.py` now builds from the model; all of `media/` was re-rendered and every image checked; no `_views` folders remain.
- BRP-PRB-001, BRP-PRC-001 and BRP-REQ-001 revised to v0.3; `README.md` (badge, TRL line, links, Concept paragraph, key components) and `project.yaml` (`trl: 3`, `trl_target: 3`, evidence list) updated. The required README sections are unchanged in name and order; none of their figures changed. PDFs rebuilt in `docs/pdf/`.

### Requirement status (BRP-CAL-001, Table 5)

1 not met, 4 at risk, 3 not verifiable at TRL 3, 2 met on paper, 3 met by design.

| ID | Status | Key number |
| --- | --- | --- |
| R2 Track frequencies | **Not met** | Sensor-noise scatter 0.053 % an hour at 100 µg (curve fit), but one 75 kg walker lowers f₁ by up to 6.3 % and walker mass adds 0.45 % scatter at 5 crossings an hour; 0.2 % would need about 26 single crossings an hour |
| R5 Temperature | At risk | ±0.5 °C only from -10 °C upward |
| R7 Data | At risk | 36 bytes fits EU868, not US915 DR0 or AS923 DR2 (11 bytes) |
| R10 Outdoor life | At risk | FieldNode heat not met in its own repo; coating life unknown |
| R12 Cost | At risk | $244.00 against $250 (2.4 % margin); $370.00 complete |
| R3 Change detection | Not verifiable at TRL 3 | Needs a daily residual of 0.75 % or less after temperature and load compensation |
| R4 Strain | Not verifiable at TRL 3 (drift) | 0.09 µε RMS resolution; range met |
| R8 Fitting | Not verifiable at TRL 3 (time) | 2.8 h estimate; no drilling met by design |
| R6, R9 | Met on paper | 16.9 mW average; 10 mm below the soffit |
| R1, R11, R13 | Met by design | |

Key numbers: first mode 23.9 Hz (modal mass 535 kg); 92.9 mW while recording; 1.39 GB of raw data a month, 22 months on 32 GB; 3.34 kg on the girder; mounting resonance 126 to 253 Hz.

Design changes made by the calculations, within the adopted choices: the mounting plate stands on the bottom flange and is jacked against the top flange (the TRL 2 plate held at the bottom flange only would resonate at about 77 Hz, near the band); the hub runs from FieldNode's switched 5 V rail and is off between records; it post-processes each record from the card because three axes do not fit in the RP2040's RAM; the frequency is estimated by a curve fit, because peak picking never reaches 0.2 %. TRL 2 numbers corrected: EI 6.52 × 10⁷ N·m² (was 6.8), 167 kg/m (was 172), recording 92.9 mW (was 84), average 16.9 mW (was 15), 22 months on the card (was 23), hub and mount 3.34 kg (was 0.6), FieldNode 2.41 kg (was 1.7), cost $244 and $370 (was $216 and $342).

### Decisions recorded (BRP-DDR-001)

Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review: D1 keep `budget_usd` at $250 and redefine R12 as BridgePulse-specific parts, complete cost stated beside it (applied to R12; no new budget figure was recommended, so `budget_usd` is unchanged); D2 ambient vibration only; D3 hourly 10 minute windows; D4 hub on the girder, FieldNode on a post; D5 foil half-bridges with dummies; D6 one accelerometer at midspan; D7 RP2040 class controller; D8 engineer-only alerts, status-only public view; D9 temperature-compensated trend with a four-week minimum baseline; D10 built on FieldNode, TwinKit and CityTwin; D11 no change to pitch or problem (none was recommended).

### Still awaiting Amish

1. **O1, FieldNode port pinout and protocol.** No recommendation; this repo assumes FieldNode's candidate pinout with RS-485 and a 5 V rail, as a working assumption only.
2. **O2, first host bridge and co-design partner.** No preference stated.
3. **O3, data ownership and what is published** beyond monitoring status. No recommendation.
4. **New, R2 and people's mass.** Options: (a) gate out record segments while someone is on the span, using the acceleration envelope or the strain channel, and estimate frequency from the rest; (b) regress each hourly frequency on a load indicator (strain mean, RMS acceleration) in TwinKit; (c) keep R2 at 0.2 % only for bridges whose modal mass is at least 20 times a walker's mass, and state a looser target (for example 1 % hourly, with daily averaging) for light footbridges. Recommendation: (a) and (b) together, checked on recorded data before any change to R2; R2 is unchanged here.
5. **New, reduced payload (R7).** An 11-byte summary at US915 DR0 and AS923 DR2 with dwell time. Recommendation: adopt once the region is known (FND-DDR-001, O1). Not applied.
6. **New, cold-range temperature check (R5).** Options: accept ±0.5 °C only above -10 °C, add an ice-point and a second reference check, or use a probe specified to -20 °C. Recommendation: ice-point check plus a probe specified over the full range if one fits the $6 margin. Not applied.
7. **New, cost margin (R12).** $6.00 is thin for indicative prices. If quotes come in higher, the first savings would be a consumer high-endurance card and a cheaper accelerometer breakout that still meets R1. No change proposed now.

Suggestions only, not in the repo: analyze the public Z24 record, or another open bridge data set, to test the temperature model against the 0.75 % daily residual; extend the prior-work review of open bridge monitors.

### Cross-repo consistency

- FieldNode (read its REVIEW.md and CAL-001; not edited): the $126.00 core cost, 2.41 kg mass, 52.2 N panel wind load, two M12 5-pin ports with one switched rail each and the 100 mW design allowance are used as FieldNode states them. BridgePulse uses 16.9 mW, 17 % of that allowance. Two points for FieldNode's review: (1) FieldNode's pole kit is designed for round poles; BridgePulse mounts it on a 50 mm square handrail post, whose 70.7 mm diagonal is at the 71 mm upper fit, so the V-block seating on a square post needs checking; (2) the port pinout is open on both sides. FieldNode's default 15 min, 20-byte schedule is replaced here by an hourly 36-byte uplink, which its D6 allows.
- TwinKit: hosts the baseline and flags as TwinKit's REVIEW.md describes; no conflict. The load regression proposed in item 4 would run there.
- CalRig: its chamber reaches about 9 to 13 °C at its coldest (CLR-CAL-001), so it cannot check the probes below -10 °C (item 6).

### Safety concerns

- False reassurance: a "no change" trend on a light footbridge could hide a real change behind traffic effects (R2). Outputs must stay framed as inspection support, never a safety rating (R13).
- Work at height, over water and near traffic during installation; the jacked plate adds a preload that must be set and checked, and the clamps and lanyard keep it from falling if the preload is lost.
- Lead or other hazardous paint when preparing gauge areas; adhesives and coatings are chemicals.
- Aluminium plate on steel: galvanic corrosion could loosen it over years unless isolated.
- FieldNode on the post: tampering, its LiFePO4 cell, and heat in hot sun as FieldNode's own calculation reports.

### Gaps and notes

- Citations: the TRL 2 note listed no unchecked citations. WebFetch confirmed the DS18B20 accuracy range (maker's page) and the RP2040's 264 kB of RAM (Raspberry Pi documentation). It did not confirm the LoRaWAN regional payload limits (the pages fetched did not state them) or an ADS1220 noise figure (the product page gives none) or the RP2040 temperature range; these are stated as assumptions in BRP-CAL-001, Table 1, and remain flagged here. WebSearch was not used (quota exhausted). No figure left out at TRL 2 was added to the README.
- Assumptions only data or tests can settle: damping (1 %), heel-strike impulse (2 N·s), ADC noise, gauge-to-dummy mismatch, jack preload, and the size of temperature and load effects on real bridges.
- The kit's cutaway cuts at the mean Y of all parts and would miss the hub, so `concept_media.py` keeps its own hub cutaway (`cut=False` in `render_all`), as at TRL 2. In the exploded view the accelerometer board (item 2) is small and mostly under its callout, and callout 5 floats between the two gauge patches because both are one BOM line.
- Existing material beyond TRL 3: `build-log/README.md` (scaffold) is present, untouched and not extended. `electronics/` and `firmware/` are empty. No test, build or firmware material exists.

### Recommended next step

TRL 4 is on hold by Amish's instruction; this repo stops at TRL 3. Amish's review is needed on BRP-DDR-001 (D1 to D11), on O1 to O3 and on new items 4 to 7 above, item 4 first because it decides whether the method suits light footbridges. For the record only, TRL 4 would need: a bench build of the hub on a girder specimen; a lab test report (TST, `environment: lab`) covering accelerometer noise and the mounting resonance of the jacked plate, frequency estimates from recorded footfall with people of known mass, gauge drift and thermal mismatch, probe accuracy including below -10 °C, and hub energy per record through a FieldNode port; and build log entries. None of this has been started.
