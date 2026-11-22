# Exact bound for all heights under the fixed complete clock

This checker uses the exact independently replayed Round 398 checkout and its finished scientific, onboarding and historical receipts. Ordinary heights are integers in [8,192, 524,288], Gaussian height is an integer in [1,024, 524,288], and complete recurring log₂ C is at most 318,292,711 under the unchanged invoice and premise class.

For fixed Gaussian height g, the ordinary sum budget is floor((318292711−1731−220g)/320). For h = (8192, S−8192−524288, 524288) and w = (1/62500, 1/250, 1), define sᵢ = wᵢ/hᵢ². For a competing vector x of heights, sum sᵢ(xᵢ−hᵢ) ≤ 0 if s₁ ≤ s₂ ≤ s₃. This follows from Σx ≤ S, x₁ ≥ h₁ and x₃ ≤ h₃. The exact reciprocal tangent identity

```text
1/x = 1/h − (x−h)/h² + (x−h)²/(h²x)
```

proves the maximum relaxed ordinary rate at h. For every different integer vector, one nonzero remainder incurs a strict weighted gap of at least min(w)/524288³, multiplied by the ordinary factors 249/250 and 1405/1024. This exceeds even the upper bound on the two earlier rounding ticks propagated to the full stage. Checking the true inactive clamp at h proves it is also the actual ordinary-cap optimizer for each bracket point. The h₂ feasibility and slope order hold throughout the initial bracket by monotonicity.

The true optimal ordinary cap is nonincreasing in g because its feasible budget sets are nested. The Gaussian cap is strictly increasing. Binary search of the fixed bracket g₀±2,048 obtains two neighboring integer points, each with exact previous-stage ticks, and compares their true caps. Below the bracket, the Gaussian cap is bounded at the left endpoint. Above it, the ordinary cap is bounded at the right endpoint, even if that higher allocation requires another tangent case. The primary checker allows at most 20 distinct scalar evaluations and 60 seconds. The independent audit may use at most four more, for a combined maximum of 24. The primary checker verifies the candidate's signed stock, geometry and ordinary seams only if the exact optimum strictly exceeds the prior installed crossing. A positive result remains price-only until the literal construction and full independent replay pass.

Both checkers run with CPython 3.12 and one explicit exact Git checkout. [Portable replay](../README.md)
