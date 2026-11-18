---
uri: work/flow/holonomy/TASKFLOW_SPRINT_BOARD.md
owner: edphos
title: TaskFlow Sprint Board — Phosphene Holonomy & Etienne vs. Foley Paper Sprint
status: completed
track: holonomy.package-and-paper-sprint
created: 2026-11-18
updated: 2026-11-18
---

# TASKFLOW_SPRINT_BOARD.md

Sprint board tracking the implementation of `phosphene/holonomy` as the canonical standalone package repository for differential-geometric, data-preserving, and macroevolutionary diversification primitives, alongside the complete comparative paper analyzing Etienne (2012) / Valente et al. (2015) Galápagos empirical radiation vs. Foley & Van Holstein (2024) hominin PyRate claims.

---

## Sprint Overview

| ID | Module / Track | Type | Pri | Title | Owner | Status |
|---|---|---|---|---|---|---|
| **TF-HOL-001** | `holonomy.macroevo.galapagos` | data & schema | high | Ingest canonical Galápagos avifauna dataset & typed dataclasses | edphos + flow | closed |
| **TF-HOL-002** | `holonomy.macroevo.master_equation` | feature | high | Continuous-time master equation branching likelihood & profile solver | edphos + flow | closed |
| **TF-HOL-003** | `holonomy.macroevo.comparative_metrics` | feature | high | Cross-domain metric extractor (Archipelago vs. Continental Taphonomy) | edphos + flow | closed |
| **TF-HOL-004** | `tests/test_galapagos_etienne.py` | test | high | Comprehensive unit, property, and convergence tests for Galápagos | edphos + flow | closed |
| **TF-HOL-005** | `tests/test_hominin_vs_galapagos.py` | test | high | Profile likelihood flat surface test on hominin lineages | edphos + flow | closed |
| **TF-HOL-006** | `docs/COMPARATIVE_PAPER_ETIENNE_VS_FOLEY.md` | docs/paper | high | Full comparative scientific monograph & paper draft | edphos + flow | closed |

---

## Task Verification & Invariants

1. **Test Suite:** 16/16 tests passing in `uv run pytest` (<7s).
2. **Package Invariants:** Strict type safety, log-space stability, physical invariants ($K \ge S$).
3. **Standalone Integrity:** Zero external dependencies beyond `numpy`, `scipy`, `pydantic`.
