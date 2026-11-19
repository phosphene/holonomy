# Pytest and Hypothesis Patterns and Anti-Patterns for Scientific Algebraic Dynamics

## 1. Strategy and Input Geometry Patterns

### Pattern 1.1: Constructive Manifold and Cone Parameterization

* **Principle:** Sample unconstrained coordinates in a tangent space, Lie algebra, or factor space and map them deterministically onto the target algebraic manifold, group, or cone.

* **Mechanism:** Algebraic varieties (orthogonal groups `O(n)`, special orthogonal groups `SO(n)`, symmetric positive-definite cones, Metzler transition generators, simplex probability vectors) have Lebesgue measure zero inside ambient Euclidean space `R^(n x n)`. Constructive maps such as skew-symmetrization `A = 0.5 * (X - X^T)` followed by Cayley or matrix-exponential projection, Cholesky factors `L @ D @ L^T`, or positive waiting-time cumulative sums concentrate 100% of Hypothesis examples on valid algebraic objects.

* **Idiom:**

  ```
  @st.composite
  def descending_event_schedule(draw, min_events=2, max_events=8):
      n = draw(st.integers(min_value=min_events, max_value=max_events))
      deltas = draw(
          st.lists(
              st.floats(
                  min_value=0.05,
                  max_value=2.5,
                  allow_nan=False,
                  allow_infinity=False,
                  allow_subnormal=False,
              ),
              min_size=n,
              max_size=n,
          )
      )
      # Reverse cumulative sum guarantees t_1 > t_2 > ... > t_n > 0 for every draw and shrink
      return tuple(np.cumsum(deltas)[::-1].tolist())
  
  ```

### Pattern 1.2: Boundary-Relative Parameterization for Shrinker Continuity

* **Principle:** Parameterize critical domain thresholds relative to the active algebraic or physical boundary rather than drawing independent absolute values.

* **Mechanism:** Hypothesis shrinks failing test cases by reducing underlying byte choices toward zero. When a phase transition or saturation boundary occurs at `K = k_max`, drawing `headroom = K - k_max` directly allows the shrinker to slide a failing input smoothly onto `headroom = 0.0`, isolating the exact threshold where behavior changes.

* **Idiom:**

  ```
  @st.composite
  def capacity_bounded_system(draw, k_observed: int):
      headroom = draw(
          st.floats(
              min_value=-2.0,
              max_value=20.0,
              allow_nan=False,
              allow_infinity=False,
              allow_subnormal=False,
          )
      )
      capacity_K = float(k_observed) + headroom
      return capacity_K, headroom
  
  ```

### Pattern 1.3: Strict IEEE-754 Finite-Domain Hygiene

* **Principle:** Explicitly disable `NaN`, `infinity`, and IEEE-754 subnormal floats in algebraic and dynamical strategies, testing extended-real edge cases in dedicated boundary tests.

* **Mechanism:** Leaving `allow_nan=True`, `allow_infinity=True`, or `allow_subnormal=True` active embeds an algebraic field inside the extended real lattice `R union {-inf, +inf, NaN}`. Because `NaN` is absorbing and `1.0 / subnormal` overflows to `inf`, Hypothesis's shrinker collapses genuine algorithmic cancellation bugs into trivial `[inf, -inf]` or `1e-323` underflow counterexamples.

### Pattern 1.4: Shrink-Monotonic Composite Generators

* **Principle:** Keep `@st.composite` generators deterministic, free of internal PRNG reseeding, and monotonic with respect to Hypothesis's choice sequence.

* **Mechanism:** Hypothesis simplifies counterexamples by making small edits to its internal choice buffer. If a composite strategy uses hash-based branching, external random seeds, or non-monotonic array reshaping, small byte edits cause erratic jumps in matrix dimension or condition number, defeating shrinking.

### Pattern 1.5: Common Random Numbers (Quantile Coupling) for Statistical Estimators

* **Principle:** When testing statistical estimators, Monte Carlo likelihoods, or stochastic differential integrators, draw uniform quantiles `u in (0, 1)` via Hypothesis and push them through deterministic inverse-CDFs or fixed basis transformations.

* **Mechanism:** Coupling random draws to Hypothesis-controlled uniform quantiles makes stochastic noise deterministic and shrinkable. When a statistical estimator exhibits bias or variance blow-up, Hypothesis shrinks the quantile vector toward canonical uniform spacing, exposing the exact sample configuration causing estimator failure.

## 2. Oracle and Algebraic Invariant Patterns

