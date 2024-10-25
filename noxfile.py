#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : noxfile.py
# License           : MIT license <Check LICENSE>
# Author            : Anderson I. da Silva (aignacio) <anderson@aignacio.com>
# Date              : 25.10.2024
# Last Modified Date: 25.10.2024
import nox


@nox.session(
    python=["3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12"], reuse_venv=True
)
def run(session):
    session.env["DUT"] = "ahb_template"
    session.env["SIM"] = "icarus"
    session.env["TIMEUNIT"] = "1ns"
    session.env["TIMEPREC"] = "1ps"
    session.install(
        "pytest",
        "pytest-xdist",
        "pytest-sugar",
        "pytest-cov",
        "pytest-split",
        "cocotb>=1.8.0",
        "cocotbext-ahb>=0.4.4",
    )
    session.install("-e", ".")
    session.run(
        "pytest",
        "--cov=cocotbext",
        "--cov-branch",
        "--cov-report=xml",
        # "-rf",
        "-rP",
        "-n",
        "auto",
        *session.posargs
    )


@nox.session(python=["3.9", "3.10", "3.11", "3.12"], reuse_venv=True)
def lint(session):
    session.install("flake8")
    session.run("flake8")
