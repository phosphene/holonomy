# holonomy: Differential Geometry, Data-Preserving Architecture, and Deterministic Macroevolution

`holonomy` is the canonical Phosphene Python package for morphodynamics, sedimentological transport, and macroevolutionary diversification inference. It completely replaces legacy empirical MCMC tools (such as PyRate) with deterministic profile likelihoods, continuous-time Markov master equations, and data-preserving geometry.

---

## 1. Mapping Morphodynamic Math to Package Primitives

```
                      [holonomy.Loop]
                 Parameterized Forcing:
              ∮ [τ_x(t), τ_y(t), h(t)] dt
                          │
                          ▼
holonomy.Manifold M₀ ───────────────► holonomy.Defect Δη
(Immutable Bathymetry,              (Net Geometric Residual,
 read-only array flags)              exact displacement)
                          ▲
                          │
             [holonomy.Connection]
             Flux Operator: -∇ · q_s
             Pure Exner integration
```

- **`holonomy.Manifold`**: The immutable reference bathymetry and spatial discretization (the initial coordinate surface $\mathcal{M}_0$ held strictly read-only with `flags.writeable = False` so baseline grids survive every run intact).
- **`holonomy.Connection`**: The sediment-flux differential operator $-\nabla \cdot \mathbf{q}_s$ (the transport rule dictating how boundary shear shifts mass between neighboring cells without mutating shared arrays). Advances the Exner equation:
  $$\partial_t \eta = -\frac{1}{1 - p} \nabla \cdot \mathbf{q}_s$$
- **`holonomy.Loop`**: A parameterized trajectory of hydrodynamic boundary conditions (an ordered forcing schedule across tidal phases, storm hydrographs, or wave climates).
- **`holonomy.Defect`**: The net morphological displacement $\Delta \eta = \oint \partial_t \eta \, dt$ (the exact geometric residual obtained by comparing preserved initial and final states after traversing a forcing cycle). Non-zero norm $\|\Delta \eta\| > 0$ indicates non-trivial holonomy (irreversible morphological work).

---

## 2. Data-Preserving Execution Architecture

### Trajectory Preservation by Definition
Replacing PyRate requires eliminating destructive in-place array mutations (overwriting memory buffers during time-stepping). Because **holonomy is an invariant of a path rather than an isolated grid**, the name makes data preservation a mathematical prerequisite: computing a path-dependent residue requires keeping both the reference manifold $\mathcal{M}_0$ (the untouched initial bathymetry) and the ordered state lineage (every intermediate bed configuration along the forcing curve).

- **Immutable State Transitions (`SurfaceState`)**: Advancing the Exner equation returns a newly allocated elevation field paired with a zero-copy reference to the static horizontal mesh (eliminating the in-place buffer overwrites that caused PyRate to destroy historical data while avoiding redundant coordinate duplication).
- **Explicit Trajectory Graphs (`holonomy.Trace`)**: Chaining steps along a `Loop` records a directed lineage of snapshots (enabling instant rollback, mass-conservation audits across arbitrary time windows, and clean differentiation through transport closures).

---

## 3. Literate Replacements for PyRate (`holonomy.macroevo`)

PyRate exhibited critical failure modes in macroevolutionary analysis:
1. **In-place buffer mutation**: Destroyed historical likelihood states during MCMC random walks.
2. **Artificial rate-shift artifacts**: Trans-dimensional jump proposals drifted into unidentifiable parameter regimes without calculating actual likelihood gradients.
3. **Zero-length branch singularities**: Polytomies with machine-epsilon branch lengths ($\epsilon < 10^{-6}$ Myr) exploded tip diversification rates by $10^{11}$.

`holonomy.macroevo` provides deterministic, pure functional mathematical replacements:

| Capability | Module / Function | Mathematical Formulation | Advantage over PyRate |
|---|---|---|---|
| **Diversity Hazard** | `primitives.log_diversity_hazard` | $\ln \lambda(D) = \ln \lambda_0 + G_l D$ | Clamped numerical stability; zero floating-point overflow. |
| **Preservation Conditioning** | `primitives.log_keiding_conditioning` | $\ln [1 - \exp(-q \Delta t)] = \ln(-\text{expm1}(-q \Delta t))$ | Keiding (1975) preservation conditioning; no cancellation at small $\Delta t$. |
| **Poisson Occurrences** | `primitives.log_poisson_occurrences` | $\ln P(k \mid \Delta t, q) = k \ln(q \Delta t) - q \Delta t - \ln(k!)$ | Pure functional, closed-form Poisson likelihood. |
| **Profile Likelihood** | `diversity_surface.compute_profile_likelihood_surface` | $\mathcal{L}(G_l) = \max_{\lambda_0} \ln L(\lambda_0, G_l \mid \text{LTT})$ | Direct profile likelihood curve; exact $\chi^2$ likelihood-ratio test replacing drifting MCMC. |
| **Master Equation** | `master_equation.solve_master_equation` | $\frac{d\mathbf{P}}{dt} = \mathbf{Q} \mathbf{P}$ | Exact continuous-time Markov cladogenesis (Etienne 2012); no empirical simulations. |
| **Tip DR Auditing** | `phylogenetic_dr.audit_tree_diversification_rates` | $\text{DR}_i = \left(\sum_j l_j 2^{-(j-1)}\right)^{-1}$ | Detects machine-epsilon polytomy artifacts; regularized inverse branch lengths. |
| **Joint Likelihood** | `joint_likelihood.compute_joint_taphonomic_likelihood` | $\ln L_{\text{joint}} = \sum_i [\ln f_{\text{ext}} + \ln P_{\text{occ}} - \ln P_{\text{obs}} + \ln \lambda]$ | Unified taphonomic + diversification likelihood without sample discarding. |

---

## 4. Usage Example

```python
import numpy as np
from phosphene.holonomy import Connection, Loop, Manifold, Trace
from phosphene.holonomy.macroevo import (
    DiversityTrajectory,
    compute_profile_likelihood_surface,
)

# 1. Morphodynamic Holonomy
x = np.linspace(0, 1000, 21)
y = np.linspace(0, 500, 11)
elevation = np.zeros((11, 21))
manifold = Manifold.from_grid(x, y, elevation)

loop = Loop.sinusoidal_tide(manifold, period=43200.0, num_steps=24)
conn = Connection(porosity=0.4)
trace = Trace(manifold.initial_state())

defect = trace.traverse(loop, conn)
print("Morphological Holonomy Norm:", defect.norm)
print("Mass conservation residual:", trace.mass_conservation_audit(0, -1))

# 2. Deterministic Diversity-Dependence (Replacing PyRate)
traj = DiversityTrajectory(
    time_bins_myr=np.array([4.0, 3.0, 2.0, 1.0, 0.0]),
    standing_diversity=np.array([2.0, 4.0, 6.0, 8.0]),
    speciation_events=np.array([1, 2, 1, 0]),
)
surface = compute_profile_likelihood_surface(traj)
print(f"Best G_l: {surface.best_g_l:.4f}, LR statistic: {surface.likelihood_ratio:.3f}, p-value: {surface.p_value:.4f}")
```
