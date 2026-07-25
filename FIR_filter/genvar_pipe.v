module fir_genvar #(parameter N = 100)(
    input clk,
    input signed [15:0] x,
    output signed [31:0] y
);

    reg signed [15:0] h [0:N-1];
    reg signed [31:0] stage [0:N-1];

    genvar i;
    integer init_idx;

    initial begin
        $readmemh("coeffs_hex.dat", h);
        for (init_idx = 0; init_idx < N; init_idx = init_idx + 1) begin
            stage[init_idx] = 0;
        end
    end

    always @(posedge clk)
        stage[0] <= (x * h[0]) >>> 14;

    generate
        for (i = 1; i < N; i = i + 1) begin : MAC
            always @(posedge clk)
                stage[i] <= stage[i-1] + ((x * h[i]) >>> 14);
        end
    endgenerate

    assign y = stage[N-1];

endmodule
