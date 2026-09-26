# BOM notes

Prices are indicative (TRL 3), each with a supplier or supplier type in `bom/bom.csv`; every line is priced. Item numbers 1 to 8 match the exploded view in `media/exploded.png`; item 9, the microSD card, sits in the signal board. Totals are checked by `docs/04-calcs/sizing.py` (BRP-CAL-001, section K).

| Group | Items | Cost |
| --- | --- | --- |
| BridgePulse-specific parts | 1 to 7, 9 | $248.00 |
| FieldNode core (shared component, costed in the FieldNode repo) | 8 | $126.00 |
| **Complete monitor for one bridge** | 1 to 9 | **$374.00** |

`budget_usd` in `project.yaml` is $250. Under BRP-DDR-001 D1 (decided by Amish, 2026-09-25: go with recommendation), it covers the BridgePulse-specific parts: $248.00, a margin of $2.00 (0.8 %), which is thin for indicative prices, so R12 is at risk. The complete monitor is $124.00 over $250 and is always stated beside it. If quotes come in higher, the first savings are a consumer high-endurance card and a cheaper accelerometer breakout that still meets R1 (BRP-DDR-002).

Change under BRP-DDR-002: item 6 is now a TMP1826 class probe potted in a stainless sheath at $6.00 each (was a DS18B20 class probe at $4.00), so R5 holds down to -20 °C; +$4.00.

Changes from TRL 2 ($216 BridgePulse-specific, $342 complete): the mounting plate is now an aluminium plate jacked between the flanges with two flange-tip clamps (BRP-CAL-001, section H); the signal board gains a buck converter and an RS-485 transceiver for the FieldNode link; the microSD card is a separate industrial-grade line; the cable line adds a moulded M12 5-pin cable to the FieldNode port.

The bridge itself, installation labor, access equipment, traffic management, paint testing and consumables for surface preparation are not included.
