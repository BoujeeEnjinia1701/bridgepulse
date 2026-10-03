# BOM notes

Prices are indicative (TRL 3), each with a supplier or supplier type in `bom/bom.csv`; every line is priced. Item numbers 1 to 8 match the exploded view in `media/exploded.png`; item 9, the microSD card, sits in the signal board, and item 10, the installation banding, is used only on installed units and is not modelled. Totals are checked by `docs/04-calcs/sizing.py` (BRP-CAL-001, section K).

| Group | Items | Cost |
| --- | --- | --- |
| BridgePulse-specific parts | 1 to 7, 9, 10 | $275.00 |
| FieldNode core (shared component, costed in the FieldNode repo) | 8 | $126.00 |
| **Complete monitor for one bridge** | 1 to 10 | **$401.00** |

`budget_usd` in `project.yaml` is $250. Under BRP-DDR-001 D1 (decided by Amish, 2026-09-25: go with recommendation), it is a hypothetical value-engineering target covering the BridgePulse-specific parts. Value-engineering target: USD 250.00. Estimated cost of the constructable design: USD 275.00 (USD 25.00 over the target, 10.0 %). The complete monitor is $151.00 over the $250 target and is always stated beside it. The savings named in BRP-DDR-002 (a consumer high-endurance card and a cheaper accelerometer breakout that still meets R1) would recover part of the gap; see the value engineering section of the design decisions register (`docs/06-design-decisions.md`).

Change under BRP-DDR-002: item 6 is now a TMP1826 class probe potted in a stainless sheath at $6.00 each (was a DS18B20 class probe at $4.00), so R5 holds down to -20 °C; +$4.00.

Changes from TRL 2 ($216 BridgePulse-specific, $342 complete): the mounting plate is now an aluminium plate jacked between the flanges with two flange-tip clamps (BRP-CAL-001, section H); the signal board gains a buck converter and an RS-485 transceiver for the FieldNode link; the microSD card is a separate industrial-grade line; the cable line adds a moulded M12 5-pin cable to the FieldNode port.

The bridge itself, installation labor, access equipment, traffic management, paint testing and consumables for surface preparation are not included.

Change under BRP-DDR-004 (design for construction, 2026-09-30): item 1 adds two M12 probe glands and the base fixing (+$2.00, now $22.00); item 4 becomes the plate with two foot blocks, two steel jaws, two packers, a jack block and their screws (+$2.00, now $40.00); items 2, 5, 6, 7 and 8 have their fixing spelled out (spacers, coupon on silicone, probe flange clip, push-on flange clips, FieldNode V-blocks left off and longer bands) at no change in price.

Decisions of 2026-10-02 (BRP-DEC-001), carried into the BOM on 2026-10-02: line 4 gains the lanyard anchor (+$19.00, now $59.00) and a new line 10 carries the installation banding ($4.00). Installed units hold the FieldNode with stainless banding and one-way crimped buckles; the worm-drive bands of line 8 are for the bench unit.

| Line | Part added | Qty | Price | Basis |
| --- | --- | --- | --- | --- |
| 4 | Single-flange girder clamp with an eye, set screw and lock nut, working load limit 100 kg or more | 1 | $12.00 | Indicative small-quantity price for a galvanized malleable iron or steel beam clamp of this class; the rating need is in BRP-CAL-001, H4c |
| 4 | Stainless pad eye, 38 x 22 mm base, with two M5 x 10 stainless screws | 1 | $3.00 | Indicative marine hardware price for a 316 stainless pad eye and two screws |
| 4 | Made-up 3 mm 7 x 7 stainless wire lanyard, about 0.45 m, thimble eye and crimped ferrule at each end | 1 | $6.00, replacing the $2.00 plain lanyard already in the line (+$4.00) | Indicative rigging supplier price for a short made-up lanyard |
| 10 | 12.7 x 0.76 mm 304 stainless banding, two lengths of about 0.4 m, and two one-way crimped buckles | 1 set | $4.00 | About $0.80 a metre of band from a 30 m roll and about $1.00 a buckle, with an allowance for waste; the banding tool is borrowed or hired |

Mass of the line 4 additions from the model: 0.37 kg on the girder (BRP-CAL-001, H1).
