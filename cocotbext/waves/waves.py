#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : waves.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 25.10.2024
import cocotb
import wavedrom
import json
import copy

from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge, FallingEdge


class waveform:
    def __init__(
        self,
        clk,
        name,
        hscale: int = 2,
        is_posedge: bool = True,
        debug: bool = False,
    ) -> None:
        self.handles = []  # Stores [handle, last_value, color]
        self.waves = {}
        self.waves["signal"] = []
        self.color_idx = 3
        self.hscale = hscale
        self.debug = debug

        self.is_posedge = is_posedge
        self.clk = clk
        self.name = name

        self.waves["signal"].append({"name": clk._name, "wave": ""})
        self.mon = cocotb.start_soon(self._monitor())

    def add_signal(self, sig):
        if not isinstance(sig, list):
            sig = [sig]

        for signal in sig:
            if signal.__len__() == 1:
                self.waves["signal"].append(
                    {
                        "name": signal._name,
                        "wave": "",
                    }
                )
                self.handles.append([signal, None, None])
            else:
                self.waves["signal"].append(
                    {
                        "name": signal._name,
                        "wave": "",
                        "data": "",
                    }
                )

                if self.color_idx == 9:
                    color = 3
                else:
                    color = self.color_idx
                    self.color_idx = color + 1
                self.handles.append([signal, None, str(color)])

    async def _monitor(self):
        while True:
            if self.is_posedge is True:
                await RisingEdge(self.clk)
                await FallingEdge(self.clk)
            else:
                await FallingEdge(self.clk)
                await RisingEdge(self.clk)

            self._append_wave_dot(None, self.clk, self.clk._name, True)

            for index, handle in enumerate(self.handles):
                self._append_wave_dot(index, handle, handle[0]._name, False)

    def _append_wave_dot(self, index, handle, name, is_clock):
        if is_clock is True:
            for entry in self.waves["signal"]:
                if entry["name"] == name:
                    if handle.value.is_resolvable is not True:
                        if "z" in handle.value:
                            entry["wave"] += "z"
                        else:
                            entry["wave"] += "x"
                    else:
                        if entry["wave"] == "":
                            entry["wave"] += "P" if self.is_posedge else "N"
                        else:
                            entry["wave"] += "."
        else:
            for entry in self.waves["signal"]:
                if entry["name"] == name:
                    if handle[1] is None:
                        self.handles[index][1] = copy.deepcopy(handle[0].value)

                        if handle[0].value.is_resolvable is not True:
                            if "z" in handle[0].value:
                                entry["wave"] += "z"
                            else:
                                entry["wave"] += "x"
                        else:
                            if handle[0].__len__() > 1:
                                entry["data"] += str(hex(handle[0].value)) + " "
                                entry["wave"] += self.handles[index][2]
                            else:
                                entry["wave"] += str(handle[0].value)
                    elif handle[0].value == handle[1]:
                        entry["wave"] += "."
                    else:
                        self.handles[index][1] = copy.deepcopy(handle[0].value)

                        if handle[0].value.is_resolvable is not True:
                            if "z" in handle[0].value:
                                entry["wave"] += "z"
                            else:
                                entry["wave"] += "x"
                        else:
                            if handle[0].__len__() > 1:
                                entry["wave"] += self.handles[index][2]
                                entry["data"] += str(hex(handle[0].value)) + " "
                            else:
                                entry["wave"] += str(handle[0].value)

    def save(self):
        self.mon.kill()
        # Format each name entry
        for handle in self.handles:
            for entry in self.waves["signal"]:
                if entry["name"] == handle[0]._name:
                    if handle[0].__len__() > 1:
                        entry["name"] += "[" + str(handle[0].__len__() - 1) + ":0]"

        self.waves["config"] = {"hscale": self.hscale}
        if self.debug:
            print("[Waves - Debug] Printing JSON Wavedrom")
            print(json.dumps(self.waves))
        svg = wavedrom.render(json.dumps(self.waves))
        svg.saveas(self.name + ".svg")
