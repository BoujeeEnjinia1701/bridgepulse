# BOM notes

Prices are indicative (TRL 3), each with a supplier or supplier type in `bom/bom.csv`; every line is priced. Item numbers 1 to 8 match the exploded view in `media/exploded.png`; item 9, the microSD card, sits in the signal board. Totals are checked by `docs/04-calcs/sizing.py` (BRP-CAL-001, section K).

| Group | Items | Cost |
| --- | --- | --- |
| BridgePulse-specific parts | 1 to 7, 9 | $252.00 |
| FieldNode core (shared component, costed in the FieldNode repo) | 8 | $126.00 |
| **Complete monitor for one bridge** | 1 to 9 | **$378.00** |

`budget_usd` in `project.yaml` is $250. Under BRP-DDR-001 D1 (decided by Amish, 2026-09-25: go with recommendation), it covers the BridgePulse-specific parts: $252.00, which is $2.00 (0.8 %) over, so R12 is not met. The complete monitor is $128.00 over $250 and is always stated beside it. The savings named in BRP-DDR-002 (a consumer high-endurance card and a cheaper accelerometer breakout that still meets R1) would bring it back under; whether to take them or raise the budget is open for Amish in the design decisions register (`docs/06-design-decisions.md`).

Change under BRP-DDR-002: item 6 is now a TMP1826 class probe potted in a stainless sheath at $6.00 each (was a DS18B20 class probe at $4.00), so R5 holds down to -20 °C; +$4.00.

Changes from TRL 2 ($216 BridgePulse-specific, $342 complete): the mounting plate is now an aluminium plate jacked between the flanges with two flange-tip clamps (BRP-CAL-001, section H); the signal board gains a buck converter and an RS-485 transceiver for the FieldNode link; the microSD card is a separate industrial-grade line; the cable line adds a moulded M12 5-pin cable to the FieldNode port.

The bridge itself, installation labor, access equipment, traffic management, paint testing and consumables for surface preparation are not included.

Change under BRP-DDR-004 (design for construction, 2026-09-30): item 1 adds two M12 probe glands and the base fixing (+$2.00, now $22.00); item 4 becomes the plate with two foot blocks, two steel jaws, two packers, a jack block and their screws (+$2.00, now $40.00); items 2, 5, 6, 7 and 8 have their fixing spelled out (spacers, coupon on silicone, probe flange clip, push-on flange clips, FieldNode V-blocks left off and longer bands) at no change in price.
