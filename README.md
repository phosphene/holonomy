# phosphene-holonomy

Differential-geometric, data-preserving, and macroevolutionary diversification primitives. Replaces legacy MCMC tools (such as PyRate) with deterministic profile likelihoods, continuous-time Markov master equations, and data-preserving geometry.

## Literate Specification & Architecture
See full literate specification in [`docs/LITERATE_SPECIFICATION.md`](docs/LITERATE_SPECIFICATION.md).

## Morphodynamic Primitives

- `holonomy.Manifold`: Immutable reference bathymetry $\mathcal{M}_0$ and spatial discretization. Held strictly read-only so baseline coordinate grids survive every run intact.
- `holonomy.Connection`: Pure sediment-flux differential operator $-\nabla \cdot \mathbf{q}_s$, dictating how boundary shear stress shifts mass between neighboring cells without mutating shared arrays.
- `holonomy.Loop`: Parameterized trajectory of hydrodynamic boundary conditions (tidal cycles, storm hydrographs, wave climates).
- `holonomy.Defect`: Net morphological displacement $\Delta \eta = \oint \partial_t \eta \, dt$ contrasting initial and final states after traversing a forcing cycle.
- `SurfaceState`: Immutable state container pairing an elevation field $\eta$ with a zero-copy reference to the static coordinate manifold $\mathcal{M}_0$. Advancing the Exner equation returns a freshly allocated elevation field.
- `holonomy.Trace`: Chaining steps along a `Loop` records a directed lineage of immutable snapshots, enabling instant rollback, mass-conservation audits across arbitrary time windows, and clean gradient tracking.

## Macroevolutionary Suite (`holonomy.macroevo` — PyRate Replacements)

Deterministic, pure functional replacements for PyRate's empirical MCMC sampler:
- `holonomy.macroevo.compute_profile_likelihood_surface`: Exact profile likelihoods $\mathcal{L}(G_l)$ and likelihood-ratio hypothesis testing over LTT curves.
- `holonomy.macroevo.solve_master_equation`: Continuous-time Markov master equation solver (Etienne 2012) for diversity-dependent cladogenesis.
- `holonomy.macroevo.audit_tree_diversification_rates`: Regularized Jetz et al. (2012) Tip Diversification Rates (DR) with zero-length branch singularity diagnostics.
- `holonomy.macroevo.compute_joint_taphonomic_likelihood`: Taphonomically conditioned joint likelihood with Keiding (1975) observation conditioning.
