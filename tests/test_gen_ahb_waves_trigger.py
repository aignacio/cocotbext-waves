#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test_gen_ahb_waves_trigger.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 31.10.2024
import cocotb
import os
import random

from const import cfg
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock
from cocotbext.ahb import AHBBus, AHBMaster, AHBSlave
from cocotb.runner import get_runner
from cocotbext.waves import waveform
from cocotb.regression import TestFactory


def pick_random_value(input_list):
    if input_list:
        return random.choice(input_list)
    else:
        return None  # Return None if the list is empty


def rnd_val(bit: int = 0, zero: bool = True):
    if zero is True:
        return random.randint(0, (2**bit) - 1)
    else:
        return random.randint(1, (2**bit) - 1)


async def setup_dut(dut, cycles):
    cocotb.start_soon(Clock(dut.test_nclk, *cfg.CLK_200MHz).start())
    cocotb.start_soon(Clock(dut.hclk, *cfg.CLK_100MHz).start())
    dut.hresetn.value = 0
    await ClockCycles(dut.hclk, cycles)
    dut.hresetn.value = 1


@cocotb.test()
async def run_test(dut):
    N = 2

    waves = waveform(clk=dut.hclk, name="ahb_test", hscale=3, debug=True)
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
    waves.add_signal(
        dut.test_nclk, is_clock=True, is_posedge_clock=False, clock_period=0.50
    )
    waves.add_trigger(dut.hresetn, 1)

    await setup_dut(dut, cfg.RST_CYCLES)

    ahb_master = AHBMaster(AHBBus.from_entity(dut), dut.hclk, dut.hresetn, def_val="Z")
    ahb_slave = AHBSlave(AHBBus.from_entity(dut), dut.hclk, dut.hresetn)

    type(ahb_slave)

    address = [rnd_val(32) for _ in range(N)]
    value = [rnd_val(32) for _ in range(N)]
    size = [random.choice([1, 2, 4]) for _ in range(N)]

    resp = await ahb_master.write(address, value, size, verbose=True)
    resp = await ahb_master.read(address, size, verbose=True)
    waves.save_txt()
    waves.save_svg()
    type(resp)
    del waves


def test_gen_ahb_waves_trigger():
    """
    Test generating waveforms in AHB protocol

    Test ID: 2
    """
    test_name = os.path.splitext(os.path.basename(__file__))[0]

    SIM_BUILD = os.path.join(cfg.TESTS_DIR, f"../run_dir/{test_name}_{cfg.SIMULATOR}")

    runner = get_runner(cfg.SIMULATOR)
    runner.build(
        verilog_sources=cfg.VERILOG_SOURCES,
        hdl_toplevel=cfg.TOPLEVEL,
        build_args=cfg.EXTRA_ARGS,
        timescale=cfg.TIMESCALE,
        waves=True,
        build_dir=SIM_BUILD,
    )

    runner.test(
        hdl_toplevel=cfg.TOPLEVEL,
        timescale=cfg.TIMESCALE,
        test_module=test_name,
        waves=True,
        test_dir=SIM_BUILD,
    )
