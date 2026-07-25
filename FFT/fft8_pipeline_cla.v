`timescale 1ns/1ps
module fft8_pipeline(
    input  wire clk,
    input  wire rst_n,
    input  wire din_valid,
    input  wire signed  [7:0] din_re,
    input  wire signed  [7:0] din_im,

    output reg dout_valid,

    output reg  signed [23:0] r0, i0,
    output reg  signed [23:0] r1, i1,
    output reg  signed [23:0] r2, i2,
    output reg  signed [23:0] r3, i3,
    output reg  signed [23:0] r4, i4,
    output reg  signed [23:0] r5, i5,
    output reg  signed [23:0] r6, i6,
    output reg  signed [23:0] r7, i7
);

integer i;
reg [2:0] count;
reg full;
reg signed [23:0] xr [0:7];
reg signed [23:0] xi [0:7];

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        count <= 3'd0;
        full  <= 1'b0;

    end else if (full) begin
        full  <= 1'b0;
        count <= 3'd0;

    end else if (din_valid) begin
        xr[count] <= {{16{din_re[7]}}, din_re};
        xi[count] <= {{16{din_im[7]}}, din_im};
        if (count == 3'd7)
            full <= 1'b1;
        else
            count <= count + 3'd1;
    end
end

reg signed [23:0] br [0:7];
reg signed [23:0] bi [0:7];
reg v1;

always @(posedge clk) begin
    v1 <= full;
    if (full) begin
        br[0] <= xr[0];  bi[0] <= xi[0];
        br[1] <= xr[4];  bi[1] <= xi[4];
        br[2] <= xr[2];  bi[2] <= xi[2];
        br[3] <= xr[6];  bi[3] <= xi[6];
        br[4] <= xr[1];  bi[4] <= xi[1];
        br[5] <= xr[5];  bi[5] <= xi[5];
        br[6] <= xr[3];  bi[6] <= xi[3];
        br[7] <= xr[7];  bi[7] <= xi[7];
    end
end

reg signed [23:0] s1r [0:7];
reg signed [23:0] s1i [0:7];
reg v2;

always @(posedge clk) begin
    v2 <= v1;
    if (v1) begin
        for (i = 0; i < 8; i = i + 2) begin
            s1r[i] <= br[i] + br[i+1];
            s1i[i] <= bi[i] + bi[i+1];
            s1r[i+1] <= br[i] - br[i+1];
            s1i[i+1] <= bi[i] - bi[i+1];
        end
    end
end

reg signed [23:0] s2r [0:7];
reg signed [23:0] s2i [0:7];
reg               v3;

always @(posedge clk) begin
    v3 <= v2;
    if (v2) begin
        s2r[0] <= s1r[0] + s1r[2];
        s2i[0] <= s1i[0] + s1i[2];
        s2r[2] <= s1r[0] - s1r[2];
        s2i[2] <= s1i[0] - s1i[2];

        s2r[1] <= s1r[1] + s1i[3];
        s2i[1] <= s1i[1] - s1r[3];
        s2r[3] <= s1r[1] - s1i[3];
        s2i[3] <= s1i[1] + s1r[3];

        s2r[4] <= s1r[4] + s1r[6];
        s2i[4] <= s1i[4] + s1i[6];
        s2r[6] <= s1r[4] - s1r[6];
        s2i[6] <= s1i[4] - s1i[6];

        s2r[5] <= s1r[5] + s1i[7];
        s2i[5] <= s1i[5] - s1r[7];
        s2r[7] <= s1r[5] - s1i[7];
        s2i[7] <= s1i[5] + s1r[7];
    end
end

function signed [23:0] mul_re;
    input signed [17:0] Wr, Wi;
    input signed [23:0] Br, Bi;
    reg signed [42:0] t;
    begin
        t = ($signed(Wr) * $signed(Br)) - ($signed(Wi) * $signed(Bi));
        mul_re = t >>> 17;
    end
endfunction

function signed [23:0] mul_im;
    input signed [17:0] Wr, Wi;
    input signed [23:0] Br, Bi;
    reg signed [42:0] t;
    begin
        t = ($signed(Wr) * $signed(Bi)) + ($signed(Wi) * $signed(Br));
        mul_im = t >>> 17;
    end
endfunction

parameter signed [17:0] W1r =  92682,  W1i = -92682;
parameter signed [17:0] W2r =      0,  W2i = -131072;
parameter signed [17:0] W3r = -92682,  W3i = -92682;

always @(posedge clk) begin
    dout_valid <= v3;

    if (v3) begin
        r0 <= s2r[0] + s2r[4];
        i0 <= s2i[0] + s2i[4];
        r4 <= s2r[0] - s2r[4];
        i4 <= s2i[0] - s2i[4];

        r1 <= s2r[1] + mul_re(W1r, W1i, s2r[5], s2i[5]);
        i1 <= s2i[1] + mul_im(W1r, W1i, s2r[5], s2i[5]);
        r5 <= s2r[1] - mul_re(W1r, W1i, s2r[5], s2i[5]);
        i5 <= s2i[1] - mul_im(W1r, W1i, s2r[5], s2i[5]);

        r2 <= s2r[2] + mul_re(W2r, W2i, s2r[6], s2i[6]);
        i2 <= s2i[2] + mul_im(W2r, W2i, s2r[6], s2i[6]);
        r6 <= s2r[2] - mul_re(W2r, W2i, s2r[6], s2i[6]);
        i6 <= s2i[2] - mul_im(W2r, W2i, s2r[6], s2i[6]);

        r3 <= s2r[3] + mul_re(W3r, W3i, s2r[7], s2i[7]);
        i3 <= s2i[3] + mul_im(W3r, W3i, s2r[7], s2i[7]);
        r7 <= s2r[3] - mul_re(W3r, W3i, s2r[7], s2i[7]);
        i7 <= s2i[3] - mul_im(W3r, W3i, s2r[7], s2i[7]);
    end
end
endmodule
