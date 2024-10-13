#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Lucas Teske <lucas@teske.com.br>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeECP5Platform
from litex.build.lattice.programmer import EcpDapProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk24", 0, Pins("K16"), IOStandard("LVCMOS33")),

    # Led
    ("user_led_n", 0, Pins("E15"), IOStandard("LVCMOS33")),
    ("user_led_n", 1, Pins("E14"), IOStandard("LVCMOS33")),
    ("user_led_n", 2, Pins("D14"), IOStandard("LVCMOS33")),
    ("user_led_n", 3, Pins("C14"), IOStandard("LVCMOS33")),

    # Reset button
    ("cpu_reset_n", 0, Pins("C4"), IOStandard("LVCMOS33"), Misc("PULLMODE=UP")),

    # Serial
    ("serial", 0, # iCELink
        Subsignal("tx", Pins("A8")),
        Subsignal("rx", Pins("A7")),
        IOStandard("LVCMOS33")
    ),

    # SPIFlash (W25Q32JV)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("N8")),
        # https://github.com/m-labs/nmigen-boards/pull/38
        #Subsignal("clk",  Pins("")), driven through USRMCLK
        Subsignal("mosi", Pins("T8")),
        Subsignal("miso", Pins("T7")),
        IOStandard("LVCMOS33"),
    ),
]

# from colorlight_i5.py adapted to icesugar pro
# https://github.com/wuxx/icesugar-pro/blob/master/doc/iCESugar-pro-pinmap.png
_connectors = [
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeECP5Platform):
    default_clk_name   = "clk24"
    default_clk_period = 1e9/24e6

    def __init__(self, toolchain="trellis"):
        device     = "LFE5U-25F-6BG256C"
        io         = _io
        connectors = _connectors
        LatticeECP5Platform.__init__(self, device, io, connectors=connectors, toolchain=toolchain)

    def create_programmer(self):
        return EcpDapProgrammer()

    def do_finalize(self, fragment):
        LatticeECP5Platform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk24", loose=True), 1e9/24e6)
