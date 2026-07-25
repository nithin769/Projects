# 8-Point Pipelined FFT (Radix-2, DIT)
A custom hardware implementation of an 8-point Radix-2 Fast Fourier Transform using a Decimation-In-Time (DIT) pipelined architecture, self-checking testbench, and synthesis comparison against a vendor FFT IP core.

# How it works
The core module (`fft8_pipeline_cla`) processes serial input samples through three stages:

1. **Input Buffering & Bit-Reversal** — Serial samples (`din_re`, `din_im`) are shifted into a buffer until a full 8-point frame arrives, then loaded into parallel registers using bit-reversed indexing (required for DIT).
2. **Pipelined Butterfly Stages** — Three synchronous stages progressively combine samples: Stage 1 runs parallel 2-point butterflies, Stage 2 runs 4-point butterflies, Stage 3 runs the final 8-point butterflies to resolve frequency bins.
3. **Fixed-Point Twiddle Multiplication** — The final stage applies twiddle factors using custom fixed-point multiply functions (`mul_re`, `mul_im`) with arithmetic right-shifts, avoiding floating-point logic or vendor DSP blocks entirely.

The testbench (`fft8_tb_cla`) is self-checking: it streams in five test signals (cosine tone, impulse, DC, complex exponential, two-tone) and automatically compares output bins against expected magnitudes, printing PASS/FAIL per test case.

# Files
- `fft8_pipeline_cla.v` — core FFT pipeline module
- `fft8_tb_cla.v` — self-checking testbench with 5 test cases
- `fft_verify.m` — MATLAB script: computes floating-point FFT reference, verifies Verilog fixed-point output against it (tolerance-based pass/fail), and plots magnitude spectrum overlays
- `report.pdf` — Full write-up: architecture details, verification results, and synthesis/performance comparison

# Results
**Verification:** All 5 test cases matched the MATLAB floating-point reference within tolerance, confirmed via magnitude spectrum overlay plots.
