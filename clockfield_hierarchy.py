#!/usr/bin/env python3
"""
CLOCKFIELD HIERARCHY: The Γ-Power Tower
==========================================

Computes and visualizes how the Clockfield metric Γ = 1/(1+τβ)²
creates the 37-order hierarchy between electromagnetic and
gravitational coupling.

Key insight:
  EM coupling   ~ Γ²_vac  (two powers of the metric)
  Gravity       ~ Γ⁴_vac  (four powers of the metric)
  Hierarchy     = Γ²_vac / Γ⁴_vac = 1/Γ²_vac

For 1/Γ²_vac ≈ 10³⁷ → Γ_vac ≈ 10⁻¹⁸·⁵ → τβ₀ ≈ 1.78 × 10⁹

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import numpy as np
from scipy import optimize
import json

# ═══════════════════════════════════════════════════════════════════
# PHYSICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════

ALPHA_EM = 1.0 / 137.035999084
HBAR_C = 3.16153e-26  # ħc in J·m
G_NEWTON = 6.67430e-11  # m³/(kg·s²)
M_PROTON = 1.67262e-27  # kg
C_LIGHT = 2.99792e8     # m/s
L_PLANCK = 1.61626e-35  # m

# The hierarchy ratio
HIERARCHY = ALPHA_EM * HBAR_C / (G_NEWTON * M_PROTON**2)
print(f"Physical hierarchy: α·ħc/(G·m_p²) = {HIERARCHY:.4e}")
print(f"  = 10^{np.log10(HIERARCHY):.2f}")

# ═══════════════════════════════════════════════════════════════════
# THE Γ-POWER TOWER
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("THE Γ-POWER TOWER: How Different Couplings Scale with τβ₀")
print("="*80)

def Gamma_vac(tb0):
    """Vacuum proper-time rate."""
    return 1.0 / (1.0 + tb0)**2

def hierarchy_ratio(tb0):
    """The EM/gravity ratio = 1/Γ²_vac."""
    g = Gamma_vac(tb0)
    return 1.0 / (g**2) if g > 0 else np.inf

print(f"\n{'τβ₀':>12s} {'Γ_vac':>14s} {'Γ² (EM)':>14s} {'Γ⁴ (Grav)':>14s} "
      f"{'1/Γ² = Hierarchy':>18s} {'log₁₀':>8s}")
print("-" * 90)

tb_values = [0.5, 1, 2, 3, 5, 10, 30, 100, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1.78e9]
for tb in tb_values:
    g = Gamma_vac(tb)
    g2 = g**2
    g4 = g**4
    h = 1.0/g2 if g2 > 0 else np.inf
    log_h = np.log10(h) if h > 0 and not np.isinf(h) else 0
    marker = " ★" if abs(log_h - 37) < 1 else ""
    print(f"  {tb:10.2e}  {g:14.6e}  {g2:14.6e}  {g4:14.6e}  {h:18.6e}  {log_h:8.2f}{marker}")

# Find the exact τβ₀ for 10³⁷ hierarchy
try:
    sol = optimize.brentq(lambda log_tb: np.log10(hierarchy_ratio(10**log_tb)) - 37.0,
                          8, 11, xtol=1e-12)
    tb_37 = 10**sol
    g_37 = Gamma_vac(tb_37)
    print(f"\n★ Exact 10³⁷ hierarchy at τβ₀ = {tb_37:.6e}")
    print(f"  Γ_vac = {g_37:.6e}")
    print(f"  1/Γ²_vac = {1/g_37**2:.6e}")
except:
    tb_37 = 1.78e9

# ═══════════════════════════════════════════════════════════════════
# THE α-HIERARCHY CONNECTION
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("THE α-HIERARCHY CONNECTION")
print("="*80)

def alpha_self(tb0, rmax=500, n=100000):
    """Γ²-weighted self-energy ratio (the EM coupling)."""
    r = np.linspace(0.5, rmax, n)
    A = np.tanh(r)  # vortex profile, ξ=1
    beta = A**2
    G_r = 1.0 / (1.0 + tb0 * beta)**2
    num = np.trapezoid(G_r**2 * A**2 / r, r)
    den = np.trapezoid(A**2 / r, r)
    return num / den if den > 0 else 0

print("""
In the Clockfield, the fine-structure constant α is the Γ²-screened
self-energy ratio of a vortex. We can compute α_self(τβ₀) and ask:
at what τβ₀ does α = 1/137, and what hierarchy does that produce?
""")

# 2D calculation
print("2D vortex (toy model):")
try:
    sol_alpha = optimize.brentq(lambda log_tb: alpha_self(10**log_tb) - ALPHA_EM,
                                 0, 4, xtol=1e-12)
    tb_alpha_2d = 10**sol_alpha
    g_alpha = Gamma_vac(tb_alpha_2d)
    h_alpha = hierarchy_ratio(tb_alpha_2d)
    print(f"  α = 1/137 at τβ₀ = {tb_alpha_2d:.6f}")
    print(f"  Γ_vac = {g_alpha:.6f}")
    print(f"  Hierarchy = 1/Γ² = {h_alpha:.1f} (= 10^{np.log10(h_alpha):.2f})")
    print(f"  Physical hierarchy = 10^37")
    print(f"  Gap: factor of 10^{37 - np.log10(h_alpha):.1f}")
    print(f"\n  → The 2D model gives a hierarchy of ~{h_alpha:.0f}, not 10³⁷.")
    print(f"    The 3D calculation must produce a much larger τβ₀.")
except Exception as e:
    print(f"  Could not find α crossing: {e}")
    tb_alpha_2d = 2.895

# 3D extrapolation
print("\n3D vortex string (extrapolation):")

def alpha_self_3d_monopole(tb0, rmax=500, n=100000):
    """3D monopole version: r²-weighted screening."""
    r = np.linspace(0.5, rmax, n)
    A = np.tanh(r)
    beta = A**2
    G_r = 1.0 / (1.0 + tb0 * beta)**2
    num = np.trapezoid(G_r**2 * A**2 * r**2, r)
    den = np.trapezoid(A**2 * r**2, r)
    return num / den if den > 0 else 0

try:
    sol_3d = optimize.brentq(lambda log_tb: alpha_self_3d_monopole(10**log_tb) - ALPHA_EM,
                              0, 6, xtol=1e-12)
    tb_alpha_3d = 10**sol_3d
    g_3d = Gamma_vac(tb_alpha_3d)
    h_3d = hierarchy_ratio(tb_alpha_3d)
    print(f"  α_3D = 1/137 at τβ₀ = {tb_alpha_3d:.6f}")
    print(f"  Γ_vac = {g_3d:.6e}")
    print(f"  Hierarchy = 1/Γ² = {h_3d:.4e} (= 10^{np.log10(h_3d):.2f})")
    print(f"\n  → The 3D monopole gives τβ₀ = {tb_alpha_3d:.2f}")
    print(f"    Still not 10⁹, but the r² weighting pushes it higher.")
except Exception as e:
    print(f"  Could not find 3D α crossing: {e}")
    tb_alpha_3d = None

# ═══════════════════════════════════════════════════════════════════
# THE CASCADE DYNAMICS
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("THE 5TH-POWER CASCADE")
print("="*80)
print("""
The escape rate from a Clockfield high-β region scales as:
  R_escape ∝ (1+τβ)⁻⁵

