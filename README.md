[![Lint > Tests > Publish](https://github.com/aignacio/cocotbext-waves/actions/workflows/run.yaml/badge.svg)](https://github.com/aignacio/cocotbext-waves/actions/workflows/run.yaml)

# Cocotb Waves

## Table of Contents
* [Introduction](#intro)
* [Installation](#install)
* [Usage](#usage)

## <a name="intro"></a> Introduction

This repository contains wavedrom svg generator for [cocotb](https://github.com/cocotb/cocotb) sims.

## <a name="install"></a> Installation

Installation from pip (release version, stable):
```bash
$ pip install cocotbext-waves
```

## <a name="usage"></a> Usage

Example sampling AHB signals using [`cocotbext-ahb`](https://github.com/aignacio/cocotbext-ahb).

```python
from cocotbext.waves import waveform

...

waves = waveform(
    clk=dut.hclk, name="ahb_test", hscale=3, debug=True
)
waves.add_signal(
    [
        dut.hsel,
        dut.haddr,
        dut.hburst,
        dut.hsize,
        dut.htrans,
        dut.hwdata,
        dut.hwrite,
        dut.hready_in,
        dut.hrdata,
        dut.hready,
        dut.hresp,
    ]
)
...
<Running sim, issuing txns>
...
waves.save()
```

**Output:**

![ahb](ahb_test.svg)


