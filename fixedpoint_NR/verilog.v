module nr_divider (
    input clk,
    input reset,
    input start,
    input [15:0] numerator,    
    input [15:0] denominator,  
    output reg signed [31:0] quotient, 
    output reg done
);

    localparam signed [31:0] TWO_FP = 32'sd131072;
    localparam signed [31:0] CONST_A = 32'sd191857;
    localparam signed [31:0] CONST_B = 32'sd131072;
    localparam IDLE = 3'd0, NORM = 3'd1, ITER1 = 3'd2, ITER2 = 3'd3, ITER3 = 3'd4, ITER4 = 3'd5, FINISH = 3'd6;
    reg [2:0] state;
    reg signed [31:0] x_i;
    reg signed [31:0] d_norm;
    reg [4:0] shift_k;
    reg signed [31:0] num_fp;

    wire [31:0] shifted_denom;

    assign shifted_denom = ({16'b0, denominator} << 16) >> shift_k;

    function signed [31:0] fp_mult;
        input signed [31:0] a;
        input signed [31:0] b;
        reg signed [63:0] temp;
        begin
            temp = a * b;
            fp_mult = temp[47:16];
        end
    endfunction

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            state <= IDLE;
            done <= 0;
            quotient <= 0;
        end else begin
            case (state)
                IDLE: begin
                    done <= 0;
                    if (start) begin
                        num_fp <= {16'b0, numerator} << 16;
                        if (denominator[15]) shift_k <= 16;
                        else if (denominator[14]) shift_k <= 15;
                        else if (denominator[13]) shift_k <= 14;
                        else if (denominator[12]) shift_k <= 13;
                        else if (denominator[11]) shift_k <= 12;
                        else if (denominator[10]) shift_k <= 11;
                        else if (denominator[9])  shift_k <= 10;
                        else if (denominator[8])  shift_k <= 9;
                        else if (denominator[7])  shift_k <= 8;
                        else if (denominator[6])  shift_k <= 7;
                        else if (denominator[5])  shift_k <= 6;
                        else if (denominator[4])  shift_k <= 5;
                        else if (denominator[3])  shift_k <= 4;
                        else if (denominator[2])  shift_k <= 3;
                        else if (denominator[1])  shift_k <= 2;
                        else shift_k <= 1;
                        state <= NORM;
                    end
                end
                NORM: begin
                    d_norm <= shifted_denom;
                    x_i <= CONST_A - fp_mult(CONST_B, shifted_denom);

                    state <= ITER1;
                end
                ITER1: begin
                    x_i <= fp_mult(x_i, (TWO_FP - fp_mult(x_i, d_norm)));
                    state <= ITER2;
                end
                ITER2: begin
                    x_i <= fp_mult(x_i, (TWO_FP - fp_mult(x_i, d_norm)));
                    state <= ITER3;
                end
                ITER3: begin
                    x_i <= fp_mult(x_i, (TWO_FP - fp_mult(x_i, d_norm)));
                    state <= ITER4;
                end
                ITER4: begin
                    x_i <= fp_mult(x_i, (TWO_FP - fp_mult(x_i, d_norm)));
                    state <= FINISH;
                end
                FINISH: begin
                    quotient <= fp_mult(num_fp, (x_i >> shift_k));
                    done <= 1;
                    state <= IDLE;
                end
            endcase
        end
    end
endmodule
