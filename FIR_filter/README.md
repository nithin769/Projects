# Pipelined FIR Filter
A 100-tap Finite Impulse Response (FIR) low-pass filter, implemented and compared across three Verilog pipelining strategies, targeting the Intel Cyclone V FPGA (5CEBA2F17A7). Verified against a MATLAB fixed-point reference model.

# How it works
The filter uses **Q2.14 fixed-point** coefficients (`fir1` designed in MATLAB, cutoff 1kHz at 10kHz sample rate). Three Verilog architectures implement the same 100-tap MAC (multiply-accumulate) filter differently:

1. **Direct (`dir_pipe.v`)** — Registers multiplier outputs, but accumulates the products combinationally in one large adder tree. This creates a long critical path that limits maximum clock frequency (Fmax).
2. **Optimized (`opt_pipe.v`)** — Pipelines both multiplication *and* accumulation, so each stage only has a single multiply-add per clock cycle: `stage[i] <= stage[i-1] + ((x·h[i]) >>> 14)`.
3. **Genvar (`genvar_pipe.v`)** — Same optimized accumulation structure as above, but instantiated using a Verilog `generate` loop, making the pipeline depth easily parameterizable/scalable.

# Files
- `dir_pipe.v` / `opt_pipe.v` / `genvar_pipe.v` — the three FIR filter implementations
- `tb_dir_pipe.v` / `tb_opt_pipe.v` / `tb_genvar_pipe.v` — testbenches driving each design and logging outputs
- `generate.m` — MATLAB script: designs the FIR filter, generates fixed-point coefficients and test signals, and computes a golden fixed-point reference output
- `verify.py` — Python script: aligns and compares hardware output against the MATLAB reference, computing max/mean error per design
- `report.pdf` — Full write-up: architecture explanation, resource/DSP analysis, and error comparison
- (Various `.dat` files — coefficients, input signals, and output logs used to pass data between MATLAB, Verilog, and Python during simulation/verification)

# Results
All three architectures produce numerically consistent outputs (max error ~0.003, matching MATLAB reference), but differ in **timing and resource usage**:
- Direct and unoptimized designs exceeded available DSP resources on the target FPGA, causing synthesis failure
- Optimized and Genvar pipelined designs fit within device constraints while maintaining throughput and improving Fmax
- Genvar consistently achieved the tightest signal-alignment shift (1 cycle) across all three test signals, indicating the most efficient pipeline latency
