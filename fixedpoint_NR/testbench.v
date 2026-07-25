`timescale 1ns / 1ps

module tb_nr_divider();

    reg clk;
    reg reset;
    reg start;
    reg [15:0] numerator;
    reg [15:0] denominator;

    wire signed [31:0] quotient;
    wire done;
    integer file;

    nr_divider dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .numerator(numerator),
        .denominator(denominator),
        .quotient(quotient),
        .done(done)
    );

    always #5 clk = ~clk;
    initial begin
        clk = 0;
        reset = 1;
        start = 0;
        file = $fopen("verilog_results.txt", "w");

        #100;
        reset = 0;
        #20;

        //Test Case 1
        numerator = 15;
        denominator = 23;

        start = 1; #10; start = 0;
        wait(done);
        $fwrite(file, "%0d %0d %0d\n", numerator, denominator, quotient);

        #50;

        //Test Case 2
        numerator = 10;
        denominator = 79;
        start = 1; #10; start = 0;
        wait(done);
        $fwrite(file, "%0d %0d %0d\n", numerator, denominator, quotient);

        #50;
        
        //Test Case 3
        numerator = 14;
        denominator = 41;
        start = 1; #10; start = 0;
        wait(done);
        $fwrite(file, "%0d %0d %0d\n", numerator, denominator, quotient);
        
        #50
        
        //Test Case 4
        numerator = 35;
        denominator = 277;
        start = 1; #10; start = 0;
        wait(done);
        $fwrite(file, "%0d %0d %0d\n", numerator, denominator, quotient);

        $fclose(file);
        $finish;
    end
endmodule
