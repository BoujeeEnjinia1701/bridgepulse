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
