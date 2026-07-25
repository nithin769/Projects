clc; clear; close all;
N = 8;
tests = {};

% TC1: Cosine (k=1)
n = 0:N-1;
tests{1} = 100*cos(2*pi*1*n/N);

% TC2: Impulse
tests{2} = [127 zeros(1,7)];

% TC3: DC
tests{3} = 64*ones(1,N);

% TC4: Complex exponential (k=2)
tests{4} = 100*exp(1j*2*pi*2*n/N);

% TC5: Two-tone (k=2 and k=6)
tests{5} = 50*cos(2*pi*2*n/N) + 50*cos(2*pi*6*n/N);

verilog = {};

verilog{1} = [ ...
  0+0j;
  400+0j;
  0+0j;
 -1+0j;
  0+0j;
  0+0j;
  0+0j;
  401+0j ];

verilog{2} = 127*ones(8,1);

verilog{3} = [512;0;0;0;0;0;0;0];

verilog{4} = [0;0;800;0;0;0;0;0];

verilog{5} = [0;0;400;0;0;0;400;0];

for t = 1:5
    
    x = tests{t};
    X_matlab = fft(x);
    X_verilog = verilog{t}.';
    err = abs(X_matlab - X_verilog);
    
    fprintf('\n===== TC%d =====\n', t);
    fprintf('Max Error = %.2f\n', max(err));
    
    disp('MATLAB FFT:');
    disp(round(X_matlab));
    
    disp('Verilog FFT:');
    disp(X_verilog);
    
end

clear; clc; close all;

N        = 8;               
DW       = 20;                   
TW       = 16;                   
SCALE    = 2^15;                 
CLIP_MAX = 2^(DW-1) - 1;        
CLIP_MIN = -2^(DW-1);

tw_re = [32767,  23170,      0, -23170];
tw_im = [    0, -23170, -32767, -23170];

function [wr, wi] = q15_cmul(ar, ai, wr_t, wi_t)
    wr = floor( (ar * wr_t - ai * wi_t) / 2^15 );
    wi = floor( (ar * wi_t + ai * wr_t) / 2^15 );
end

function y = clip20(x)
    CLIP_MAX = 2^19 - 1;
    CLIP_MIN = -2^19;
    y = max(CLIP_MIN, min(CLIP_MAX, x));
end

function [y0r, y0i, y1r, y1i] = butterfly(ar, ai, br, bi, wr_t, wi_t)
    [wbr, wbi] = q15_cmul(br, bi, wr_t, wi_t);
    y0r = clip20(ar + wbr);  y0i = clip20(ai + wbi);
    y1r = clip20(ar - wbr);  y1i = clip20(ai - wbi);
end

test_cases = {
    'TC1: Cosine tone k=1', ...
        int8([100, 71,  0, -71, -100, -71,   0,  71]), int8(zeros(1,8));
    'TC2: Impulse', ...
        int8([127,  0,  0,   0,    0,   0,   0,   0]), int8(zeros(1,8));
    'TC3: DC signal', ...
        int8([ 64, 64, 64,  64,   64,  64,  64,  64]), int8(zeros(1,8));
    'TC4: Complex exp k=2', ...
        int8([100,  0,-100,  0,  100,   0,-100,   0]), ...
        int8([  0,100,   0,-100,   0, 100,   0,-100]);
    'TC5: Two-tone k=1,3', ...
        int8([100,  0,-100,  0,  100,   0,-100,   0]), int8(zeros(1,8));
};

num_tests = size(test_cases, 1);
fig_idx   = 0;

fprintf('\n%s\n', repmat('=',1,70));
fprintf('  8-POINT FFT VERIFICATION: MATLAB vs Fixed-Point Verilog Model\n');
fprintf('%s\n\n', repmat('=',1,70));

all_pass = true;
TOLERANCE = 2;

