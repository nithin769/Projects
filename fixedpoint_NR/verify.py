FRAC_BITS = 16
SCALE = 1 << FRAC_BITS

def fp_to_float(x):
    return x / SCALE

def read_float_file(filename):
    data = {}
    with open(filename, "r") as f:
        for line in f:
            n, d, val = line.strip().split()
            data[(int(n), int(d))] = float(val)
    return data

def read_fixed_file(filename):
    data = {}
    with open(filename, "r") as f:
        for line in f:
            n, d, val = line.strip().split()
            data[(int(n), int(d))] = int(val)
    return data

python_float = read_float_file("python_float_results.txt")
python_fixed = read_fixed_file("python_fixed_results.txt")
verilog_fixed = read_fixed_file("verilog_results.txt")

print("FINAL ERROR COMPARISON")
print(f"{'n/d':<10} {'Float':<12} {'Python FP':<12} {'Verilog':<12} {'Err(Py)':<12} {'Err(Ver)':<12}")

for key in python_float:
    float_val = python_float[key]
    py_val = fp_to_float(python_fixed[key])
    ver_val = fp_to_float(verilog_fixed[key])
    err_py = abs(float_val - py_val)
    err_ver = abs(float_val - ver_val)
    print(f"{key[0]}/{key[1]:<7} {float_val:<12.6f} {py_val:<12.6f} {ver_val:<12.6f} {err_py:<12.8f} {err_ver:<12.8f}")
