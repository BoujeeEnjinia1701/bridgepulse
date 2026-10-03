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

Update 2026-09-25: items 1 to 7 and 9 are now **Decided by Amish, 2026-09-25: go with recommendation** (BRP-DDR-001 D1 to D8, BRP-DDR-002). Items 8 and 10 had no recommendation and remain "Proposed, awaiting Amish".

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

Decided by Amish, 2026-09-25: go with recommendation (recorded at this session as adopted for TRL 3, open for his review; see BRP-DDR-002): D1 keep `budget_usd` at $250 and redefine R12 as BridgePulse-specific parts, complete cost stated beside it (applied to R12; no new budget figure was recommended, so `budget_usd` is unchanged); D2 ambient vibration only; D3 hourly 10 minute windows; D4 hub on the girder, FieldNode on a post; D5 foil half-bridges with dummies; D6 one accelerometer at midspan; D7 RP2040 class controller; D8 engineer-only alerts, status-only public view; D9 temperature-compensated trend with a four-week minimum baseline; D10 built on FieldNode, TwinKit and CityTwin; D11 no change to pitch or problem (none was recommended).

### Still awaiting Amish

1. **O1, FieldNode port pinout and protocol.** No recommendation; this repo assumes FieldNode's candidate pinout with RS-485 and a 5 V rail, as a working assumption only.
2. **O2, first host bridge and co-design partner.** No preference stated.
3. **O3, data ownership and what is published** beyond monitoring status. No recommendation.
Update 2026-09-25: items 4 to 7 are now **Decided by Amish, 2026-09-25: go with recommendation** (BRP-DDR-002, D12 to D15). O1 to O3 remain "Proposed, awaiting Amish".

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

## Session 2026-09-25: recommendations accepted

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Every item with a recommendation is now **Decided by Amish, 2026-09-25: go with recommendation**, recorded in `docs/decisions/0002-recommendations-accepted.md` (BRP-DDR-002 v0.1). BRP-DDR-001 is revised to v0.2 with D1 to D11 marked decided.

### Decisions applied and what changed

| Decision | Change | Before | After |
| --- | --- | --- | --- |
| D1 to D11 (BRP-DDR-001) | Status wording only; `budget_usd` stays at $250 for the BridgePulse-specific parts, pitch and problem unchanged | Adopted for TRL 3, open for review | Decided |
| D12, R2 and people's mass | Load gating in the hub (gate from the strain step, 0.25 s pad, 10 dB and damping acceptance rule) plus a load regression in TwinKit; simulated in BRP-CAL-001 v0.2, B10 to B12 | Scatter 0.45 % at 5 crossings (simple count; 1.5 to 3.1 % in the new time-varying simulation); R2 not met | 0.015 % or less gated (1 to 20 crossings per record; 80 % of records accepted with one crossing); R2 at risk, target unchanged |
| D13, reduced payload | 11-byte summary where the data rate allows 11 bytes; R7 restated | 36 bytes only; R7 at risk | 36 or 11 bytes (371 ms at SF10); R7 met on paper (AS923 limit assumed) |
| D14, cold-range temperature | TMP1826 class probe in a stainless sheath plus an ice-point check | DS18B20 class, ±0.5 °C from −10 °C; $4.00 each; R5 at risk | ±0.3 °C from −40 to +105 °C; $6.00 each; R5 met on paper |
| D15, cost margin | No change; contingency savings recorded | $244.00 specific, $6.00 margin; $370.00 complete | $248.00 specific, $2.00 margin (0.8 %); $374.00 complete |

Files changed: BRP-PRB-001 v0.4, BRP-PRC-001 v0.4, BRP-REQ-001 v0.4, BRP-CAL-001 v0.2 with `docs/04-calcs/sizing.py`, BRP-DDR-001 v0.2, new BRP-DDR-002 v0.1, `bom/bom.csv` (item 6), `bom/bom-notes.md`, `cad/src/sheets.py` and BRP-DWG-001 at Rev P2 (probe note added; notes box moved up so the last line clears the title block), `cad/src/concept_media.py` (key figures), `README.md`, `project.yaml` (evidence list only). `cad/src/model.py` geometry is unchanged; STEP and STL were re-exported. All media and PDFs were regenerated with the designmolecule.com footer.

