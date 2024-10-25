#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test_gen_ahb_waves.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 25.10.2024
import cocotb
import os
import random

from const import cfg
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock
from cocotbext.ahb import AHBBus, AHBMaster, AHBSlave
from cocotb.runner import get_runner


def rnd_val(bit: int = 0, zero: bool = True):
    if zero is True:
        return random.randint(0, (2**bit) - 1)
    else:
        return random.randint(1, (2**bit) - 1)


async def setup_dut(dut, cycles):
    cocotb.start_soon(Clock(dut.hclk, *cfg.CLK_100MHz).start())
    dut.hresetn.value = 0
    await ClockCycles(dut.hclk, cycles)
    dut.hresetn.value = 1


@cocotb.test()
async def run_test(dut, bp_fn=None, pip_mode=False):
    N = 10

    await setup_dut(dut, cfg.RST_CYCLES)

    ahb_master = AHBMaster(AHBBus.from_entity(dut), dut.hclk, dut.hresetn, def_val="Z")
    ahb_slave = AHBSlave(AHBBus.from_entity(dut), dut.hclk, dut.hresetn, bp=bp_fn)

    type(ahb_slave)

    address = [rnd_val(32) for _ in range(N)]
    value = [rnd_val(32) for _ in range(N)]
    size = [random.choice([1, 2, 4]) for _ in range(N)]

    resp = await ahb_master.write(address, value, pip=pip_mode, verbose=True)
    resp = await ahb_master.read(address, pip=pip_mode, verbose=True)


def test_gen_ahb_waves():
    """
    Test generating waveforms in AHB protocol

    Test ID: 1
    """
    test_name = os.path.splitext(os.path.basename(__file__))[0]

    SIM_BUILD = os.path.join(
        cfg.TESTS_DIR, f"../run_dir/{test_name}_{cfg.SIMULATOR}"
    )

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
