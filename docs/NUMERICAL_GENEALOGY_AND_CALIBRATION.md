# Primitives, Python Numerical Genealogy, and Hypothesis Calibration in holonomy

## 1. Decomposing holonomy into Legible Primitives

`holonomy` models path-dependent dynamical systems where traversing a trajectory $\gamma(t) : [0, T] \to \mathcal{C}$ through control space leaves a path-dependent residual displacement:

$$\Delta \mathcal{M} = \oint_\gamma \partial_t \mathcal{M} \, dt \neq 0$$

To keep numerical modeling transparent, testable, and accessible to scientists working with datasets of any size, `holonomy` decomposes every solver into six pure, immutable primitives in `holonomy.core`:

1. **`State` (Immutable Configuration Value):**
 Holds the current coordinate, discrete index, probability or density vector `P`, and accumulated log-evidence `lnL`. Every array buffer enforces `flags.writeable = False` at construction so past states can never be mutated in place.
2. **`ControlLoop` / `ForcingField` (External Schedule):**
 Defines the discrete or continuous path through control space (for example, observed branching times $t_1 > t_2 > \dots > t_s > 0$, tidal forcing cycles, or mechanical load schedules).
3. **`CapacityEdge` (Explicit Boundary Value Object):**
 Separates physical or ecological ceiling constraints ($S \le K$) from linear algebra, exposing $\text{headroom} = K - k$ and discrete regime labels (`interior_radiation`, `boundary_grazing`, `saturated_ceiling`) as inspectable data.
4. **`TransferClosure` (Constitutive Rate Operator):**
 Pure mapping `(State, ForcingField, CapacityEdge) -> Generator` that produces instantaneous flux vectors or tridiagonal transition matrices without executing time integration.
5. **`next_state` (Single-Step Integrator / Update Rule):**
 Pure transition `(State, dt, TransferClosure) -> State` advancing the system across one continuous interval or one discrete observation event.
6. **`EvolutionTrace` and `HolonomyDefect` (Append-Only Lineage and Path Residue):**
 Records every immutable `State` as an ordered tuple supporting zero-loss rollback, mass conservation checks, and explicit non-abelian commutator measurement.

### Cross-Dialect Uniformity

Every scientific dialect in `holonomy` instantiates these exact same six primitives:

| holonomy.core Primitive | holonomy.macroevo (Branching) | holonomy.geomorph (Sediment) | holonomy.morphometrics (Form) |
| :--- | :--- | :--- | :--- |
| `State` (`writeable=False`) | Unobserved-lineage vector `P(n)` + `lnL` | Bathymetric `Bed` elevation $\eta$ | Kendall `Configuration` landmarks |
| `ControlLoop` | Observed split schedule $t_1 > \dots > t_s$ | Cyclic tidal/flood `Flow` shear | Cyclic mechanical load schedule |
| `CapacityEdge` | Niche ceiling $K - k$ headroom | Critical Shields shear threshold | Ontogenetic growth limit |
| `TransferClosure` | Tridiagonal Metzler matrix $\mathbf{M}_k$ | `meyer_peter_muller` sediment flux | `allometric_growth_closure` |
| `next_state` | Interval propagation & split update | `exner.next_bed` conservation step | Differential growth step |
| `HolonomyDefect` | $[\text{flow}(dt), \text{observe\_split}]$ residue | Cyclic topographic hysteresis | Permanent skeletal divergence |

---

## 2. Standard Python Numerical Genealogy and the Scientist's Escalation Ladder

Scientists rarely start with massive, high-resolution datasets. When a dataset contains only a handful of taxa, short time windows, or sparse measurements, launching directly into stiff matrix exponentials (`scipy.linalg.expm`) or nonlinear capacity-coupled PDEs risks overfitting noise and obscuring simple explanations behind opaque numerical machinery.

Instead, `holonomy` organizes its numerical primitives along the standard genealogy of scientific Python (`math` $\to$ `numpy` $\to$ `scipy.linalg` $\to$ `holonomy.core`). Each higher rung must collapse identically onto the rung below it when coupling parameters are turned off.

### Rung 0: Scalar Closed-Form Primitives (`math` Standard Library)