The CAL note also corrects a v0.1 wording error: the walker-mass scatter in B8 counts crossings inside the 10 minute record, not crossings an hour.

README: "What sparked the idea" rewritten around the 1967 Silver Bridge collapse and the National Bridge Inspection Standards of 1971 (FHWA source); the reference to a September 2026 review of the lab's research areas was removed. BRP-PRB-001 did not attribute the idea to a review.

### Requirement status (BRP-CAL-001 v0.2, Table 5)

0 not met, 3 at risk, 3 not verifiable at TRL 3, 4 met on paper, 3 met by design (was 1, 4, 3, 2, 3).

| ID | Status | Key number |
| --- | --- | --- |
| R2 Track frequencies | At risk | 0.015 % or less with load gating in simulation; to be checked on recorded data |
| R10 Outdoor life | At risk | FieldNode heat not met in its own repo; coating life unknown |
| R12 Cost | At risk | $248.00 against $250 (0.8 % margin); $374.00 complete |
| R3 Change detection | Not verifiable at TRL 3 | Needs a daily residual of 0.75 % or less; the traffic term falls to 0.010 % with gating |
| R4 Strain | Not verifiable at TRL 3 (drift) | 0.09 µε RMS; range met |
| R8 Fitting | Not verifiable at TRL 3 (time) | 2.8 h estimate |
| R5, R6, R7, R9 | Met on paper | ±0.3 °C; 16.9 mW; 36 or 11 bytes; 10 mm below the soffit |
| R1, R11, R13 | Met by design | |

### Still awaiting Amish

1. **O1, FieldNode port pinout and protocol.** No recommendation.
2. **O2, first host bridge and co-design partner.** No preference stated.
3. **O3, data ownership and what is published.** No recommendation.
4. **O4, LoRaWAN region for the first installation** (FND-DDR-001, O1). No recommendation here; D13 makes R7 independent of it.

### Cross-repo actions

- **TwinKit:** host the load regression of D12 (hourly frequency against strain mean and RMS acceleration) beside the temperature model.
- **FieldNode:** (1) review seating its V-block clamps on a 50 mm square handrail post, whose 70.7 mm diagonal is at the 71 mm upper fit; (2) make the payload limit of the current data rate available to the sensor port so the hub can pick the 11-byte summary (D13); (3) agree the port pinout (O1).
- **CalRig:** its chamber does not reach the cold range, so the ice-point check of D14 is done outside it.

No other repo was edited.

### Verification and gaps

- WebFetch confirmed the TMP1826 accuracy (Texas Instruments product page) and the EU868 and US915 payload limits (The Things Network regional pages). The AS923 dwell-time limit could not be fetched (LoRa Alliance site blocked) and stays an assumption. The ADS1220 noise figure and RP2040 temperature range remain assumptions, as before.
- The gating simulation is optimistic: one mode, an idealized walker, a perfect gate and no wind while people cross. Its gated scatter is below the random-excitation floor because the free decays after each crossing are clean in the model.
- The TMP1826 probe is a made part (sensor potted in a sheath); its $6.00 price is indicative.

### TRL 4

TRL 4 remains on hold by Amish's instruction. The recorded-data check of load gating (D12), the ice-point and CalRig checks of the new probes (D14) and quotes for the BOM (D15) are decided but on hold. No build, test, purchase, PCB or firmware work was started.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26.

### What was added

`cad/src/product_model.py` exposes `product_parts()` (48 parts: 31 shell, 12 internal, 3 accessory, 2 context), `TITLE` and `RENDER_VIEWS` (hero, exploded, and a low detail view that shows the accelerometer board through the lid window). It reuses PARAMS and derived() from `cad/src/model.py`; the hub, board, plate, jack, clamp, gauge, coupon and probe sizes and positions are as model.py. It adds:

