import numpy as np
import math
FRACTIONAL_BITS = 16
ONE_FP = 1 << FRACTIONAL_BITS
TWO_FP = 2 << FRACTIONAL_BITS
CONST_A_FP = int((4*(math.sqrt(3)-1)) * ONE_FP)
CONST_B_FP = 2 << FRACTIONAL_BITS

def float_to_fp(val):
    return int(val*ONE_FP)

def fp_to_float(val):
    return val/ONE_FP

def fp_multiply(a, b):
    return (a*b) >> FRACTIONAL_BITS

def newton_raphson_division(numerator, denominator):
    num_fp = float_to_fp(numerator)
    k = 0
    temp_d = denominator
    while temp_d > 0:
        k += 1
        temp_d >>= 1
    
    d_norm_float = denominator/(1 << k)
    d_norm_fp = float_to_fp(d_norm_float)
    x0_fp = CONST_A_FP - fp_multiply(CONST_B_FP, d_norm_fp)
    print(f"Shift (k): {k}, Normalized d: {fp_to_float(d_norm_fp):.5f}, Initial Guess (x0): {fp_to_float(x0_fp):.5f}")
    xi_fp = x0_fp
    for i in range(4):
        term_fp = fp_multiply(xi_fp, d_norm_fp)
        diff_fp = TWO_FP - term_fp
        xi_fp = fp_multiply(xi_fp, diff_fp)

    reciprocal_fp = xi_fp >> k
    result_fp = fp_multiply(num_fp, reciprocal_fp)

    actual = numerator / denominator
    computed = fp_to_float(result_fp)

    print(f"-> Computed FP result: {computed:.5f} | Actual Python float: {actual:.5f}")
    return computed

fractions = [(15, 23), (10, 79), (14, 41), (35, 277)]
with open("python_float_results.txt", "w") as f_float, \
     open("python_fixed_results.txt", "w") as f_fixed:

    for n, d in fractions:
        float_result = n / d
        f_float.write(f"{n} {d} {float_result}\n")
        fixed_result = newton_raphson_division(n, d)
        fixed_raw = float_to_fp(fixed_result)
        f_fixed.write(f"{n} {d} {fixed_raw}\n")