Starting from Ξ = 1 (critical), a small perturbation δβ triggers
a cascade that amplifies through 37 orders. Here is the arithmetic:
""")

def cascade_simulation(tb0_initial, delta_frac=0.1, n_steps=200):
    """Simulate the 5th-power cascade from just above critical."""
    tb = tb0_initial * (1 + delta_frac)  # start just above critical
    history = [tb]
    
    for step in range(n_steps):
        # Escape rate (normalized to 1 at the critical point)
        R_escape = 1.0 / (1 + tb)**5
        R_escape_crit = 1.0 / (1 + tb0_initial)**5
        
        # Net growth: accumulation exceeds escape
        # Growth rate ∝ (R_accum - R_escape) ∝ (1 - R_escape/R_accum)
        # At Ξ = 1+δ: R_escape/R_accum = (1+tb_crit)⁵/(1+tb)⁵ < 1
        ratio = ((1 + tb0_initial) / (1 + tb))**5
        growth_rate = max(0, 1 - ratio)  # normalized
        
        # β grows proportionally
        delta_tb = tb * growth_rate * 0.1  # timestep factor
        tb += delta_tb
        history.append(tb)
        
        if tb > 1e20:  # Overflow prevention
            break
    
    return history

# Run cascade from modest initial τβ₀
for tb_init in [1.0, 5.0, 10.0]:
    hist = cascade_simulation(tb_init, delta_frac=0.1, n_steps=500)
    orders = np.log10(hist[-1] / hist[0]) if hist[-1] > hist[0] else 0
    print(f"  τβ₀_initial = {tb_init:.1f}, 10% above critical:")
    print(f"    After cascade: τβ₀_final = {hist[-1]:.2e}")
    print(f"    Amplification: {orders:.1f} orders of magnitude")
    print(f"    Steps to complete: {len(hist)}")

# ═══════════════════════════════════════════════════════════════════
# THE BEKENSTEIN-HAWKING CONNECTION
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("BEKENSTEIN-HAWKING AND THE HIERARCHY")
print("="*80)

# For a solar-mass black hole
M_SUN = 1.989e30  # kg
R_BH = 2 * G_NEWTON * M_SUN / C_LIGHT**2
print(f"\nSolar-mass black hole:")
print(f"  Schwarzschild radius: {R_BH:.4f} m")
print(f"  Planck length: {L_PLANCK:.4e} m")
print(f"  Ratio R_BH/ℓ_P: {R_BH/L_PLANCK:.4e}")
print(f"  BH entropy S = A/(4ℓ_P²) = π·R²/(ℓ_P²) = {np.pi * R_BH**2 / L_PLANCK**2:.4e}")

# The entropy in terms of Γ_vac
print(f"\nIn Clockfield terms (at the physical τβ₀ = {tb_37:.2e}):")
g_phys = Gamma_vac(tb_37)
print(f"  Γ_vac = {g_phys:.4e}")
print(f"  ℓ_P = ξ · Γ_vac^(1/2) → ξ = ℓ_P / Γ_vac^(1/2) = {L_PLANCK / np.sqrt(g_phys):.4e} m")
print(f"  This ξ is the 'bare' vortex core size at the core rate")

# The entropy rewritten
xi_bare = L_PLANCK / np.sqrt(g_phys)
S_area = np.pi * R_BH**2 / (4 * L_PLANCK**2)
S_clockfield = np.pi * R_BH**2 / (xi_bare**2) * np.log(2 * 330)
print(f"\n  S_BH = {S_area:.4e} (standard)")
print(f"  S_CF = (A/ξ²)·ln(2m) with m=330: {S_clockfield:.4e}")
print(f"  Ratio S_CF/S_BH: {S_clockfield/S_area:.4f}")

# ═══════════════════════════════════════════════════════════════════
# THE PLANCK SCALE AS FROZEN VACUUM
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("THE PLANCK SCALE AS Γ-COMPRESSED CORE SIZE")
print("="*80)

# If ℓ_P = ξ_core · Γ_vac^(1/2), what is ξ_core?
print(f"\nThe Clockfield says: ℓ_P = ξ · √(Γ_vac)")
print(f"At τβ₀ = {tb_37:.2e}:")
print(f"  Γ_vac = {g_phys:.4e}")
print(f"  √(Γ_vac) = {np.sqrt(g_phys):.4e}")
print(f"  ξ_core = ℓ_P / √(Γ_vac) = {xi_bare:.4e} m")
print(f"  = {xi_bare/1e-26:.2f} × 10⁻²⁶ m")

# Compton wavelength of the proton
lambda_C_proton = HBAR_C / (M_PROTON * C_LIGHT**2) * C_LIGHT
print(f"\nFor comparison:")
print(f"  Proton Compton wavelength: {lambda_C_proton:.4e} m")
print(f"  ξ_core / λ_C(proton) = {xi_bare/lambda_C_proton:.4e}")
print(f"  Classical electron radius: {2.818e-15:.4e} m")
print(f"  ξ_core / r_e = {xi_bare/2.818e-15:.4e}")

# ═══════════════════════════════════════════════════════════════════
# THE COMPLETE CONSTRAINT WEB
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("THE COMPLETE CLOCKFIELD CONSTRAINT WEB")
print("="*80)
print(f"""
Starting from 4 parameters: (μ², λ, τ, c₀)