- Sensor hub (BOM 1): powder-coated die-cast base and lid with filleted edges, a gasket line at the parting plane, four lid screws, a teal name plate, an IP67 rating label, an accelerometer axis mark on the lid, two M12 cable glands, and the M12 panel connector with its moulded plug and knurled coupling nut (BOM 7).
- Accelerometer board (BOM 2) with its sensor, header and screws; signal board (BOM 3) with the RP2040 class module, ADC and RS-485 modules, microSD socket and card (BOM 9), gauge terminal block, brass standoffs and a lit green status light.
- Mounting plate (BOM 4): hard anodized with a filleted outline, top tab and ID label; M12 jack screw with lock nut and swivel pad; the two flange-tip clamps with jaws, M10 bolts, nuts, washers and screws to the plate foot.
- Strain gauges (BOM 5): active foil gauge under its cover patch below the bottom flange; dummy gauge on its steel coupon, with its own cover, on the flange top.
- Steel temperature probe (BOM 6) as a bonded boss with a lead strain relief.
- Sensor cables (BOM 7) with UV-stable clips, and context (not in the BOM): a 520 mm section of the south girder, IPE 360 class with root fillets, and a strip of the timber deck.

`README.md` now shows `media/render-hero.png` and links `media/render-exploded.png`; the orchestrator produces both files.

### Differences from model.py (Proposed, awaiting Amish)

1. **Clear window in the hub lid.** BOM line 1 is a die-cast aluminium box with a plain lid. The appearance model adds a clear polycarbonate window so the accelerometer and signal boards show. Proposed, awaiting Amish. Recommendation: keep the window as a render aid only and build with the plain die-cast lid, which keeps IP67 simple and the enclosure stiff; option: a gasketed window if a status light must be readable on site.
2. **Parts left out to keep the render compact.** The north girder's gauge and cover, the air temperature probe under the deck, and the FieldNode core with its handrail post (BOM 8) are not shown; they stay in model.py and the concept media. Proposed, awaiting Amish. Recommendation: accept; FieldNode has its own renders in its repo.
3. **Cable routes shortened and moved.** The cables end at the edges of the girder section. The far gauge cable crosses under the flange at x = +100 mm instead of x = -100 mm, so it no longer crosses the near gauge cable in front of the hub, and the FieldNode cable rises past the deck edge at x = -130 mm instead of x = 0 so it does not run across the lid window. Proposed, awaiting Amish. Recommendation: adopt both routes in model.py at the next CAD revision; neither changes an interface.
4. **model.py cable clash (found while routing).** In model.py the far gauge cable passes the inner flange edges at y = ±522 mm, which is 7 mm inside the 515 mm flange edge, so the modelled cable runs through each bottom flange. The appearance model uses y = -508 mm. Proposed, awaiting Amish. Recommendation: change `inner_n` in model.py to `gy - bf / 2 - r - 3` at the next CAD revision; it is a modelling error, not a design change.
5. **Probe sheath size.** model.py draws the steel probe as a 14 mm diameter by 15 mm boss (radius taken as `t_probe[0]` = 7 mm), while BOM line 6 gives a 7 mm by 60 mm sheath. The appearance model keeps the model.py envelope and treats it as a bonded boss holding the sheath. Proposed, awaiting Amish. Recommendation: show the 7 mm sheath and its clip in model.py at the next CAD revision.
6. **The active gauge is not visible in the hero.** It sits under the bottom flange and every view is from above the studio floor; the hero shows the dummy gauge coupon and the gauge cable wrapping the flange tip, and the exploded view shows the active gauge and its cover. No change proposed.

### Status

This is an appearance model only: no tolerances, no fabrication detail, nothing past TRL 3. `trl: 3` and `trl_target: 3` are unchanged, and TRL 4 remains on hold. model.py, the BOM and the other documents were not edited.

## Session 2026-09-27: owner decision applied

Amish's instruction: "resolve the challenges for ConePro, BridgePulse, Grainguard and WellSense." For BridgePulse the decided item is item 4 of the 2026-09-26 session, the far gauge cable clash in `cad/src/model.py`. Decided by Amish on 2026-09-27; recorded in BRP-DDR-003.

### What changed