for tc = 1:num_tests
    tc_name = test_cases{tc,1};
    xr = double(test_cases{tc,2}); 
    xi = double(test_cases{tc,3});  
    x  = xr + 1j*xi;

    fprintf('─── %s ───\n', tc_name);

    X_matlab = fft(x, N);

   
    brev_r = double(int32(xr));
    brev_i = double(int32(xi));
    br_order = [1,5,3,7,2,6,4,8];
    brev_r = brev_r(br_order);
    brev_i = brev_i(br_order);

    s = brev_r + 1j*brev_i;  
    s1 = zeros(1, N);
    for p = [1,3,5,7] 
        a = s(p); b = s(p+1);
        s1(p)   = a + b;
        s1(p+1) = a - b;
    end

    s2 = zeros(1, N);

    s2(1) = s1(1) + s1(3);
    s2(3) = s1(1) - s1(3);
    wb = imag(s1(4)) - 1j*real(s1(4));
    s2(2) = s1(2) + wb;
    s2(4) = s1(2) - wb;
    
    s2(5) = s1(5) + s1(7);
    s2(7) = s1(5) - s1(7);
    
    wb = imag(s1(8)) - 1j*real(s1(8));
    s2(6) = s1(6) + wb;
    s2(8) = s1(6) - wb;

    s3 = zeros(1, N);
    tw_complex = (tw_re + 1j*tw_im) / 2^15; 

    for p_idx = 0:3
        p = p_idx + 1;         
        q = p_idx + 5;      
        tw = tw_complex(p_idx+1);
        wb = tw * s2(q);
     
        wb_r = floor(real(s2(q))*real(tw) - imag(s2(q))*imag(tw));
        wb_i = floor(real(s2(q))*imag(tw) + imag(s2(q))*real(tw));
        s3(p) = s2(p) + wb_r + 1j*wb_i;
        s3(q) = s2(p) - wb_r - 1j*wb_i;
    end

    X_verilog = s3;
    err_re = abs(real(X_matlab) - real(X_verilog));
    err_im = abs(imag(X_matlab) - imag(X_verilog));
    max_err = max(max(err_re), max(err_im));
    pass = max_err <= TOLERANCE;
    all_pass = all_pass && pass;

    fprintf('  %-12s %-12s %-12s %-12s %-12s\n', ...
        'Bin', 'MATLAB Re', 'Verilog Re', 'MATLAB Im', 'Verilog Im');
    fprintf('  %s\n', repmat('-',1,65));
    for k = 0:N-1
        fprintf('  %-12d %-12.1f %-12.1f %-12.1f %-12.1f\n', k, ...
            real(X_matlab(k+1)), real(X_verilog(k+1)), ...
            imag(X_matlab(k+1)), imag(X_verilog(k+1)));
    end
    if pass
        fprintf('  ✓ PASS  (max error = %.1f LSB)\n\n', max_err);
    else
        fprintf('  ✗ FAIL  (max error = %.1f LSB — exceeds tolerance of %d)\n\n', ...
            max_err, TOLERANCE);
    end

    fig_idx = fig_idx + 1;
    figure(fig_idx);
    bins = 0:N-1;
    subplot(2,1,1);
    bar(bins, abs(X_matlab), 0.4, 'FaceColor', [0.2,0.5,0.8]);
    title([tc_name, ' — Magnitude (MATLAB reference)']);
    xlabel('Frequency bin k'); ylabel('|X[k]|');
    xticks(bins); grid on;

    subplot(2,1,2);
    stem(bins, abs(X_matlab),  'b-o', 'LineWidth', 1.5, 'DisplayName','MATLAB float');
    hold on;
    stem(bins, abs(X_verilog), 'r--s','LineWidth', 1.5, 'DisplayName','Verilog fixed-pt');
    title([tc_name, ' — Overlay: MATLAB vs Verilog']);
    xlabel('Frequency bin k'); ylabel('|X[k]|');
    legend('Location','best'); xticks(bins); grid on;
    hold off;
end

for f = 1:num_tests
    figure(f);
    print(sprintf('fft_tc%d_spectrum', f), '-dpng', '-r150');
end
fprintf('  Figures saved as fft_tc1_spectrum.png ... fft_tc%d_spectrum.png\n', num_tests);
fprintf('%s\n', repmat('=',1,70));
