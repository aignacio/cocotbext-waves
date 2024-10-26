#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : test_gen_ahb_waves_ram.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 26.10.2024
import cocotb
import os
import random

from const import cfg
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock
from cocotbext.ahb import AHBBus, AHBMaster, AHBLiteSlaveRAM
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
    cocotb.start_soon(Clock(dut.hclk, *cfg.CLK_100MHz).start())
    dut.hresetn.value = 0
    await ClockCycles(dut.hclk, cycles)
    dut.hresetn.value = 1


@cocotb.test()
async def run_test(dut):
    N = 2
    mem_size_kib = 4

    waves = waveform(clk=dut.hclk, name="ahb_test_sram")
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

    await setup_dut(dut, cfg.RST_CYCLES)

    ahb_lite_sram = AHBLiteSlaveRAM(
        AHBBus.from_entity(dut),
        dut.hclk,
        dut.hresetn,
        mem_size=mem_size_kib * 1024,
    )
    ahb_master = AHBMaster(AHBBus.from_entity(dut), dut.hclk, dut.hresetn, def_val="Z")

    # Below is only required bc of flake8 - non-used rule
    type(ahb_lite_sram)

    address = [(rnd_val(10) & 0xFFFF_FFFFC) for _ in range(N)]
    value = [rnd_val(32) for _ in range(N)]
    size = [random.choice([1, 2, 4]) for _ in range(N)]

    pip_mode = True
    resp = await ahb_master.write(address, value, size, pip=pip_mode)
    resp = await ahb_master.read(address, size, pip=pip_mode)

    waves.save()
    type(resp)
    del waves


def test_gen_ahb_waves_ram():
    """
    Test generating waveforms in AHB protocol

    Test ID: 3
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
