module fir_direct_pipe #(parameter N = 100)(
    input clk,
    input signed [15:0] x,
    output reg signed [31:0] y
);

    reg signed [15:0] h [0:N-1];
    reg signed [15:0] delay [0:N-1];
    reg signed [31:0] mult_reg [0:N-1];
    
    reg signed [31:0] combo_sum [0:N-1];
    integer i;

    initial begin
        $readmemh("coeffs_hex.dat", h);
        for (i = 0; i < N; i = i + 1) begin
            delay[i] = 0;
            mult_reg[i] = 0;
        end
    end

    always @(posedge clk) begin
        delay[0] <= x;
        for (i = 1; i < N; i = i + 1) begin
            delay[i] <= delay[i-1];
        end

        for (i = 0; i < N; i = i + 1) begin
            mult_reg[i] <= (delay[i] * h[i]) >>> 14;
        end

        y <= combo_sum[N-1];
    end

    always @(*) begin
        combo_sum[0] = mult_reg[0];
        for (i = 1; i < N; i = i + 1) begin
            combo_sum[i] = combo_sum[i-1] + mult_reg[i];
        end
    end

endmodule
