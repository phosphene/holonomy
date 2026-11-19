# holonomy: Literate Specification and Architectural Mapping

`holonomy` is the canonical Phosphene Python package for path-dependent dynamical systems, non-abelian hysteresis, and geometric state preservation.

---

## 1. Mapping the Universal Mathematical Pipeline to Core Primitives

```
                           [ControlLoop]
                     Parameterized Control Path:
                         γ(t): [0, T] → C
                               │
                               ▼
   Manifold M₀ ──────────────────────────────► HolonomyDefect ΔM
 (Immutable State,                          (Net Geometric Residual,
  read-only arrays)                           exact displacement)
                               ▲
                               │
                       [TransferClosure]
                       Rate/Flux Operator: J
                      Continuity: next_state
```

The universal core (`holonomy.core`) provides the generic foundation:

- **`Manifold` & `State`**: Immutable spatial configurations, coordinate meshes, or abstract state tensors ($\mathcal{M}_0$). Array buffers are strictly read-only (`flags.writeable = False`), ensuring baseline coordinate surfaces survive execution intact without memory corruption.
- **`ControlLoop` & `ForcingField`**: Parameterized trajectories in control space ($\gamma(t)$) traversing closed cycles where $\mathcal{F}(0) = \mathcal{F}(T)$.
- **`TransferClosure` & `compute_flux_divergence`**: Pure constitutive rate or flux operators mapping state and forcing to transport fields $(\mathcal{M}, \mathcal{F}) \mapsto \mathbf{J}$.
- **`next_state`**: Generalized continuity integration advancing state values in time:
  $$\partial_t \mathcal{M} = -\mathcal{D}(\mathbf{J})$$
- **`EvolutionTrace` & `HolonomyDefect`**: Ordered, append-only lineage of immutable states along a control loop. Calculates the exact closed-loop path residue:
  $$\Delta \mathcal{M} = \oint_\gamma \partial_t \mathcal{M} \, dt = \mathcal{M}(T) - \mathcal{M}(0) \neq 0$$
  A non-vanishing norm $\|\Delta \mathcal{M}\| > 0$ directly measures dissipative hysteresis (irreversible structural work performed on the system).

---

## 2. Trajectory Preservation by Definition

Scientific computing software often suffers from destructive in-place mutations (overwriting arrays during time-stepping). Because **holonomy is an invariant of an entire path rather than an isolated time step**, the package elevates data preservation from a coding habit into an architectural requirement:

1. **Immutable State Transitions**: State advance operations allocate new value buffers while maintaining zero-copy references to static coordinate manifolds.
2. **Explicit Lineage Graphs**: Chaining steps along an `EvolutionTrace` maintains a directed lineage of snapshots, enabling instant historical rollback, mass-conservation audits across arbitrary time windows, and clean algorithmic differentiation.

---

## 3. Domain Specialization Dialects

The generalized mathematical kernel is specialized into domain dialects that provide natural language entry points native to each scientific literature:

### A. Geomorphology (`holonomy.geomorph`)
Maps the core abstractions to coastal and fluvial sediment transport:
- **`Bed`**: Bathymetric elevation surface $\eta(\mathbf{x})$, bed slopes, and active-layer sediment stratigraphy.
- **`Flow`**: Hydrodynamic forcing fields (velocity $\mathbf{u}$, boundary shear stress $\boldsymbol{\tau}_b$).
- **`flux.meyer_peter_muller`**: Solid sediment transport rate $\mathbf{q}_s$ as a function of excess boundary shear stress.
- **`exner.next_bed`**: Exner sediment mass conservation:
  $$\partial_t \eta = -\frac{1}{1 - p} \nabla \cdot \mathbf{q}_s$$
- **`exner.holonomy_defect`**: Closed-loop bathymetric displacement across tidal, flood, or storm hydrographs.

### B. Morphometrics (`holonomy.morphometrics`)
Maps the core abstractions to skeletal morphogenesis and anatomical deformation:
- **`Configuration`**: 3D landmark configurations and centroid sizes in Kendall shape space.
- **`allometric_growth_closure`**: Differential growth tensors driven by ontogenetic stress gradients.
- **`remodeling.ontogenetic_trace`**: Lineage of anatomical forms under cyclic functional loading.
- **`remodeling.morphological_defect`**: Permanent skeletal divergence and shape change.

### C. Deterministic Macroevolutionary Suite (`holonomy.macroevo`)
Replaces heuristic, destructive MCMC tools (such as PyRate) with deterministic profile likelihoods and continuous-time Markov models:

| Capability | Module / Function | Mathematical Formulation | Advantage over PyRate |
|---|---|---|---|
| **Diversity Hazard** | `primitives.log_diversity_hazard` | $\ln \lambda(D) = \ln \lambda_0 + G_l D$ | Clamped numerical stability; zero floating-point overflow. |
| **Preservation Conditioning** | `primitives.log_keiding_conditioning` | $\ln [1 - \exp(-q \Delta t)] = \ln(-\text{expm1}(-q \Delta t))$ | Keiding (1975) preservation conditioning; no cancellation at small $\Delta t$. |
| **Poisson Occurrences** | `primitives.log_poisson_occurrences` | $\ln P(k \mid \Delta t, q) = k \ln(q \Delta t) - q \Delta t - \ln(k!)$ | Pure functional, closed-form Poisson likelihood. |
| **Profile Likelihood** | `diversity_surface.compute_profile_likelihood_surface` | $\mathcal{L}(G_l) = \max_{\lambda_0} \ln L(\lambda_0, G_l \mid \text{LTT})$ | Direct profile likelihood curve; exact $\chi^2$ likelihood-ratio test replacing drifting MCMC. |
| **Master Equation** | `master_equation.solve_master_equation` | $\frac{d\mathbf{P}}{dt} = \mathbf{Q} \mathbf{P}$ | Exact continuous-time Markov cladogenesis (Etienne 2012) via matrix exponential (`expm`); no empirical simulations. |
| **Tip DR Auditing** | `phylogenetic_dr.audit_tree_diversification_rates` | $\text{DR}_i = \left(\sum_j l_j 2^{-(j-1)}\right)^{-1}$ | Detects machine-epsilon polytomy artifacts; regularized inverse branch lengths. |
| **Joint Likelihood** | `joint_likelihood.compute_joint_taphonomic_likelihood` | $\ln L_{\text{joint}} = \sum_i [\ln f_{\text{ext}} + \ln P_{\text{occ}} - \ln P_{\text{obs}} + \ln \lambda]$ | Unified taphonomic + diversification likelihood without sample discarding. |
| **Canonical Galapagos** | `galapagos.load_galapagos_csv` | Valente, Phillimore, & Etienne (2015) | Authentic 8-clade insular baseline with verified branching times. |
| **Comparative Metrics** | `comparative_metrics.generate_canonical_comparison` | Cross-domain evaluation | Contrasts bounded island equilibrium with sparse continental taphonomy. |