- `cad/src/model.py`: new function `far_cable_inner()` returns `gy - bf / 2 - cable_r - 3` (508 mm); `build_parts()` uses it for `inner_n` (was `gy - bf / 2 + r + 3`, 522 mm). No other dimension or interface changed.
- `cad/src/product_model.py`: the far gauge cable now takes its inboard offset from `far_cable_inner()` instead of its own formula. The value is the same (y = -508 mm), so the appearance model's geometry is unchanged. Its far cable crossing at x = +100 mm (item 3) is kept, since that item is still open.
- Regenerated: `cad/step/*.step`, `cad/stl/*.stl`, `media/hero.png`, `exploded.png`, `cutaway.png`, `flow.png`, `concept-blueprint.*`, `model.glb`, and `cad/drawings/BRP-DWG-001.*`, now Rev P3 (`cad/src/sheets.py`, revision row "Far gauge cable clear of bottom flanges per BRP-DDR-003").
- `docs/decisions/0003-far-gauge-cable-route.md` (BRP-DDR-003 v0.1), new, and listed in `project.yaml` `trl_evidence`.
- `docs/pdf/` rebuilt with `python .kit/render.py`.

### Result

The far gauge cable's vertical runs now sit 3 mm (cable surface) inboard of the inner bottom-flange edges at |y| = 515 mm. A check in build123d against 800 mm of both girders gives zero overlap (was 1,277 mm³ for the far cable), with the closest approach of any cable the intended 2 mm where it is clipped under a flange. No other document stated the old value; the BOM, requirements and calculations are unaffected (R9 clearance below the soffit is unchanged).

### Photoreal renders

Regeneration of `media/render-*.png` is **not needed**: no part in any RENDER_VIEWS view (hero, exploded, detail) changes shape, size or position.

### Still Proposed, awaiting Amish

From the 2026-09-26 session: item 1 (clear window in the hub lid), item 2 (parts left out of the appearance model), item 3 (far gauge cable crossing at x = +100 mm and FieldNode cable at x = -130 mm in the appearance model), and item 5 (steel probe drawn as a 14 mm boss against the 7 mm sheath in BOM line 6).

### Status

`trl: 3` and `trl_target: 3` are unchanged; TRL 4 remains on hold. No fabrication-level detail was added.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.

## Session 2026-09-30: design for construction and prototype build plan (kit 1.7.0)

Amish's instructions of 2026-09-30: an illustrated build plan for every repo in the approved format, with outstanding decisions kept out of the plan in a separate design decisions register, and "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations."

### What was done

- Kit 1.7.0 installed (`.kit/`, `.claude/commands/`); `CLAUDE.md` matches `.kit/CLAUDE.md`.
- `cad/src/model.py` rebuilt as separate components (`build_components()`), with root fillets on the girders and 75 constructability checks (`python cad/src/model.py --check`): all pass.
- New decision record `docs/decisions/0004-design-for-construction.md` (BRP-DDR-004 v0.1, Draft): every change below, made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review.
- New `docs/05-build-plan.md` (BRP-BLD-001 v0.1) with pictures from `cad/src/build_plan_media.py`: an overview, 7 making sketches (`cad/drawings/BRP-DWG-101` to `107`), 2 hole layouts, 9 joint close-ups, 13 assembly step pictures and a wiring diagram, all in `docs/05-build-plan/`.
- New `docs/06-design-decisions.md` (BRP-DEC-001 v0.1): 11 open decisions (budget treated as a value-engineering target on 2026-10-01), 7 items to confirm when parts are bought, and the decisions made.
- Updated: BRP-CAL-001 v0.3 with `sizing.py`, BRP-REQ-001 v0.5, BRP-PRC-001 v0.5, `bom/bom.csv` (lines 1, 2, 4 to 8), `bom/bom-notes.md`, `cad/src/sheets.py` and BRP-DWG-001 Rev P5, STEP and STL, the concept media (`media/hero.png`, `exploded.png`, `cutaway.png`, `flow.png`, `concept-blueprint.*`, `model.glb`), `project.yaml` (`design_state: constructable`, evidence list) and `README.md` (links line and "Building the prototype").

### Design changes made for construction (BRP-DDR-004)

