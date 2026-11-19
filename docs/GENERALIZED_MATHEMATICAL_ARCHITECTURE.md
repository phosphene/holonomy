# Holonomy: Generalized Mathematical Architecture and Domain Specialization

**Namespace:** `holonomy.core`  
**Authors:** Systems Architect (Ed Phil), Research Principal (Jan), Flow (`@feelingflowingbot`)  
**Status:** Living Canonical Architecture Specification  
**Date:** November 2026  
**Repository:** `phosphene/holonomy`  

---

## 1. Executive Summary

This specification formalizes `holonomy` as a **universal mathematical engine for path-dependent dynamical systems, non-abelian hysteresis, and geometric state preservation**.

Rather than restricting the top-level interface to the vocabulary of any single empirical substrate (such as coastal sediment transport or river hydraulics), `holonomy` elevates the governing mathematics into generic, timeless abstractions:

1. **The Pure Mathematical Kernel (`holonomy.core` / root):** Operates on abstract state manifolds $\mathcal{M}$, parameterized control loops $\gamma \subset \mathcal{C}$, constitutive transfer operators $\mathcal{J}$, continuity/conservation laws $\mathcal{D}$, immutable evolution traces $\mathcal{T}$, and holonomy defects $\Delta \mathcal{M}$.
2. **The Domain Dialects (`holonomy.geomorph`, `holonomy.morphometrics`, `holonomy.macroevo`):** Isomorphic specializations of the mathematical kernel that provide natural language entry points native to each scientific literature (`bed/flow/flux/exner` for geomorphology, `configuration/loading/deformation` for skeletal morphometrics, and `trajectory/saturation/master_equation` for macroevolution).
3. **The Three-Phase Process (Pull $\to$ Transform $\to$ Push):** Strict grammatical predication where in-memory transformations are pure, noun-led functions producing immutable values, and operational boundaries (I/O, validation, archiving) are verb-led.

---

## 2. The Universal Mathematical Pipeline

In any physical or macroevolutionary system exhibiting dissipative hysteresis, cyclic driving does not return the system to its initial configuration. The path integral of state change over a closed control trajectory forms a non-vanishing residue:

$$\Delta \mathcal{M} = \oint_\gamma \partial_t \mathcal{M} \, dt \neq 0$$

The universal pipeline decomposes into six primitive concepts:

| Mathematical Concept | Universal Sign (`holonomy.core`) | Mathematical Role |
| :--- | :--- | :--- |
| **State Manifold** | `Manifold`, `State` | Immutable spatial, shape, or diversity configuration inhabiting coordinate space $\mathcal{M}$. |
| **Control Loop** | `ControlLoop`, `Forcing` | Parameterized cycle $\gamma(t): [0, T] \to \mathcal{C}$ such that $\mathcal{F}(0) = \mathcal{F}(T)$. |
| **Transfer Operator** | `Transfer`, `transfer_flux` | Pure constitutive mapping $(\mathcal{M}, \mathcal{F}) \mapsto \mathbf{J}$ producing flux/rate fields. |
| **Continuity Law** | `Continuity`, `next_state` | Mass, energy, or probability conservation operator: $\partial_t \mathcal{M} = -\mathcal{D}(\mathbf{J})$. |
| **Evolution Trace** | `EvolutionTrace`, `Trace` | Ordered, append-only lineage of immutable states along $\gamma$: $\{\mathcal{M}(t_k)\}_{k=0}^N$. |
| **Holonomy Defect** | `HolonomyDefect`, `defect` | Closed-loop path-dependent residue: $\Delta \mathcal{M} = \mathcal{M}(T) - \mathcal{M}(0)$. |

---

## 3. Domain Specialization Topology

```
holonomy/
├── core/                       # Generalized Mathematical Kernel (Timeless Sense)
│   ├── manifold.py             # Immutable coordinate grids, shapes, and state vectors
│   ├── forcing.py              # Cyclic & transient control schedules
│   ├── transfer.py             # Constitutive flux & rate operators
│   ├── continuity.py           # Conservation laws & ODE/matrix exponential integrators
│   └── trace.py                # Lineage graphs, rollback, and holonomy defect audits
│
├── geomorph/                   # Fluvial & Coastal Sediment Transport Dialect
│   ├── bed.py                  # Bathymetric boundary & active-layer stratigraphy
│   ├── flow.py                 # Hydrodynamic forcing fields (velocity, shear stress)
│   ├── flux.py                 # Solid sediment discharge & transport closures (MPM, Engelund)
│   └── exner.py                # Exner mass-conservation law & cyclic bed defect
│
├── morphometrics/              # Skeletal & Biological Morphogenesis Dialect
│   ├── configuration.py        # Landmark configurations in Kendall shape space
│   ├── strain.py               # Biomechanical loading & ontogenetic force fields
│   ├── deformation.py          # Allometric strain tensors & growth vector fields
│   └── remodeling.py           # Structural continuity & permanent morphological defect
│
├── macroevo/                   # Macroevolutionary Diversification Dialect (PyRate Replacements)
│   ├── trajectory.py           # Standing diversity & lineage-through-time profiles
│   ├── master_equation.py      # Etienne continuous-time Markov solver (expm)
│   ├── taphonomy.py            # Keiding observation conditioning & horizon arrivals
│   └── comparative.py          # Cross-domain metrics (Archipelago vs. Continental Taphonomy)
│
└── io/                         # Unified Operational Adapters (Pull & Push Boundaries)
    ├── ingest.py               # Boundary readers with assumption verification
    └── export.py               # Lineage & defect serializers (Zarr, Parquet, NetCDF, JSON)
```

---

## 4. Lossless Skimming Across Dialects

Because all domain specializations execute the identical core contracts, user scripts across different disciplines share the same grammatical clarity:

### Fluvial Geomorphology:
```python
from holonomy.geomorph import bed, flow, flux, exner

initial_bed = bed.read_bathymetry("estuary.nc")
tidal_flows = flow.read_hydrograph("spring_neap.nc")
beds = exner.evolution_trace(initial_bed, tidal_flows, closure=flux.bedload)
net_erosion = exner.holonomy_defect(beds)
```

### Skeletal Morphometrics:
```python
from holonomy.morphometrics import configuration, strain, deformation, remodeling

initial_cranium = configuration.read_landmarks("specimen_m1.ply")
chewing_strains = strain.read_cycles("mastication_profile.json")
ontogeny = remodeling.growth_trace(initial_cranium, chewing_strains, tensor=deformation.allometric)
cranial_divergence = remodeling.morphological_defect(ontogeny)
```

### Macroevolutionary Diversification:
```python
from holonomy.macroevo import trajectory, master_equation

finches_brts = trajectory.read_branching_times("galapagos_finches.csv")
solution = master_equation.solve_master_equation(finches_brts, k_carrying_capacity=20.0)
profile = master_equation.profile_carrying_capacity(finches_brts, k_grid=[16, 20, 30, 50])
```
