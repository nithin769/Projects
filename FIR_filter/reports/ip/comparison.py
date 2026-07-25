import numpy as np
import matplotlib.pyplot as plt

def load_sim_file(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            if not tokens:
                continue
            try:
                # Grab the last token to handle "123" IP formatting
                data.append(int(tokens[-1]))
            except ValueError:
                # Automatically ignores 'x', 'z', and text headers
                pass
    return np.array(data, dtype=np.int32)

def align_and_compare(ip_data, rtl_data, freq_label, max_samples=None):
    if len(ip_data) == 0 or len(rtl_data) == 0:
        print(f"[{freq_label}Hz] Error: Empty data arrays parsed.")
        return

    # Limit search space to avoid the IP's DC offset artifact at the end of simulation
    search_len = min(len(ip_data), len(rtl_data))
    if max_samples:
        search_len = min(search_len, max_samples)

    max_shift = 50
    best_shift = 0
    min_error = float('inf')

    # Find latency difference by minimizing Mean Absolute Error (MAE)
    for shift in range(-max_shift, max_shift):
        if shift >= 0:
            y_ip = ip_data[:search_len]
            y_rtl = rtl_data[shift:shift+search_len]
        else:
            y_ip = ip_data[-shift:-shift+search_len]
            y_rtl = rtl_data[:search_len]
        
        comp_len = min(len(y_ip), len(y_rtl))
        if comp_len < 10:
            continue
            
        err = np.mean(np.abs(y_ip[:comp_len] - y_rtl[:comp_len]))
        if err < min_error:
            min_error = err
            best_shift = shift

    # Align arrays based on the calculated latency
    if best_shift >= 0:
        aligned_ip = ip_data
        aligned_rtl = rtl_data[best_shift:]
    else:
        aligned_ip = ip_data[-best_shift:]
        aligned_rtl = rtl_data

    # Trim to identical lengths for strict comparison
    final_len = min(len(aligned_ip), len(aligned_rtl))
    if max_samples:
        final_len = min(final_len, max_samples)

    aligned_ip = aligned_ip[:final_len]
    aligned_rtl = aligned_rtl[:final_len]

    max_err = np.max(np.abs(aligned_ip - aligned_rtl))
    
    print(f"[{freq_label}Hz] Latency Shift: {abs(best_shift)} samples | Valid Samples: {final_len} | Max Error: {max_err}")

    plt.figure(figsize=(10, 4))
    plt.plot(aligned_ip, label='Quartus IP', alpha=0.8)
    plt.plot(aligned_rtl, '--', label='Verilog', alpha=0.8)
    plt.title(f'IP vs Verilog FIR - {freq_label}Hz')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

frequencies = ["950", "1100", "2000"]
# Truncate 2000Hz to 150 samples so the IP's End-of-File DC flatline doesn't trigger a false error
sample_limits = [None, None, 150] 

for freq, limit in zip(frequencies, sample_limits):
    ip_filename = f"verilog_ip_out_{freq}.txt"
    rtl_filename = f"out_{freq}.dat"
    
    try:
        ip_data = load_sim_file(ip_filename)
        rtl_data = load_sim_file(rtl_filename)
        align_and_compare(ip_data, rtl_data, freq, max_samples=limit)
    except FileNotFoundError as e:
        print(f"[{freq}Hz] Missing file: {e.filename}")
