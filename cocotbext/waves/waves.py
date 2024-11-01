#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : waves.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 01.11.2024
import cocotb
import wavedrom
import json
import copy
import logging
import datetime

from .version import __version__
from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge, FallingEdge


class signal_data:
    def __init__(
        self,
        name,
        handle,
        is_clock,
        is_posedge_clock,
        color_data=None,
        previous_val=None,
        clock_period=1,
        group=None,
    ) -> None:
        self.name = name
        self.handle = handle
        self.color_data = color_data
        self.is_clock = is_clock
        self.is_posedge_clock = is_posedge_clock
        self.previous_val = previous_val
        self.clock_period = clock_period
        self.group = group


class waveform:
    def __init__(
        self,
        clk,
        name,
        hscale: int = 2,
        is_posedge: bool = True,
        debug: bool = False,
        start: bool = True,
    ) -> None:
        self.handles = []  # List to store [signal_data] obj
        self.waves = {}
        self.waves["signal"] = []
        self.trigger = {"trigger": None, "value": 0}

        self.head = {"text": name, "tick": 0, "every": 1}
        self.foot = {"text": "Generated by cocotbext-waves", "tick": 0, "every": 1}

        self._start = False
        self.close = False
        self.hscale = hscale
        self.debug = debug
        self.is_posedge = is_posedge
        self.clk = clk
        self.name = name
        self.color_idx = 3  # Start color for multi-bit signal

        self.add_signal(clk, color=None, is_clock=True, is_posedge_clock=is_posedge)

        self.log = logging.getLogger(f"cocotb.waves.{name}")
        self.log.info(f"Waveform / Wavedrom - ({name})")
        self.log.info("cocotbext-waves version %s", __version__)
        self.log.info(
            f"Copyright (c) {datetime.datetime.now().year} Anderson Ignacio da Silva"
        )
        self.log.info("https://github.com/aignacio/cocotbext-waves")

        if start:
            self.start()

    def add_trigger(self, handle, val):
        self.trigger = {"trigger": handle, "value": val}

    def add_signal(
        self,
        sig,
        color=None,
        is_clock: bool = False,
        is_posedge_clock: bool = True,
        clock_period=1,
        group=None,
    ):
        if not isinstance(sig, list):
            sig = [sig]

        sig_list = []

        for signal in sig:
            if signal.__len__() == 1:
                sig_list.append(
                    {
                        "name": signal._name,
                        "wave": "",
                    }
                )

                self.handles.append(
                    signal_data(
                        name=signal._name,
                        handle=signal,
                        is_clock=is_clock,
                        is_posedge_clock=is_posedge_clock,
                        clock_period=clock_period,
                        group=group,
                    )
                )
            else:
                sig_list.append(
                    {
                        "name": signal._name,
                        "wave": "",
                        "data": "",
                    }
                )

                if color is None:
                    # Automatically assigns a color
                    if self.color_idx == 9:
                        color_tmp = 3
                    else:
                        color_tmp = self.color_idx
                        self.color_idx = color_tmp + 1
                else:
                    # Take user's input
                    color_tmp = color

                # Append to the list that will be used later
                self.handles.append(
                    signal_data(
                        name=signal._name,
                        handle=signal,
                        color_data=str(color_tmp),
                        is_clock=is_clock,
                        is_posedge_clock=is_posedge_clock,
                        clock_period=clock_period,
                        group=group,
                    )
                )

        if group is not None:
            self.waves["signal"].append([group] + sig_list)
        else:
            for item in sig_list:
                self.waves["signal"].append(item)

    def start(self):
        if self._start is False:
            self.mon = cocotb.start_soon(self._monitor())
            self._start = True
            if self.debug:
                print("[Waves - Debug] Starting sampling signals")

    async def _monitor(self):
        while True:
            if self.is_posedge is True:
                await RisingEdge(self.clk)
                await FallingEdge(self.clk)
            else:
                await FallingEdge(self.clk)
                await RisingEdge(self.clk)

            if self.trigger["trigger"] is not None:
                if self.trigger["trigger"].value == self.trigger["value"]:
                    self._add_signals()
            else:
                self._add_signals()

    def _add_signals(self):
        for index, signal in enumerate(self.handles):
            self._append_wave_dot(index, signal)

    def _append_wave_dot(self, index, signal):
        if signal.is_clock is True:
            for entry in self.waves["signal"]:
                if isinstance(entry, dict) and entry["name"] == signal.name:
                    if signal.handle.value.is_resolvable is not True:
                        if "z" in signal.handle.value:
                            entry["wave"] += "z"
                        else:
                            entry["wave"] += "x"
                    else:
                        if entry["wave"] == "":
                            entry["wave"] += "P" if signal.is_posedge_clock else "N"
                            entry["period"] = signal.clock_period
                        else:
                            entry["wave"] += "."
                elif isinstance(entry, list):
                    for subentry in entry:
                        if (
                            isinstance(subentry, dict)
                            and subentry.get("name") == signal.name
                        ):
                            if signal.handle.value.is_resolvable is not True:
                                if "z" in signal.handle.value:
                                    subentry["wave"] += "z"
                                else:
                                    subentry["wave"] += "x"
                            else:
                                if subentry["wave"] == "":
                                    subentry["wave"] += (
                                        "P" if signal.is_posedge_clock else "N"
                                    )
                                    subentry["period"] = signal.clock_period
                                else:
                                    subentry["wave"] += "."
        else:
            for entry in self.waves["signal"]:
                if isinstance(entry, dict) and entry["name"] == signal.name:
                    if entry["name"] == signal.name:
                        if signal.previous_val is None:
                            self.handles[index].previous_val = copy.deepcopy(
                                signal.handle.value
                            )

                            if signal.handle.value.is_resolvable is not True:
                                if "z" in signal.handle.value:
                                    entry["wave"] += "z"
                                else:
                                    entry["wave"] += "x"
                            else:
                                if signal.handle.__len__() > 1:
                                    entry["data"] += str(hex(signal.handle.value)) + " "
                                    entry["wave"] += signal.color_data
                                else:
                                    entry["wave"] += str(signal.handle.value)
                        elif signal.handle.value == signal.previous_val:
                            entry["wave"] += "."
                        else:
                            self.handles[index].previous_val = copy.deepcopy(
                                signal.handle.value
                            )

                            if signal.handle.value.is_resolvable is not True:
                                if "z" in signal.handle.value:
                                    entry["wave"] += "z"
                                else:
                                    entry["wave"] += "x"
                            else:
                                if signal.handle.__len__() > 1:
                                    entry["wave"] += signal.color_data
                                    entry["data"] += str(hex(signal.handle.value)) + " "
                                else:
                                    entry["wave"] += str(signal.handle.value)
                elif isinstance(entry, list):
                    for subentry in entry:
                        if (
                            isinstance(subentry, dict)
                            and subentry.get("name") == signal.name
                        ):
                            if signal.previous_val is None:
                                self.handles[index].previous_val = copy.deepcopy(
                                    signal.handle.value
                                )

                                if signal.handle.value.is_resolvable is not True:
                                    if "z" in signal.handle.value:
                                        subentry["wave"] += "z"
                                    else:
                                        subentry["wave"] += "x"
                                else:
                                    if signal.handle.__len__() > 1:
                                        subentry["data"] += (
                                            str(hex(signal.handle.value)) + " "
                                        )
                                        subentry["wave"] += signal.color_data
                                    else:
                                        subentry["wave"] += str(signal.handle.value)
                            elif signal.handle.value == signal.previous_val:
                                subentry["wave"] += "."
                            else:
                                self.handles[index].previous_val = copy.deepcopy(
                                    signal.handle.value
                                )

                                if signal.handle.value.is_resolvable is not True:
                                    if "z" in signal.handle.value:
                                        subentry["wave"] += "z"
                                    else:
                                        subentry["wave"] += "x"
                                else:
                                    if signal.handle.__len__() > 1:
                                        subentry["wave"] += signal.color_data
                                        subentry["data"] += (
                                            str(hex(signal.handle.value)) + " "
                                        )
                                    else:
                                        subentry["wave"] += str(signal.handle.value)

    def set_head(self, text, tick, every):
        self.head = {"text": text, "tick": tick, "every": every}

    def set_foot(self, text, tick, every):
        self.foot = {"text": text, "tick": tick, "every": every}

    def _incl_width(self):
        # Format each multi-bit name entry to include width
        for signal in self.handles:
            for entry in self.waves["signal"]:
                if isinstance(entry, dict) and entry["name"] == signal.name:
                    if signal.handle.__len__() > 1:
                        entry["name"] += "[" + str(signal.handle.__len__() - 1) + ":0]"
                elif isinstance(entry, list):
                    for subentry in entry:
                        if (
                            isinstance(subentry, dict)
                            and subentry.get("name") == signal.name
                        ):
                            if signal.handle.__len__() > 1:
                                subentry["name"] += (
                                    "[" + str(signal.handle.__len__() - 1) + ":0]"
                                )

    def _close(self):
        if self.close is False:
            self.close = True

            self.mon.kill()
            self._incl_width()
            self.waves["config"] = {"hscale": self.hscale}
            self.waves["head"] = self.head
            self.waves["foot"] = self.foot

    def __str__(self):
        return str(json.dumps(self.waves))

    def stop(self):
        self._close()
        if self.debug:
            print("[Waves - Debug] Stopping sims")

    def save_svg(self):
        self._close()
        if self.debug:
            print("[Waves - Debug] Printing JSON Wavedrom")
            print(json.dumps(self.waves))
        svg = wavedrom.render(json.dumps(self.waves))
        svg.saveas(self.name + ".svg")

    def save_txt(self):
        self._close()
        try:
            with open(self.name + ".txt", "w") as file:
                json.dump(self.waves, file, indent=4)  # indent for better readability
            if self.debug:
                print(f"Wavedrom diagram written into {self.name}.txt")
        except Exception as e:
            print(f"An error occurred: {e} while trying to write wavedrom diagram")
