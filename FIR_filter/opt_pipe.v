module fir_optimized #(parameter N = 100)(
    input clk,
    input signed [15:0] x,
    output reg signed [31:0] y
);

    reg signed [15:0] h [0:N-1];
    reg signed [31:0] stage [0:N-1];

    integer i;

    initial begin
        $readmemh("coeffs_hex.dat", h);
        for (i = 0; i < N; i = i + 1) begin
            stage[i] = 0;
        end
    end

    always @(posedge clk) begin
        stage[0] <= (x * h[0]) >>> 14;

        for (i = 1; i < N; i = i + 1)
            stage[i] <= stage[i-1] + ((x * h[i]) >>> 14);

        y <= stage[N-1];
    end

endmodule
