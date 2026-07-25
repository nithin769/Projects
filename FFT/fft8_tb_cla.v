`timescale 1ns/1ps
module fft8_tb;

reg clk;
reg rst_n;
reg din_valid;
reg signed [7:0] din_re;
reg signed [7:0] din_im;

wire dout_valid;
wire signed [23:0] r0, i0, r1, i1, r2, i2, r3, i3;
wire signed [23:0] r4, i4, r5, i5, r6, i6, r7, i7;

fft8_pipeline uut (
    .clk(clk),
    .rst_n(rst_n),
    .din_valid(din_valid),
    .din_re(din_re),
    .din_im(din_im),
    .dout_valid(dout_valid),
    .r0(r0), .i0(i0),  .r1(r1), .i1(i1),
    .r2(r2), .i2(i2),  .r3(r3), .i3(i3),
    .r4(r4), .i4(i4),  .r5(r5), .i5(i5),
    .r6(r6), .i6(i6),  .r7(r7), .i7(i7)
);

initial clk = 1'b0;
always #5 clk = ~clk;

integer tc_num;
initial tc_num = 0;

task send_samples;
    input integer testcase;
    integer k;
    begin
        for (k = 0; k < 8; k = k + 1) begin
            @(posedge clk);
            #1;
            din_valid = 1'b1;
            case (testcase)
            1: begin
                case (k)
                    0: begin din_re =  100; din_im = 0; end
                    1: begin din_re =   71; din_im = 0; end
                    2: begin din_re =    0; din_im = 0; end
                    3: begin din_re =  -71; din_im = 0; end
                    4: begin din_re = -100; din_im = 0; end
                    5: begin din_re =  -71; din_im = 0; end
                    6: begin din_re =    0; din_im = 0; end
                    7: begin din_re =   71; din_im = 0; end
                endcase
            end
            2: begin
                din_re = (k == 0) ? 8'd127 : 8'd0;
                din_im = 8'd0;
            end
            3: begin
                din_re = 8'd64;
                din_im = 8'd0;
            end
            4: begin
                case (k)
                    0: begin din_re =  100; din_im =    0; end
                    1: begin din_re =    0; din_im =  100; end
                    2: begin din_re = -100; din_im =    0; end
                    3: begin din_re =    0; din_im = -100; end
                    4: begin din_re =  100; din_im =    0; end
                    5: begin din_re =    0; din_im =  100; end
                    6: begin din_re = -100; din_im =    0; end
                    7: begin din_re =    0; din_im = -100; end
                endcase
            end
            5: begin
                case (k)
                    0: begin din_re =  100; din_im = 0; end
                    1: begin din_re =    0; din_im = 0; end
                    2: begin din_re = -100; din_im = 0; end
                    3: begin din_re =    0; din_im = 0; end
                    4: begin din_re =  100; din_im = 0; end
                    5: begin din_re =    0; din_im = 0; end
                    6: begin din_re = -100; din_im = 0; end
                    7: begin din_re =    0; din_im = 0; end
                endcase
            end
            endcase
        end
        @(posedge clk);
        #1;
        din_valid = 1'b0;
    end
endtask

task wait_done;
    begin
        @(posedge dout_valid);
        @(posedge clk);
    end
endtask

initial begin
    rst_n     = 1'b0;
    din_valid = 1'b0;
    din_re    = 8'd0;
    din_im    = 8'd0;
    tc_num    = 0;

    repeat(2) @(posedge clk);
    #1;
    rst_n = 1'b1;
    @(posedge clk);

    send_samples(1);  wait_done;
    send_samples(2);  wait_done;
    send_samples(3);  wait_done;
    send_samples(4);  wait_done;
    send_samples(5);  wait_done;

    #50;
    $display("\n==== Simulation complete ====");
    $finish;
end

always @(posedge clk) begin
    if (dout_valid) begin
        tc_num = tc_num + 1;

        $display("\n╔════════════════════════════════════════╗");
        $display("║  FFT OUTPUT  TC%0d  (t = %0t ns)      ║", tc_num, $time);
        $display("╠════╦═══════════════╦═══════════════════╣");
        $display("║ k  ║  Re           ║  Im               ║");
        $display("╠════╬═══════════════╬═══════════════════╣");
        $display("║  0 ║ %13d ║ %17d ║", r0, i0);
        $display("║  1 ║ %13d ║ %17d ║", r1, i1);
        $display("║  2 ║ %13d ║ %17d ║", r2, i2);
        $display("║  3 ║ %13d ║ %17d ║", r3, i3);
        $display("║  4 ║ %13d ║ %17d ║", r4, i4);
        $display("║  5 ║ %13d ║ %17d ║", r5, i5);
        $display("║  6 ║ %13d ║ %17d ║", r6, i6);
        $display("║  7 ║ %13d ║ %17d ║", r7, i7);
        $display("╚════╩═══════════════╩═══════════════════╝");

        case (tc_num)
            1: begin // Cosine k=1 — expect spikes at k=1 and k=7 ≈ 400
                if (r1 === 24'd400 && r7 >= 24'd399 && r7 <= 24'd402)
                    $display("  TC1 PASS  (k=1 Re=%0d, k=7 Re=%0d)", r1, r7);
                else
                    $display("  TC1 FAIL  (expected k1=400, k7=400, got k1=%0d k7=%0d)", r1, r7);
            end
            2: begin // Impulse — all bins = 127
                if (r0===127 && r1===127 && r2===127 && r3===127 &&
                    r4===127 && r5===127 && r6===127 && r7===127)
                    $display("  TC2 PASS  (all bins = 127)");
                else
                    $display("  TC2 FAIL");
            end
            3: begin // DC — X[0]=512, rest=0
                if (r0===512 && r1===0 && r2===0 && r3===0 &&
                    r4===0   && r5===0 && r6===0 && r7===0)
                    $display("  TC3 PASS  (X[0]=512, others=0)");
                else
                    $display("  TC3 FAIL  (X[0]=%0d)", r0);
            end
            4: begin // Complex exp k=2 — X[2]=800, rest=0
                if (r2===800 && r0===0 && r1===0 && r3===0 &&
                    r4===0   && r5===0 && r6===0 && r7===0)
                    $display("  TC4 PASS  (X[2]=800, others=0)");
                else
                    $display("  TC4 FAIL  (X[2]=%0d)", r2);
            end
            5: begin // Two-tone k=2,k=6 — X[2]=400, X[6]=400, rest=0
                if (r2===400 && r6===400 && r0===0 && r1===0 &&
                    r3===0   && r4===0   && r5===0 && r7===0)
                    $display("  TC5 PASS  (X[2]=400, X[6]=400)");
                else
                    $display("  TC5 FAIL  (X[2]=%0d, X[6]=%0d)", r2, r6);
            end
        endcase
    end
end
endmodule
