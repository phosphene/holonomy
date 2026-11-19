# holonomy

A generic mathematical engine for path-dependent dynamical systems, non-abelian hysteresis, and geometric state preservation.

`holonomy` provides pure, immutable, and differentiable abstractions for modeling systems where state changes depend on the path taken through control space. In continuum mechanics, geometry, and non-linear dynamics, traversing a closed parameter loop $\gamma(t)$ leaves a permanent residual displacement in state:

$$\Delta \mathcal{M} = \oint_\gamma \partial_t \mathcal{M} \, dt \neq 0$$

Elevating this governing physical invariant into software guarantees **trajectory preservation by definition**: every state is treated as an immutable value, and time evolution records an explicit, verifiable lineage rather than performing in-place buffer mutations.

---

## 1. Pure Mathematical Core (`holonomy.core` / root)

The top-level package operates on timeless mathematical abstractions:

- **`Manifold` & `State`**: Immutable spatial configurations, coordinate discretizations, or abstract metric spaces ($\mathcal{M}_0$). Array buffers are strictly read-only (`flags.writeable = False`).
- **`ControlLoop` & `ForcingField`**: Parameterized trajectories in external control space traversing closed or transient forcing curves ($\gamma(t): [0, T] \to \mathcal{C}$ such that $\mathcal{F}(0) = \mathcal{F}(T)$).
- **`TransferClosure` & `compute_flux_divergence`**: Pure constitutive mappings $(\mathcal{M}, \mathcal{F}) \mapsto \mathbf{J}$ producing generalized flux or transfer vector fields.
- **`next_state`**: Generalized continuity/conservation integration: $\partial_t \mathcal{M} = -\mathcal{D}(\mathbf{J})$.
- **`EvolutionTrace` & `HolonomyDefect`**: Ordered, append-only lineage of immutable states along a control loop, enabling zero-loss historical rollback, mass/energy conservation auditing, and exact path residue calculation ($\Delta \mathcal{M} = \mathcal{M}(T) - \mathcal{M}(0)$).

---

## 2. Domain Specialization Dialects

The generalized mathematical kernel is specialized into domain dialects that provide natural language entry points native to each scientific literature:

### A. Fluvial & Coastal Geomorphology (`holonomy.geomorph`)
Models erodible bed evolution under cyclic hydrodynamic forcing (tides, floods, storm waves):
- `Bed`: Bathymetric boundary geometry and active-layer stratigraphy.
- `Flow`: Hydrodynamic forcing fields (velocity, boundary shear stress).
- `flux.meyer_peter_muller` / `flux.flux_divergence`: Constitutive sediment transport closures.
- `exner.next_bed` / `exner.bed_evolution_trace` / `exner.holonomy_defect`: Exner sediment mass conservation $\partial_t \eta = -\frac{1}{1-p} \nabla \cdot \mathbf{q}_s$ and cyclic topographic displacement.

### B. Skeletal Morphometrics & Morphogenesis (`holonomy.morphometrics`)
Models biological form generation, allometric scaling, and permanent anatomical divergence:
- `Configuration`: Landmark configurations and centroid sizes in Kendall shape space.
- `allometric_growth_closure`: Differential growth tensors driven by ontogenetic stress gradients.
- `remodeling.ontogenetic_trace` / `remodeling.morphological_defect`: Structural continuity and permanent skeletal divergence across cyclic loading.

### C. Deterministic Macroevolutionary Suite (`holonomy.macroevo`)
Replaces heuristic, destructive random-walk MCMC tools (such as PyRate) with deterministic profile likelihoods and continuous-time Markov models:
- `master_equation`: Continuous-time Markov master equation solver (Etienne 2012) via matrix exponentiation (`expm`), enforcing physical carrying capacity ceilings ($S \le K$) and survival conditioning.
- `diversity_surface`: Exact profile likelihood surfaces $\mathcal{L}(G_l)$ and formal $\chi^2$ likelihood-ratio tests over lineage-through-time curves.
- `taphonomy`: Taphonomically conditioned Poisson occurrence models with Keiding (1975) truncation correction.
- `galapagos`: Canonical Valente, Phillimore, & Etienne (2015) empirical insular avifaunal radiation dataset.
- `comparative_metrics`: Cross-domain comparison contrasting bounded insular radiations against sparse continental taphonomy.

---

## 3. Quickstart & Lossless Skimming

### Pure Core Engine:
```python
import numpy as np
from phosphene.holonomy import (
    Manifold,
    State,
    ControlLoop,
    linear_gradient_transfer,
    evolution_trace,
)

# 1. Establish immutable state manifold
x = np.linspace(0, 1000, 21)
y = np.linspace(0, 500, 11)
baseline = np.zeros((11, 21))
manifold = Manifold.from_grid(x, y, baseline)
initial_state = State.create(manifold, baseline)

# 2. Evaluate evolution trace across cyclic control loop
loop = ControlLoop.sinusoidal(period=3600.0, num_steps=12, shape=manifold.shape)
closure = linear_gradient_transfer(diffusion_coeff=0.05)
trace = evolution_trace(initial_state, loop, closure)

# 3. Audit closed-loop holonomy defect
defect = trace.defect()
print(f"Holonomy Defect L2 Norm: {defect.norm:.4e}")
```

### Geomorphology Dialect:
```python
from phosphene.holonomy.geomorph import (
    Bed,
    sinusoidal_hydrograph,
    meyer_peter_muller,
    bed_evolution_trace,
    holonomy_defect,
)

initial_bed = Bed.from_elevation(x, y, baseline)
hydrograph = sinusoidal_hydrograph(period=43200.0, num_steps=24, shape=initial_bed.elevation.shape)
trace = bed_evolution_trace(initial_bed, hydrograph, meyer_peter_muller())
net_displacement = holonomy_defect(trace)
```

---

## 4. Documentation & Specifications

- [`docs/GENERALIZED_MATHEMATICAL_ARCHITECTURE.md`](docs/GENERALIZED_MATHEMATICAL_ARCHITECTURE.md): Formal architectural specification, semantic triad (Frege), and Three-Phase Process (Pull $\to$ Transform $\to$ Push).
- [`docs/LITERATE_SPECIFICATION.md`](docs/LITERATE_SPECIFICATION.md): Literate code walkthrough and mathematical mapping across the core kernel and domain dialects.
- [`docs/COMPARATIVE_PAPER_ETIENNE_VS_FOLEY.md`](docs/COMPARATIVE_PAPER_ETIENNE_VS_FOLEY.md): Comparative analysis: *“Transcending Birth-Death Storytelling: A Comparative Analysis of Diversity-Dependent Diversification in Insular Archipelagos vs. Continental Hominin Taphonomy”*.

---

## 5. Development & Testing

```bash
uv sync
uv run pytest
```
