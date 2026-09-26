# BOM notes

Prices are indicative (TRL 3), each with a supplier or supplier type in `bom/bom.csv`; every line is priced. Item numbers 1 to 8 match the exploded view in `media/exploded.png`; item 9, the microSD card, sits in the signal board. Totals are checked by `docs/04-calcs/sizing.py` (BRP-CAL-001, section K).

| Group | Items | Cost |
| --- | --- | --- |
| BridgePulse-specific parts | 1 to 7, 9 | $244.00 |
| FieldNode core (shared component, costed in the FieldNode repo) | 8 | $126.00 |
| **Complete monitor for one bridge** | 1 to 9 | **$370.00** |

`budget_usd` in `project.yaml` is $250. Under BRP-DDR-001 D1 (adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review), it covers the BridgePulse-specific parts: $244.00, a margin of $6.00 (2.4 %), which is thin for indicative prices, so R12 is at risk. The complete monitor is $120.00 over $250 and is always stated beside it.

Changes from TRL 2 ($216 BridgePulse-specific, $342 complete): the mounting plate is now an aluminium plate jacked between the flanges with two flange-tip clamps (BRP-CAL-001, section H); the signal board gains a buck converter and an RS-485 transceiver for the FieldNode link; the microSD card is a separate industrial-grade line; the cable line adds a moulded M12 5-pin cable to the FieldNode port.

The bridge itself, installation labor, access equipment, traffic management, paint testing and consumables for surface preparation are not included.
