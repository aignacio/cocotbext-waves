[![Lint > Tests > Publish](https://github.com/aignacio/cocotbext-waves/actions/workflows/run.yaml/badge.svg)](https://github.com/aignacio/cocotbext-waves/actions/workflows/run.yaml)

# Cocotb Waves

## Table of Contents
* [Introduction](#intro)
* [Installation](#install)
* [Usage](#usage)
* [Classes & Methods](#methods)

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
    ],
    group="MOSI",
)
waves.add_signal(
    [
        dut.hrdata,
        dut.hready,
        dut.hresp,
    ],
    group="MISO",
)
waves.start()
...
<Running sim, issuing txns>
...
waves.save()
waves.save_txt()
```

**Output:**

![ahb](ahb_test.svg)

## <a name="methods"></a> Classes & Methods

### Class waveform

```python
class waveform:
    def __init__(
        self,
        clk,
        name,
        hscale: int = 2,
        is_posedge: bool = True,
        debug: bool = False,
        start: bool = True
    ) -> None:
```

* **clk**: Synchronous clock used as the sample the signals
* **name**: Defines the object / filename, also part of the diagram header
* **hscale**: Horizontal scale for the SVG
* **is_posedge**: Defines clock model
* **debug**: Enable some debug messages
* **start**: Starts the signal monitoring

### .start()/.stop()

Optional start/stop the sampling to create the diagram.y

### .add_trigger(handle, val)

Adds a trigger to start sampling the signal, starts when handle.value == val.

### .add_signal(color, is_clock, is_posedge_clock, clock_period, group)

Adds a signal to be monitored in the diagram. If it is a clock, other arguments
can be populated, please note that signals from the same *group* have to be
declared in a single method call.

### .set_head/foot(text, tick, every)

Set header/foot propertries of the diagram, more info on wavedrom website.

### .save_svg()

Stops the sampling and convert into SVG the final diagram.

### .save_txt()

Stops the sampling and convert into .txt fmt the json.
