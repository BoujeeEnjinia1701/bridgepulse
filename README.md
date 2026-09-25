# BridgePulse

**Area:** Smart Cities · **Status:** Concept · **Prototype budget:** about $250 USD · **Difficulty:** 3 of 5

A vibration and strain monitor for small bridges and footbridges that tracks natural frequency and strain over time to flag changes that need inspection.

## Concept rationale

Changes in natural frequency and strain can flag damage between inspections.

## Burning platform

Aging infrastructure backlogs are large, and bridge failures are catastrophic.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| _To be developed_ | |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| _To be developed_ | |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It feeds CityTwin.

## Problem

Many small bridges are inspected rarely, and deterioration is found late.

## Concept

A vibration and strain monitor for small bridges and footbridges that tracks natural frequency and strain over time to flag changes that need inspection.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Accelerometer
- Strain gauges and bridge amplifier
- Temperature sensor
- FieldNode core
- Mounting brackets

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> A research prototype; it supports but never replaces inspection by qualified engineers. Street furniture and pole mounts must be installed only with the asset owner's permission, by trained crews, with fall protection and traffic management as local rules require.

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

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Smart cities set.