* **Python stack:** `math.exp`, `math.log`, `math.log1p`, `math.fsum`. Zero arrays, zero matrices, zero truncation buffers.
* **Mathematical structure:** Uncoupled scalar processes where rates depend only on known time spans `dt` and fixed baseline rates (`lam0`, `mu0`):
  * Pure-death decay (`lam0 = 0`): $\ln P_0(t) = -k \cdot \mu_0 \cdot t$.
  * Constant-rate linear birth-death ($K \to \infty$, Nee-May-Harvey closed form):
    $$p_1(t) = \frac{r^2 e^{-rt}}{(\lambda_0 - \mu_0 e^{-rt})^2}, \quad \text{where } r = \lambda_0 - \mu_0$$
* **When to use:** Always run Rung 0 first as the baseline hypothesis. On small datasets, Rung 0 often captures all statistically identifiable signal without introducing ceiling or grid hyperparameters.

### Rung 1: Discrete Vector and Quadrature Primitives (`numpy` 1D Arrays)

* **Python stack:** `numpy.ndarray` (`flags.writeable = False`), `np.arange`, `np.cumsum`, `np.dot`.
* **Mathematical structure:** Discretizes an unobserved state coordinate $j = 0, 1, \dots, n_{\max}$ onto a finite 1D grid, evaluating rate vectors `lam_vec` and explicit small-step updates ($P + dt \cdot (\mathbf{M}_k P)$) or discrete Poisson/Euler convolutions.
* **Genealogical link to Rung 0:** When $n_{\max} = 0$ and $\lambda_0 = 0$, Rung 1 reduces to a 1-element array $[e^{-k \cdot \mu_0 \cdot dt}]$ matching Rung 0 to machine precision.

### Rung 2: Coupled Linear Semigroup Primitives (`scipy.linalg` / `scipy.sparse.linalg`)

* **Python stack:** `scipy.linalg.expm` (scaling-and-squaring Padé), `scipy.sparse.linalg.expm_multiply` (Krylov subspace), and Jensen's Uniformization (`scipy.stats.poisson` + non-negative matrix-vector products).
* **Mathematical structure:** Solves the coupled linear system $\frac{dP}{dt} = \mathbf{M}_k P$ across adjacent states $j - 1, j, j + 1$ over arbitrary step sizes $dt$.
* **Genealogical link to Rungs 0 and 1:**
  * When $K \to \infty$, multi-step Rung 2 propagation reproduces Rung 0's closed-form Nee-May-Harvey log-likelihood.
  * For any finite $K$, Rung 2 Padé and Krylov solvers are calibrated against Jensen's Uniformization (a strictly non-negative Rung 1/2 series expansion) to bound rounding drift in stiff regimes ($\gamma \cdot dt \gg 1$).

### Rung 3: Nonlinear Capacity-Bounded & Non-Abelian Path Primitives (`holonomy.core`)

* **Python stack:** `CapacityEdge`, `step_interval`, `step_cladogenetic_split`, `EvolutionTrace`, `HolonomyDefect`.
* **Mathematical structure:** Couples state-dependent throttling ($\lambda(k + j) = \max(0, \lambda_0 (1 - (k + j) / K))$) with interleaved continuous flow and discrete observation events along a non-abelian control path.
* **Genealogical link to Rung 2:** As $\text{headroom} = K - k \to \infty$, the commutator defect $[\text{flow}(dt), \text{observe\_split}]$ shrinks smoothly toward the density-independent Rung 2 limit.

### The Scientist's Escalation Ladder

To let researchers decide rationally whether higher-level mathematics improves their model, `holonomy` pairs every Rung 3 evaluation with a **Rung 0 Baseline Escalation Report**:

1. Evaluate the dataset at **Rung 0** (uncoupled scalar closed form).
2. Evaluate the dataset at **Rung 3** (capacity-bounded matrix semigroup).
3. Inspect the **Escalation Gain** $\Delta \ln L = \ln L_{\text{rung3}} - \ln L_{\text{rung0}}$ alongside `CapacityEdge.regime`:
  * If $|\Delta \ln L| < \text{threshold}$ (for instance, $< 0.5$ log-likelihood units on a small 3-to-5 taxon tree), the dataset lacks power to distinguish finite carrying capacity from unbounded growth; the scientist should report the simpler Rung 0 model.
  * If $\Delta \ln L$ is significant and `CapacityEdge.regime` enters `boundary_grazing` or `saturated_ceiling`, escalating to Rung 3 is empirically justified.
