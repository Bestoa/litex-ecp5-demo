#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Lucas Teske <lucas@teske.com.br>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

import ecp5_demo_plat

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litex.soc.interconnect.csr import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_internal_osc=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()

        # Clk / Rst
        if not use_internal_osc:
            clk = platform.request("clk24")
            clk_freq = 24e6
        else:
            clk = Signal()
            div = 5
            self.specials += Instance("OSCG",
                p_DIV = div,
                o_OSC = clk
            )
            clk_freq = 310e6/div

        rst_n = platform.request("cpu_reset_n")

        # PLL
        self.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(~rst_n | self.rst)
        pll.register_clkin(clk, clk_freq)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6, toolchain="trellis",
        with_led_chaser        = True,
        with_spi_flash         = False,
        use_internal_osc       = False,
        **kwargs):

        platform = ecp5_demo_plat.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, use_internal_osc=use_internal_osc)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, int(sys_clk_freq), ident="LiteX SoC on ECP5-demo", **kwargs)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            ledn = platform.request_all("user_led_n")
            self.leds = LedChaser(pads=ledn, sys_clk_freq=sys_clk_freq)

        # SPI Flash --------------------------------------------------------------------------------
        if with_spi_flash:
            from litespi.modules import W25Q32JV
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=W25Q32JV(Codes.READ_1_1_1))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=ecp5_demo_plat.Platform, description="LiteX SoC on Colorlight i5.")
    parser.add_target_argument("--sys-clk-freq", default=50e6, help="System clock frequency.")
    parser.add_target_argument("--with-spi-flash",   action="store_true",  help="Enable SPI Flash (MMAPed).")
    parser.add_target_argument("--use-internal-osc", action="store_true",  help="Use internal oscillator.")

    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        toolchain              = args.toolchain,
        use_internal_osc       = args.use_internal_osc,
        with_spi_flash         = args.with_spi_flash,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
