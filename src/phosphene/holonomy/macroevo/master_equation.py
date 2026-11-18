"""Continuous-time Master Equation solver for Diversity-Dependent Diversification (Etienne 2012).

Solves the exact continuous-time Markov master equation P(n, t) for cladogenesis
under carrying-capacity saturation:
    lambda(n) = max(0, lambda_0 * (1 - n/K))
    mu(n) = mu_0

Replaces random-walk MCMC approximations with exact matrix exponential and ODE integration.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class MasterEquationParams:
    """Parameters for Diversity-Dependent cladogenesis."""

    lambda0: float  # Baseline speciation rate
    mu0: float      # Baseline extinction rate
    K: float        # Clade carrying capacity
    max_richness: int = 50

    def __post_init__(self) -> None:
        if self.lambda0 <= 0.0:
            raise ValueError(f"lambda0 must be > 0.0, got {self.lambda0}")
        if self.mu0 < 0.0:
            raise ValueError(f"mu0 must be >= 0.0, got {self.mu0}")
        if self.K <= 0.0:
            raise ValueError(f"Carrying capacity K must be > 0.0, got {self.K}")


def construct_transition_matrix(params: MasterEquationParams) -> np.ndarray:
    """Build tridiagonal transition rate matrix Q for master equation dP/dt = Q * P.

    State space: n in [0, max_richness]
    Transition rates:
      n -> n + 1: lambda(n) * n
      n -> n - 1: mu(n) * n
    """
    N = params.max_richness + 1
    Q = np.zeros((N, N), dtype=np.float64)

    for n in range(N):
        # Speciation transition: n -> n + 1
        if n < params.max_richness and n > 0:
            lam_n = max(0.0, params.lambda0 * (1.0 - n / params.K))
            rate_up = lam_n * n
            Q[n + 1, n] += rate_up
            Q[n, n] -= rate_up

        # Extinction transition: n -> n - 1
        if n > 0:
            rate_down = params.mu0 * n
            Q[n - 1, n] += rate_down
            Q[n, n] -= rate_down

    return Q


def solve_master_equation(
    params: MasterEquationParams,
    initial_richness: int = 1,
    time_span: float = 10.0,
    num_eval_points: int = 101,
) -> Tuple[np.ndarray, np.ndarray]:
    """Integrate dP/dt = Q * P from t=0 to time_span.

    Returns:
        times: (T,) array of time points
        probabilities: (max_richness + 1, T) array of state probabilities
    """
    Q = construct_transition_matrix(params)
    N = params.max_richness + 1

    P0 = np.zeros(N, dtype=np.float64)
    P0[initial_richness] = 1.0

    def rhs(t: float, P: np.ndarray) -> np.ndarray:
        return Q @ P

    t_eval = np.linspace(0.0, time_span, num_eval_points)
    sol = solve_ivp(rhs, (0.0, time_span), P0, t_eval=t_eval, method="RK45")

    return sol.t, sol.y
