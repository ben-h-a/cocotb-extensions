from asyncio import set_event_loop
from typing import Any, List, Optional, Sequence, Tuple, Union

import logging
from enum import Enum
from sys import maxsize
import cocotb
from cocotb.queue import Queue, QueueFull
from cocotb.utils import get_sim_time
from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.triggers import ClockCycles, Combine, Lock, ReadOnly, RisingEdge

#Local module imports

class SramTransactionError(Exception):
    def __init__(self,  message: str):
        super().__init__(message)


class Sram(BusDriver):
    _signals = [
        "ADDR",
        "WE",
        "WDATA",
        "RDATA",
        ]
    _optional_signals = [
        "CE",
        ]
    def __init__(self, entity:SimHandleBase, name:str, clock:SimHandleBase, **kwargs:Any) -> None:
        """
        Sram interface
        """
        BusDriver.__init__(self, entity, name, clock, **kwargs)
        self.clock = clock

        print(name)
        self.bus.ADDR.setimmediatevalue(0)
        self.bus.WE.setimmediatevalue(0)
        self.bus.WDATA.setimmediatevalue(0)
        self.bus.RDATA.setimmediatevalue(0)

        for signal in self._optional_signals:
            try:
                getattr(self.bus, signal).setimmediatevalue(0)
            except AttributeError:
                pass
        #Set mutex for each channel
        self.transact_busy = Lock(name + "_busy")

    def _set_otp_signal(self, signal:str, val:int):
        try:
            getattr(self.bus, signal).value = val
        except AttributeError:
            pass

    @cocotb.coroutine
    async def transact(self, address:int, wdata:Union[int, None]=None, byte_en = None)-> Union[int, None]:
        async with self.transact_busy:
            write = wdata is not None
            await RisingEdge(self.clock)
            self.bus.ADDR.value = address
            self._set_otp_signal("CE", 1)
            if write:
                self.bus.WE.value = byte_en if byte_en else (1<<len(self.bus.WE))-1
                self.bus.WDATA.value = wdata
            else:
                self.bus.WE.value = 0
            await ReadOnly()
            if not write:
                rdata = self.bus.RDATA.value
            else:
                rdata = None
            await RisingEdge(self.clock)

            self.bus.WE.value = 0
            self._set_otp_signal("CE", 0)
            return rdata



