`timescale 1ns/1ps
module tb_fir_optimized;

    reg clk;
    reg signed [15:0] x;
    wire signed [31:0] y;

    integer i, file_in, file_out, status;
    reg signed [15:0] mem_x;
    reg [255:0] in_name, out_name;

    fir_optimized #(100) dut (.clk(clk), .x(x), .y(y));

    always #5 clk = ~clk;

    initial begin
        clk = 0;
        for (i = 1; i <= 3; i = i + 1) begin

            $sformat(in_name,  "signal_%0d.dat", i);
            $sformat(out_name, "output_optimized_%0d.dat", i);

            file_in  = $fopen(in_name, "r");
            file_out = $fopen(out_name, "w");

            if (file_in == 0) begin
                $display("Error opening %s", in_name);
                $finish;
            end

            while (!$feof(file_in)) begin
                status = $fscanf(file_in, "%d", mem_x);
                if (status == 1) begin
                    x <= mem_x;
                    @(posedge clk);
                    $fdisplay(file_out, "%d", y);
                end
            end

            // Flush pipeline
            x <= 0;
            repeat(120) @(posedge clk);

            $fclose(file_in);
            $fclose(file_out);
        end

        $finish;
    end
endmodule
