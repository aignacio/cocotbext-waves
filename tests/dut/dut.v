module ahb_template #(
  parameter ADDR_WIDTH = 32,
  parameter DATA_WIDTH = 32
)(
  input                       hclk,
  input                       hresetn,

  //----------------------------------------
  // SLAVE - IN
  //---------------------------------------
  // From master/interconnect to slave/decoder 
  inout                       hsel,
  inout   [(ADDR_WIDTH-1):0]  haddr,
  inout   [2:0]               hburst,
  inout   [2:0]               hsize,
  inout   [1:0]               htrans,
  inout   [(DATA_WIDTH-1):0]  hwdata,
  inout                       hwrite,
  inout                       hready_in,
  // From slave to interconnect/master 
  inout   [(DATA_WIDTH-1):0]  hrdata,
  inout                       hready,
  inout                       hresp
);
endmodule
