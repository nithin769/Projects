# Fixed-Point Division using Newton-Raphson
Implementation of a fast, hardware-friendly division algorithm using the Newton-Raphson iterative method, avoiding direct division hardware. Includes a Python reference model and a Verilog FSM implementation, verified against each other.

# How it works
Instead of computing `q = numerator / denominator` directly, the algorithm:

1. Normalizes the denominator to the range `[0.5, 1)`
2. Computes an initial guess for the reciprocal `1/d` using a closed-form linear approximation (`x0 = A − B·d`, derived via minimax/equioscillation)
3. Refines the guess through 4 Newton-Raphson iterations: `x(i+1) = x(i) · (2 − x(i)·d)`, which converges quadratically
4. Multiplies the final reciprocal by the numerator to get the quotient

All arithmetic uses Q16.16 fixed-point representation.

# Files
- `pycode.py` — Python reference/golden model; computes both floating-point and fixed-point results for test fractions and writes them to file
- `verilog.v` — Verilog FSM (`nr_divider`) implementing the same algorithm in fixed-point hardware logic
- `testbench.v` — Testbench (`tb_nr_divider`) that drives test cases through the Verilog module and logs results
- `report.pdf` — Full write-up: mathematical derivation, error/convergence analysis, and simulation results

# Results
Verified against 4 test fractions (e.g. 15/23, 10/79, 14/41, 35/277). Verilog output closely matches expected floating-point values, with small deltas (~0.00009) attributed to Q16.16 truncation error during fixed-point multiplication.
