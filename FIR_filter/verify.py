import numpy as np
import matplotlib.pyplot as plt

FRAC_BITS = 14

def load_hex_file(filename):
    data = []
    with open(filename) as f:
        for line in f:
            val = int(line.strip(), 16)
            if val >= 2**15:
                val -= 2**16
            data.append(val)
    return np.array(data, dtype=np.int16)

def load_output_file(filename):
    data = []
    with open(filename) as f:
        for line in f:
            try:
                data.append(int(line.strip()))
            except:
                continue
    return np.array(data, dtype=np.int32)

def fir_ideal(x, h):
    x_float = x / (2**FRAC_BITS)
    h_float = h / (2**FRAC_BITS)
    
    y = np.convolve(x_float, h_float, mode='full')
    return y[:len(x)]

def align_signals(y_ref, y_hw):
    max_shift = 200
    best_shift = 0
    min_error = float('inf')

    for shift in range(max_shift):
        length = min(len(y_ref), len(y_hw) - shift)
        if length <= 0:
            continue

        err = np.mean(np.abs(y_ref[:length] - y_hw[shift:shift+length]))

        if err < min_error:
            min_error = err
            best_shift = shift

    return best_shift

h = load_hex_file("coeffs_hex.dat")

methods = [
    ("Direct",    "output_direct_{}.dat"),
    ("Optimized", "output_optimized_{}.dat"),
    ("Genvar",    "output_genvar_{}.dat")
]

for i in range(1, 4):
    x = np.loadtxt(f"signal_{i}.dat", dtype=np.int16)
    y_ref = fir_ideal(x, h)
    plt.figure(figsize=(10,8))

    for idx, (name, pattern) in enumerate(methods, 1):
        y_hw_fixed = load_output_file(pattern.format(i))
        y_hw = y_hw_fixed / (2**FRAC_BITS)

        shift = align_signals(y_ref, y_hw)
        length = min(len(y_ref), len(y_hw)-shift)
        
        y_r = y_ref[:length]
        y_h = y_hw[shift:shift+length]

        error = y_r - y_h

        print(f"\nSignal {i} | {name}")
        print("Shift (Clock Cycles):", shift)
        print("Max Error:", np.max(np.abs(error)))
        print("Mean Error:", np.mean(np.abs(error)))

        plt.subplot(3,1,idx)
        plt.plot(y_r, label="Ideal Reference")
        plt.plot(y_h, '--', label="Hardware")
        plt.title(f"{name} FIR - Signal {i}")
        plt.legend()
        plt.grid()

    plt.tight_layout()
    plt.suptitle(f"Signal {i}", y=1.02)
plt.show()