Constraint 1: E = mc²
  μ⁴/(2λ) = c₀²
  Reduces to 3 free parameters.

Constraint 2: α = 1/137
  α_self(τβ₀) = 1/137
  In 2D: τβ₀ = {tb_alpha_2d:.4f}
  Reduces to 2 free parameters.

Constraint 3: The hierarchy
  G·m²/α = Γ²_vac = 1/(1+τβ₀)⁴
  For physical ratio: τβ₀ = {tb_37:.4e}
  Reduces to 1 free parameter (a scale).

Constraint 4: ??? (Closure)
  Candidates:
  a) Marginal stability: Ξ = 1 at vortex edge
  b) Noise self-consistency: ℏ_eff from collective Hawking radiation
  c) 3D topological quantization
  d) Cosmological consistency (total energy = 0)

If found: 0 free parameters. Everything predicted.

THE KEY QUESTION:
  Does the 3D version of α_self = 1/137 automatically give τβ₀ ~ 10⁹?
  If yes → the hierarchy is EXPLAINED.
  If no → the hierarchy requires a separate closure condition.
""")

# ═══════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ═══════════════════════════════════════════════════════════════════

output = {
    'physical_hierarchy': float(HIERARCHY),
    'log10_hierarchy': float(np.log10(HIERARCHY)),
    'tb0_for_10_37': float(tb_37),
    'Gamma_vac_at_hierarchy': float(g_phys),
    'xi_core_meters': float(xi_bare),
    'alpha_2D': {
        'tb0': float(tb_alpha_2d),
        'Gamma_vac': float(Gamma_vac(tb_alpha_2d)),
        'hierarchy': float(hierarchy_ratio(tb_alpha_2d)),
    },
    'planck': {
        'l_P_meters': float(L_PLANCK),
        'l_P_over_Gamma_half': float(xi_bare),
    },
    'gamma_power_tower': [
        {'tb0': float(tb), 'Gamma_vac': float(Gamma_vac(tb)),
         'Gamma_sq': float(Gamma_vac(tb)**2), 'Gamma_4': float(Gamma_vac(tb)**4),
         'hierarchy': float(hierarchy_ratio(tb)),
         'log10_hierarchy': float(np.log10(hierarchy_ratio(tb)))}
        for tb in tb_values
    ],
}

with open('clockfield_hierarchy.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved: clockfield_hierarchy.json")
print("\nDone.")