1. Mounting plate shortened to 290.6 mm and kept 22 mm clear of each flange, so it lies flat on the web between the 18 mm root fillets instead of standing on one.
2. Foot clamps redesigned: a stepped aluminium foot block screwed to the plate (two M6), with a 12 mm chamfer over the root fillet, clamped to the bottom flange by a 10 mm steel jaw, a packer outside the flange edge and an M10 bolt that ends inside the jaw.
3. Jack tab replaced by a 30 mm jack block screwed to the plate, tapped M12 the full depth, with the screw's head and lock nut below it; the screw bears 26 mm out from the web, clear of the top root fillet.
4. Hub fixed to the plate by four M5 screws from inside the box with bonded sealing washers.
5. Accelerometer board on four 5 mm spacers and signal board (now 92 x 68 mm) on four 14 mm standoffs, on countersunk M3 screws from outside the base.
6. Two M12 probe glands added; five penetrations in one row, 9 mm or more apart.
7. Steel probe is now the 7 x 60 mm sheath on the bottom flange top under a push-on flange clip (closes item 5 of the 2026-09-26 review in `model.py`).
8. Air probe hangs from the far gauge cable's crossing, its lead alongside that cable (it had hung from nothing).
9. Dummy coupons moved 35 mm out from the web, clear of the fillet, and set on silicone so they are not strained.
10. Gauge cover patches 60 x 40 mm (were 90 x 45), so no cable passes through them.
11. Cables held by push-on spring-steel flange clips; the FieldNode cable rises beside the post (it ran inside the post's outline) and plugs into port B (it ended under the antenna).
12. FieldNode on the square post: V-blocks left off, back plate flat on the post, band clamps one size longer through the plate slots; the panel in this repo's FieldNode envelope now faces away from the post (it faced the post), and the bracket envelope starts on the back plate.

### Key results

- Mass on the girder 3.21 kg (was 3.34 kg); mount resonance 135 to 271 Hz (was 126 to 253 Hz; target 120 Hz); 10 mm below the soffit at most (R9 limit 15 mm); hub 9 mm inside the flange edge line.
- **R12 is over the value-engineering target:** value-engineering target $250 (a hypothetical control target, not a limit); estimated cost of the constructable design $252.00 ($2.00 over the target; the two probe glands and the clamp parts added $4.00). Complete monitor $378.00. `budget_usd` is unchanged.
- Requirement count (BRP-CAL-001 v0.3): 1 over the value-engineering target (R12), 2 at risk (R2, R10), 3 not verifiable at TRL 3, 4 met on paper, 3 met by design.

### Proposed, awaiting Amish (in BRP-DEC-001)

1. Accept the design for construction (BRP-DDR-004, A5). Recommendation: accept.
2. Lanyard anchor (safety case). Recommendation: a second, independent beam clamp on the bottom flange.
3. Tamper resistance of the FieldNode on a public footbridge (R9). Recommendation: one-way crimped stainless banding for installations.
4. Support for the far gauge cable between the girders. Recommendation: decide at the site survey, preferring a cross member.

The savings worth trying against the value-engineering target (a consumer high-endurance card, a cheaper accelerometer breakout) are in the value engineering section of the register. Items O1 to O4 and review items 1 to 3 of 2026-09-26 remain open, as listed in the register.

### Safety

The build plan carries safety stops for lifting the girder offcuts, lead paint, gauge chemicals, first power and the FieldNode cell, and keeps installation on a bridge outside the plan. The lanyard anchor (item 2) is part of the safety case and is not yet chosen.

### Media and renders

The photoreal renders (`media/render-*.png`), `media/card.png`, `media/social-preview.png` and the appearance model `cad/src/product_model.py` are made on Amish's Mac and were not regenerated. They are now **stale**: they show the concept plate standing on the flange, the tab, the old clamps, the probe boss and two glands. `media/render-*.png` are not in this cloud copy.

### Recommended next step

Amish reviews BRP-DDR-004 and the register. TRL stays at 3; TRL 4 remains on hold.

## Session 2026-10-02: open decisions decided

On 2026-10-02 Amish approved the recommendations for every open decision: "i approve your recommendations for all 555 open decisions." The 11 open decisions of the design decisions register are now in its Decisions made table, dated 2026-10-02.

BRP-DDR-004 (design for construction) is accepted, with P12 subject to the FieldNode project confirming the square-post mount; A2 to A5 are decided as recommended, and A1 stays a value-engineering saving. Review flag 2 below concerns items 4 and 5 of the 2026-09-26 review, which BRP-DDR-004 resolved in the constructable model (P7 and the new cable routes).

### Documents changed

- `docs/06-design-decisions.md` (BRP-DEC-001 v0.3)
- `docs/decisions/0004-design-for-construction.md` (BRP-DDR-004 v0.3)
- `docs/02-concept.md` (BRP-PRC-001 v0.7)
- `docs/03-requirements.md` (BRP-REQ-001 v0.7)
- `docs/04-calcs/01-sizing.md` (BRP-CAL-001 v0.5)
- `docs/05-build-plan.md` (BRP-BLD-001 v0.3)
- `bom/bom-notes.md` (not a controlled document)

### Follow-up actions to carry approved decisions into the design

1. Decision 1: Ask the FieldNode project to confirm the square-post mount without V-blocks and the longer bands (P12); until it does, P12 stays conditional.
2. Decision 2: Model: add the second, independent girder clamp on the bottom flange at least 150 mm along the span from the foot clamps, with the lanyard run to it, and add its constructability checks.
3. Decision 2: Drawings: show the lanyard clamp on BRP-DWG-001 and the relevant making sketch.
4. Decision 2: Build plan pictures: show the lanyard clamp and lanyard in the installation and fixings figures.
5. Decision 2: BOM: add the load-rated girder clamp and stainless wire lanyard to line 4 with quantity and price.
6. Decision 2: Calculations: add the clamp to the mass on the girder (BRP-CAL-001, H1) and the cost (K), and state its required load rating against the hub's mass with a dynamic factor (H4).
7. Decision 3: BOM: add stainless banding with one-way crimped buckles for installed units (the bench unit keeps the worm-drive bands of line 8), and ask FieldNode to adopt the rule for all post installations.
8. Decision 5: Ask the FieldNode project to record its candidate pinout and Modbus RTU as decided for every adopting project; write the firmware's Modbus RTU register map when firmware starts.
9. Decision 11: Appearance model and renders: when the renders are next updated on Amish's Mac, make `cad/src/product_model.py` follow the cable routes of `cad/src/model.py`.

### Points found in the review

1. Item 11 is already decided by BRP-DDR-004 (P10 and P11) and should move out of the open table.
2. REVIEW 2026-09-26 items 4 (cable passing through the flange) and 5 (probe sheath) were resolved by BRP-DDR-004 (P7 and the new routes) but are not marked closed.
3. The FieldNode candidate pinout is described in FieldNode's own records as 'for discussion only'; both repos are waiting on each other, so the decision needs to be made once, in FieldNode.

No CAD model, BOM quantity or price, calculation result or picture was changed. TRL stays at 3; TRL 4 remains on hold.

## Session 2026-10-02: approved follow-ups carried out

Amish approved on 2026-10-02 that every follow-up action from the open-decision sign-off be carried out ("APPROVED CHANGES, COMPLETE THESE") and that the render scenes be prepared for new photoreal renders. TRL stays at 3; nothing here builds, tests or buys anything.

### Follow-ups, one by one

1. **Decision 1, FieldNode to confirm the square-post mount (P12).** Done in this repo: P12 stays conditional in BRP-DEC-001 (items to confirm, 5). The request to FieldNode is listed under Cross-repo actions below.
2. **Decision 2, model.** Done. `cad/src/model.py` now has a stainless pad eye on two M5 screws at the top left of the plate, a 3 mm stainless wire lanyard with a thimble eye round the pad eye's loop and round the clamp's eye, and a bought single-flange girder clamp with an eye, set screw and lock nut hooked on the south bottom flange tip at x = -275 mm, 159 mm along the span from the nearer foot clamp. The plate's plain 6.5 mm lanyard hole is replaced by the two tapped M5 holes: with the plate flat on the web, a wire could not have passed through a plain hole. 16 new constructability checks (pad eye on the plate, screws short of the web, clamp on the flange, set screw on the flange top, 150 mm or more from the foot clamps, lanyard bearing on both eyes and clear of girder, hub, mount, cables and probes): **91 of 91 pass**. STEP and STL regenerated (`cad/step/`, `cad/stl/`); the pad eye is part of `sensor-hub.step`.
3. **Decision 2, drawings.** Done. BRP-DWG-001 **Rev P6** shows the girder clamp and the lanyard in the front view, with the 159 mm clearance dimensioned, the pad eye in detail A and a line in the notes. Making sketch BRP-DWG-101 (mounting plate) **Rev P2** gives the pad eye holes in place of the lanyard hole. The clamp, pad eye and lanyard are bought, so they have no making sketch.
4. **Decision 2, build plan pictures.** Done. New joint 10 (girder clamp on the flange) and new step 9 (lanyard and its girder clamp); the overview shows the lanyard as component 17; the plate hole layout shows the pad eye holes; steps 10 to 14 (were 9 to 13) show the fitted lanyard. All step pictures redrawn with the longer bench offcut needed for the clamp.
5. **Decision 2, BOM.** Done. Line 4 ($40.00 to $59.00): girder clamp with a working load limit of 100 kg or more $12.00, pad eye and screws $3.00, made-up wire lanyard $6.00 in place of the $2.00 plain lanyard. Basis for each price in `bom/bom-notes.md`.
6. **Decision 2, calculations.** Done. BRP-CAL-001 v0.6: H1 adds the lanyard parts (0.37 kg; **3.58 kg on the girder**, was 3.21 kg); H4a and H4c rate the lanyard and clamp: 3.21 kg falling onto 25 mm of slack in a 436 mm wire gives a **1.20 kN peak, a dynamic factor of 38**, so the clamp needs a working load limit of 30 kg or more at a 4:1 design factor (specified 100 kg or more) and the wire's assumed 4.8 kN breaking load is 4.0 times the peak; K adds the cost.
7. **Decision 3, BOM.** Done. New line 10, installation banding for installed units only: two lengths of 12.7 x 0.76 mm stainless band and two one-way crimped buckles, $4.00; the bench unit keeps the worm-drive bands of line 8. The request to FieldNode is a cross-repo action.
8. **Decision 5, pinout and register map.** The FieldNode request is a cross-repo action. **Not done:** the firmware's Modbus RTU register map, because firmware has not started; under the TRL 3 cap firmware beyond a labelled sketch is not allowed. It stays a follow-up for when firmware starts.
9. **Decision 11, appearance model.** Done. `cad/src/product_model.py` rebuilt from `build_components()` so every part except the appearance hub shell (filleted box, lid, gasket, window, labels) is the constructable model's own geometry: plate, foot blocks, jaws, packers, bolts, jack block, jack screw, glands, connector, boards, probe and clip, gauges, the lanyard and its girder clamp, and the cables and flange clips on the model's routes, cut to a 640 mm girder section. RENDER_VIEWS kept (hero, exploded, detail). Render scenes exported with `.kit/export_views.py` to `/home/claude/renders/bridgepulse`: `bridgepulse__hero`, `__exploded` and `__detail` (.npz and .json each) and `bridgepulse__jobs.json`. Photoreal renders, `media/card.png` and `media/social-preview.png` are to be made on Amish's Mac.

### Documents changed and new versions

- `cad/src/model.py`, `cad/src/sheets.py`, `cad/src/build_plan_media.py`, `cad/src/concept_media.py`, `cad/src/product_model.py`, `docs/04-calcs/sizing.py`
- `cad/drawings/BRP-DWG-001` Rev P6; `cad/drawings/BRP-DWG-101` Rev P2
- `docs/04-calcs/01-sizing.md` (BRP-CAL-001 v0.6)
- `docs/03-requirements.md` (BRP-REQ-001 v0.8)
- `docs/02-concept.md` (BRP-PRC-001 v0.8)
- `docs/05-build-plan.md` (BRP-BLD-001 v0.4): new section 3.11 and step 9, steps renumbered, bench offcuts about 650 mm (about 37 kg each), first check and safety stops S7 and S8 name the lanyard; the "pictures unchanged" note of v0.3 is gone
- `docs/06-design-decisions.md` (BRP-DEC-001 v0.4): value engineering restated; item 8 to confirm (clamp rating, wire breaking load)
- `docs/decisions/0004-design-for-construction.md` (BRP-DDR-004 v0.4): consequences updated
- `bom/bom.csv`, `bom/bom-notes.md`, `README.md`
- Pictures: `docs/05-build-plan/overview.png`, `plate-holes.png`, `joint-10.png` (new), `step-05.png` to `step-14.png` (`step-14.png` new); `media/hero.png`, `exploded.png`, `cutaway.png`, `concept-blueprint.*`, `model.glb`. The cutaway leaves the lanyard parts out, since its section plane would cut the clamp away from its wire.

### Requirement status changes

- **R12:** still over the value-engineering target, now by **$25.00** (was $2.00). Value-engineering target: USD 250.00. Estimated cost of the constructable design: USD 275.00 (USD 25.00 over the target). Complete monitor $401.00. `budget_usd` unchanged. The savings named in the register (consumer high-endurance card, cheaper accelerometer breakout) no longer close the gap on their own.
- R9 stays met on paper: the girder clamp's lower jaw is 8 mm below the soffit, within the 10 mm worst case and the 15 mm limit.
- No other status changes. Counts: 1 over the value-engineering target (R12), 2 at risk (R2, R10), 3 not verifiable at TRL 3, 4 met on paper, 3 met by design.
- BRP-CAL-001 H3 now quotes the printed 75 Hz (the note said 77 Hz); a text correction, no status change.

### Cross-repo actions (for the FieldNode repo; not edited here)

- FieldNode to confirm the square-post mount without V-blocks and the band clamps one size longer, band about 300 to 330 mm (BRP-DDR-004, P12); until then P12 stays conditional.
- FieldNode to adopt one-way crimped stainless banding for all its post installations, with worm-drive bands only on the bench (BRP-DEC-001, decision of 2026-10-02 on tamper resistance).
- FieldNode to record its candidate pinout (pin 1 switched 5 V rail, pins 2 and 4 RS-485 A and B, pin 3 ground, pin 5 analog) and Modbus RTU as decided for every adopting project; its own records still call the pinout "for discussion only".

### Proposed, awaiting Amish

- Appearance deviations in `cad/src/product_model.py`: the hub is drawn as a filleted, powder-coated box with lid screws, a name plate, labels and the clear lid window (the window decided as a render aid on 2026-10-02); the cables, probe lead and clips are cut at the ends of the girder section; the lanyard is drawn taut. Recommendation: accept as appearance only.
- R12 at $25.00 over the target: the girder clamp is the largest addition. Options: (a) accept the gap until TRL 4 quotes; (b) take the microSD saving now (about $10); (c) look for a cheaper rated clamp. Recommendation: (a) with (b), since the clamp is part of the safety case.

### Safety

The lanyard is now a real, rated second retention path that shares nothing with the foot clamps. Its peak load depends mostly on slack, so the build plan and safety stop S8 limit it to 25 mm; the clamp rating and the wire breaking load are assumed catalogue values to confirm when parts are bought (register item 8). The bench offcuts are now about 37 kg each; the plan says two people or a hoist.

### Recommended next step

Amish makes the photoreal renders from the exported scenes on his Mac, then runs `.kit/cards.py`. The FieldNode project takes up the three cross-repo actions. TRL stays at 3; TRL 4 remains on hold.

## 2026-10-02: photoreal renders redone on the constructable design

Rendered with Blender Cycles on Amish's Mac from the updated appearance model (`cad/src/product_model.py`); captioned with `.kit/photo_caption.py`; `media/card.png` and `media/social-preview.png` regenerated with `.kit/cards.py`. Views: hero, exploded, detail. image_qc passes. Appearance deviations are those logged above as proposed, awaiting Amish.