### Pattern 2.1: Genealogical Rung-to-Rung Oracle Sandwiching

* **Principle:** Calibrate every numerical solver against a hierarchy of simpler, exact base cases obtained by turning off coupling terms or taking asymptotic limits.

* **Mechanism:** High-order numerical integrators (`scipy.linalg.expm`, Krylov subspace solvers, nonlinear PDE steppers) should never be tested only against loose sanity bounds. Sandwich each solver between:

  1. **Scalar closed-form limits** (e.g., `lam0 = 0` pure decay `exp(-k * mu0 * dt)`, or `K -> inf` analytical constant-rate birth-death likelihood).

  2. **Unconditionally stable low-order oracles** (e.g., Jensen's Uniformization using strictly non-negative Poisson-weighted matrix powers, or arbitrary-precision `mpmath` arithmetic).

### Pattern 2.2: Vertex-Seam Continuity and Limit-Commutativity Probes

* **Principle:** Write dedicated `@given` tests that cross discrete regime boundaries ("vertices") where a solver changes how it interprets or updates state, asserting continuity or known jump conditions across the seam.

* **Mechanism:** Bugs cluster at vertices where solver branches switch: `dt -> 0+`, `headroom = K - k -> 0+` vs `0-`, `rate -> 0+`, or `K -> inf`. Probing `x_vertex - eps` and `x_vertex + eps` for `eps in [1e-8, 1e-2]` verifies Lipschitz continuity of continuous flows and clean handling of zero-evidence boundary events without `0 / 0 -> NaN` artifacts.

### Pattern 2.3: Semigroup Composition vs. Non-Abelian Commutator Auditing

* **Principle:** Separate autonomous semigroup intervals (where time-splitting must commute) from non-commuting control sequences (where path order produces genuine holonomy).

* **Mechanism:**

  * On a constant-parameter interval, assert Chapman-Kolmogorov semigroup consistency:
    `|| propagate(M, P, dt1 + dt2) - propagate(M, propagate(M, P, dt1), dt2) ||_1 <= tol`

  * Across non-commuting operators (continuous flow `exp(M * dt)` vs. discrete observation weighting `diag(lam)`), explicitly measure the commutator residual `|| flow(dt) o observe - observe o flow(dt) ||_1` and verify it vanishes in the abelian limit (`K -> inf`).

### Pattern 2.4: Exact Conservation and Positivity Invariant Auditing

* **Principle:** Audit algebraic conservation laws (unnormalized probability mass decay `sum(P) == exp(-k * mu0 * dt)`, trace, determinant, symmetry) and Metzler/cone non-negativity (`min(P) >= -tol`) directly on raw solver outputs.

* **Mechanism:** Entrywise negativity in a Metzler semigroup or drift in total surviving mass is a direct, coordinate-free diagnostic of rational Pade overshoot or state-space tail truncation.

### Pattern 2.5: Statistical Score-Function and Likelihood-Ratio Calibration

* **Principle:** Calibrate statistical likelihood and inference engines using exact differential and order-theoretic identities rather than noisy point-estimate checks.

* **Mechanism:**

  * **Zero-Expectation Score Identity:** At the true data-generating parameter `theta_0`, the empirical average gradient of the log-likelihood across synthetic datasets satisfies `E[grad_theta ln L(theta_0; X)] == 0`.

  * **Profile Likelihood Dominance:** Maximizing over a nuisance parameter must always yield `ln L_profile(psi) >= ln L(psi, nuisance_fixed)`.

  * **Nesting Collapse:** At nested parameter boundaries (e.g., `K -> inf`), the constrained model log-likelihood must equal the null model log-likelihood within calibrated numerical tolerance.

## 3. Telemetry, Adaptive Search, and Pytest Integration Patterns

### Pattern 3.1: Variational Defect Maximization via `hypothesis.target()`

* **Principle:** Formulate every algebraic axiom, conservation law, and oracle discrepancy as a continuous non-negative residual functional `delta(x) >= 0` and pass it to `hypothesis.target(delta, label=...)`.

* **Mechanism:** Binary assertions (`assert err < tol`) treat all passing inputs as equally uninformative. Feeding `delta(x)` into `target()` transforms Hypothesis's evolutionary mutator into a gradient-free optimizer that climbs toward the worst-case numerical distortion in the parameter domain.

* **Idiom:**

  ```
  l1_defect = float(np.linalg.norm(p_oracle - p_solver, ord=1))
  negativity_overshoot = float(max(0.0, -np.min(p_solver)))
  target(l1_defect, label="solver_vs_oracle_l1_defect")
  target(negativity_overshoot, label="metzler_negativity_overshoot")
  assert negativity_overshoot <= 1e-13
  assert l1_defect <= 1e-11 * max(1.0, stiffness)
  
  ```

### Pattern 3.2: Regime Stratification via `hypothesis.event()`

* **Principle:** Emit discrete categorical tags via `hypothesis.event()` for stiffness decades, condition-number orders of magnitude, and regime classifications, and run pytest with `--hypothesis-show-statistics`.

* **Mechanism:** Statistical telemetry confirms that the test suite actually exercises ill-conditioned corners (`stiffness_decade=2`, `regime=boundary_grazing`) rather than spending its entire budget in benign interior regimes.

### Pattern 3.3: Condition-Coupled and Stiffness-Scaled Error Budgets

* **Principle:** Parameterize acceptance tolerances by local condition number `kappa(x)`, matrix dimension `n`, stiffness `||M|| * dt`, and unit roundoff `u`.

* **Mechanism:** Backward-stable numerical algorithms guarantee error bounds of the form `||f_num(x) - f_exact(x)|| <= c * u * kappa(x) * ||f_exact(x)||`. Coupling assertions to `kappa(x)` or stiffness prevents false failures at high condition numbers while keeping bounds tight at low condition numbers.

### Pattern 3.4: Read-Only Buffer Enforcement (`flags.writeable = False`)

* **Principle:** Mark all NumPy arrays inside immutable state objects as read-only (`arr.flags.writeable = False`) upon construction.

* **Mechanism:** Hypothesis replays and shrinks failing test cases repeatedly inside the same process. Read-only buffers raise `ValueError` immediately if any solver step or test helper mutates an array in place, preventing subtle state corruption across shrink attempts.

### Pattern 3.5: Solver-Backend Parameterization via `pytest.fixture`

* **Principle:** Expose numerical backends (scalar closed-form, dense Pade `expm`, sparse Krylov `expm_multiply`, arbitrary-precision reference) via a parameterized `@pytest.fixture(params=[...])`.

* **Mechanism:** Every algebraic invariant, vertex-seam check, and oracle comparison runs automatically across all numerical implementations without duplicating test code.

### Pattern 3.6: Stateful Trajectory and Rollback Machines (`RuleBasedStateMachine`)

* **Principle:** Model iterative time-stepping, discrete observation conditioning, and historical state rollbacks as `@rule` transitions in a `RuleBasedStateMachine` with `@invariant` checks after every step.

* **Mechanism:** Stateful testing uncovers cumulative drift, underflow accumulation, and path-dependent hysteresis across arbitrary interleavings of continuous and discrete steps that single-step property tests miss.

### Pattern 3.7: Witness Promotion via `@example` and Hypothesis Profiles

* **Principle:** Promote worst-case counterexamples discovered by `target()` into explicit `@example(...)` decorators, and configure `settings.register_profile(...)` for fast CI vs. deep nightly calibration runs.

* **Mechanism:** `@example` guarantees deterministic regression gating on known stiff or near-singular witnesses in every CI run, while profiles allow deep `max_examples=2000` variational searches during numerical calibration.

## 4. Anti-Patterns in Strategy and Input Generation

### Anti-Pattern 4.1: Rejection-Filtering Zero-Measure Varieties (`assume()`)

* **Failure Mode:** Generating dense random matrices or unsorted vectors and gating them with `assume(is_orthogonal(M))` or `assume(t_1 > t_2 > t_3)`.

* **Consequence:** Zero-measure algebraic constraints fail nearly 100% of random draws, triggering `HealthCheck.filter_too_much` and biasing surviving samples toward trivial zero-filled matrices.

### Anti-Pattern 4.2: Unguarded Extended-Real Pollution (`NaN`, `inf`, Subnormals)

* **Failure Mode:** Using default `st.floats()` without setting `allow_nan=False, allow_infinity=False, allow_subnormal=False`.

* **Consequence:** Hypothesis shrinks every numerical failure to `[inf, -inf]` or gradual-underflow subnormals (`5e-324`), masking genuine finite-precision cancellation and conditioning bugs.

### Anti-Pattern 4.3: Non-Monotonic Black-Box Generators That Sever Shrinker Locality

* **Failure Mode:** Calling `np.random.seed(...)`, hash-based branching, or discontinuous rejections inside `@st.composite`.

* **Consequence:** Small mutations to Hypothesis's byte stream cause erratic jumps in generated objects, preventing the shrinker from reducing a large failing matrix or tree into a minimal canonical witness.

### Anti-Pattern 4.4: Uncontrolled Internal PRNG State Inside Statistical Property Tests

* **Failure Mode:** Allowing a statistical simulator or likelihood estimator to sample from unseeded global `np.random` inside a `@given` test.

* **Consequence:** Failures become flaky and non-reproducible during Hypothesis shrinking (`Flaky` health check error), making it impossible to isolate bad parameter regimes from unlucky random draws.

## 5. Anti-Patterns in Assertions, Oracles, and Tolerances

### Anti-Pattern 5.1: Black-Box End-to-End Fuzzing Without Primitive Oracles

* **Failure Mode:** Passing random parameter tuples into a full multi-stage solver and asserting only `np.isfinite(lnL)`.

* **Consequence:** Conflates grid truncation error, linear-algebra stiffness, and boundary saturation into a single opaque scalar, providing no diagnostic signal when an assertion fails.

### Anti-Pattern 5.2: Bit-Exact Equality (`==`) on Non-Associative Floating-Point Reductions

* **Failure Mode:** Asserting `lhs == rhs` between two algebraically equivalent linear-algebra expressions evaluated in different summation or blocking orders.

* **Consequence:** IEEE-754 floating-point addition is non-associative (`(a + b) + c != a + (b + c)`), causing predictable ULP differences to masquerade as algorithmic bugs.

### Anti-Pattern 5.3: Uniform Static Epsilon Across Multi-Decade Scales and Stiffness Regimes

* **Failure Mode:** Using a single hard-coded tolerance `atol=1e-12` across inputs spanning `1e-12` to `1e12` or stiffness decades `1e-4` to `1e4`.

* **Consequence:** Flags harmless ULP quantization noise on large/stiff inputs as failures while letting complete precision loss on tiny/ill-conditioned inputs pass silently.

### Anti-Pattern 5.4: Silent Post-Step Renormalization That Hides Mass Leakage

* **Failure Mode:** Dividing a propagated probability or density vector by `np.sum(P)` inside the solver or test harness before checking conservation laws.

* **Consequence:** Erases the exact conservation diagnostic (`sum(P) == exp(-k * mu0 * dt)`) that detects probability mass escaping across an undersized truncation boundary `n_max`.

### Anti-Pattern 5.5: Conflating Scientific Model Falsification with Numerical Bugs

* **Failure Mode:** Treating `ln L = -inf` at an impossible parameter boundary (such as an observed split when standing richness already equals carrying capacity `K <= k`) as a numerical crash.

* **Consequence:** Blurs exact mathematical predictions of the scientific hypothesis with floating-point underflow defects. Boundary impossibilities must be represented as explicit, typed regime states.

### Anti-Pattern 5.6: Uncalibrated Statistical P-Value Flakiness in Stochastic Tests

* **Failure Mode:** Running a fixed-seed chi-square or Kolmogorov-Smirnov test with `alpha = 0.05` across 200 Hypothesis examples without adjusting significance thresholds or coupling quantiles.

* **Consequence:** By elementary probability (`1 - 0.95^200 ~= 0.99996`), a completely bug-free statistical implementation will fail almost every pytest run due to expected Type I false positives.

## 6. Anti-Patterns in Pytest Fixture and Execution Architecture

### Anti-Pattern 6.1: Mutable Shared Fixtures Across Hypothesis Shrink Iterations

* **Failure Mode:** Passing a mutable NumPy array or stateful solver cache from a `pytest.fixture` into a `@given` test function and mutating it in place.

* **Consequence:** Subsequent Hypothesis iterations and shrink steps operate on corrupted state from earlier runs, producing order-dependent failures that disappear when re-run in isolation.

### Anti-Pattern 6.2: Hard-Coded Random Seeds That Mask Multi-Regime Defects

* **Failure Mode:** Replacing Hypothesis property tests with a single fixed `np.random.seed(42)` unit test.

* **Consequence:** Tests only one arbitrary point in parameter space, missing stiff corners, near-singular matrices, and boundary seams that adaptive search uncovers immediately.

### Anti-Pattern 6.3: Coupling Heavy Matrix Solvers Inside Strategy Generation

* **Failure Mode:** Calling `scipy.linalg.expm` or solving linear systems inside `@st.composite` just to filter or construct test inputs.

* **Consequence:** Multiplies test generation overhead across thousands of Hypothesis draws and shrink steps, starving the search budget and slowing CI feedback loops.