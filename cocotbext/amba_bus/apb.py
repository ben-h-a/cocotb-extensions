from asyncio import set_event_loop
from typing import Any, List, Optional, Sequence, Tuple, Union

import logging
from enum import Enum
import cocotb
from cocotb.queue import Queue, QueueFull
from cocotb.utils import get_sim_time
from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.triggers import ClockCycles, Combine, Lock, ReadOnly, RisingEdge

#Local module imports
from .amba_common import Prot, ProtPrivileged, ProtTrans, ProtSecurity 
class DataItem(object):
    data:int
    address:int
    write_en:bool
    byte_en:int
class APBTransactionError(Exception):
    def __init__(self,  message: str):
        super().__init__(message)


class APB(BusDriver):
    _signals = [
        "PADDR",
        "PWDATA",
        "PWRITE",
        "PRDATA",
        "PSEL",
        "PENABLE",
        "PREADY",
        "PSLVERR"
    ]
    _optional_signals = [
        "PAUSER",
        "PWUSER",
        "PRUSER",
        "BUSER",
        "PWAKEUP",
        "PPROT", 
        "PSTRB",

    ]
    def __init__(self, entity:SimHandleBase, name:str, clock:SimHandleBase, **kwargs:Any) -> None:
        """
        AMBA APB interface
        """
        BusDriver.__init__(self, entity, name, clock, **kwargs)
        self.clock = clock

        self.bus.PADDR.setimmediatevalue(0)
        self.bus.PWDATA.setimmediatevalue(0)
        self.bus.PWRITE.setimmediatevalue(0)
        self.bus.PSEL.setimmediatevalue(0)
        self.bus.PENABLE.setimmediatevalue(0)

        
        #Set mutex for each channel
        self.transact_busy = Lock(name + "_busy")

    async def set_bus_idle(self):
        self.bus.PSEL.value = 0
        self.bus.PENABLE.value = 0
 
    @cocotb.coroutine
    async def transact(self, address:int, wdata:Union[int, None]=None)-> Union[int, None]:
        async with self.transact_busy:
            write = wdata is not None
            await RisingEdge(self.clock)
            self.bus.PADDR.value = address
            self.bus.PSEL.value = 1
            self.bus.PENABLE.value = 0
            if write:
                self.bus.PWDATA.value = wdata
                self.bus.PWRITE.value = 1
            else:
                self.bus.PWRITE.value = 0
            await RisingEdge(self.clock)
            self.bus.PENABLE.value = 1
            await RisingEdge(self.bus.PREADY)
            if self.bus.PSLVERR.value:
                msg = f"Addr: {address}" + f", wdata: {wdata}" if write else ""
                raise APBTransactionError(msg)
            await RisingEdge(self.clock)
            await self.set_bus_idle()
            if not write:
                return self.bus.PRDATA.value
            return None



