% FIR Filter Design
fs = 10000;
fc = 1000;
taps = 100;

h = fir1(taps-1, fc/(fs/2));

% -------- Q(2,14) COEFFICIENTS --------
h_fixed = int16(round(h * 2^14));

fid = fopen('coeffs_hex.dat', 'w');
fprintf(fid, '%04X\n', typecast(h_fixed, 'uint16'));
fclose(fid);

% -------- SIGNAL GENERATION --------
f = [950, 1100, 2000];
t = (0:1/fs:0.05)';

figure('Name', 'MATLAB Reference Outputs (Q2.14)');

for k = 1:3
    
    % Generate signal
    sig = sin(2*pi*f(k)*t);
    sig_fixed = int16(round(sig * 2^14));

    % Save input
    fid = fopen(sprintf('signal_%d.dat', k), 'w');
    fprintf(fid, '%d\n', sig_fixed);
    fclose(fid);

    % -------- FIXED-POINT FIR (MATCH VERILOG) --------
    y_fixed = zeros(length(sig_fixed),1,'int32');

    for n = 1:length(sig_fixed)
        acc = int32(0);
        for m = 1:taps
            if (n-m+1) > 0
                prod = int32(sig_fixed(n-m+1)) * int32(h_fixed(m));
                prod = bitshift(prod, -14);   % >>>14
                acc = acc + prod;
            end
        end
        y_fixed(n) = acc;
    end

    % Save MATLAB reference output
    fid = fopen(sprintf('matlab_out_%d.dat', k), 'w');
    fprintf(fid, '%d\n', y_fixed);
    fclose(fid);

    % -------- Plot (scaled back to float) --------
    y_float = double(y_fixed) / 2^14;

    subplot(3,1,k);
    plot(t, y_float, 'LineWidth', 1.5);
    title(sprintf('MATLAB Output (Q2.14): %d Hz', f(k)));
    grid on;
end