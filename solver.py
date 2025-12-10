import numpy as np
from thermo_data import thermo_data

R = 8.314  # J/mol·K
R_kJ = R / 1000  # kJ/mol·K
P0 = 1.0  # standard pressure (bar)


def calculate_reaction_thermo(reaction, T):
    """Calculate ΔH°, ΔS°, ΔG°, K for a reaction at temperature T"""

    ΔH = 0.0  # kJ/mol
    ΔS = 0.0  # kJ/mol·K

    for species, coeff in reaction['stoichiometry'].items():
        if species not in thermo_data:
            raise ValueError(f"{species} missing from thermo_data.py")

        ΔH += coeff * thermo_data[species]["ΔHf"]
        ΔS += coeff * thermo_data[species]["S"] / 1000  # J → kJ

    ΔG = ΔH - T * ΔS
    K = np.exp(-ΔG / (R_kJ * T))

    return ΔH, ΔS, ΔG, K


def solve_equilibrium(reaction, n0, T, P):
    """Solves ξ using Gibbs Free Energy minimization condition (Q = K)
       Also returns total moles and symbolic extent expressions
    """

    species = list(reaction["stoichiometry"].keys())
    nu = np.array([reaction["stoichiometry"][s] for s in species], dtype=float)
    n0_arr = np.array([n0.get(s, 0.0) for s in species], dtype=float)

    ΔH, ΔS, ΔG, K = calculate_reaction_thermo(reaction, T)

    def equilibrium_function(xi):
        n = n0_arr + nu * xi
        if np.any(n < 0):
            return 1e6  # violates physical feasibility
        n_tot = np.sum(n)
        y = n / n_tot
        Q = 1.0
        for i in range(len(n)):
            if abs(nu[i]) > 0:
                Q *= (y[i] * P / P0) ** nu[i]
        return Q - K

    # Numerical root solving (bisection)
    xi_low = 0.0
    xi_high = np.min(n0_arr / np.abs(nu + 1e-12)) * 0.999
    tol = 1e-8

    for _ in range(500):
        xi_mid = 0.5 * (xi_low + xi_high)
        f_mid = equilibrium_function(xi_mid)
        if abs(f_mid) < tol:
            xi = xi_mid
            break
        if equilibrium_function(xi_low) * f_mid < 0:
            xi_high = xi_mid
        else:
            xi_low = xi_mid
    else:
        xi = xi_mid

    # Equilibrium moles, total moles, mole fractions
    # Equilibrium moles, total moles, mole fractions
    nᵢ = n0_arr + nu * xi
    N = np.sum(nᵢ)
    yᵢ = nᵢ / N

    
    nᵢ (ξ) = [f"{n0[s]} + ({reaction['stoichiometry'][s]})·ξ" for s in species]
    N = [" + ".join([f"{n0[s]} + ({reaction['stoichiometry'][s]})·ξ" for s in results["nᵢ"].keys()])"]
    yᵢ (ξ) = [f"({n0[s]} + ({reaction['stoichiometry'][s]})·ξ)/N" for s in results["nᵢ"].keys()]

    return {
        "ξ_eq": xi,
        "ΔH": ΔH,
        "ΔS": ΔS,
        "ΔG": ΔG,
        "K": K,
        "nᵢ (ξ)"": dict(zip(species, nᵢ (ξ))),
        "yᵢ (ξ)"": dict(zip(species, yᵢ (ξ))),
        "N": N,
        "nᵢ: dict(zip(species, yᵢ (ξ))),
        "yᵢ: dict(zip(species, yᵢ (ξ)))
        }
    }
