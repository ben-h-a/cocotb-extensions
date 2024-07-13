import logging
from enum import IntEnum, auto

class ProtPrivileged(IntEnum):
    NORMAL = 0
    PRIVILEGED = 1 << 0

class ProtSecurity(IntEnum):
    NON_SECURE = 0
    SECURE = 1 << 1

class ProtTrans(IntEnum):
    INSTRUCTION = 0
    DATA = 1 << 2

class Prot:
    def __init__(self, bitwise_value=0):
        self.bitwise_value = bitwise_value

    @property
    def mode(self):
        return ProtPrivileged(self.bitwise_value & 1)

    @mode.setter
    def mode(self, mode):
        if mode == ProtPrivileged.PRIVILEGED:
            self.bitwise_value |= ProtPrivileged.PRIVILEGED
        else:
            self.bitwise_value &= ~ProtPrivileged.PRIVILEGED

    @property
    def security(self):
        return ProtSecurity(self.bitwise_value & (1 << 1))

    @security.setter
    def security(self, security):
        if security == ProtSecurity.SECURE:
            self.bitwise_value |= ProtSecurity.SECURE
        else:
            self.bitwise_value &= ~ProtSecurity.SECURE

    @property
    def transaction_type(self):
        return ProtTrans(self.bitwise_value & (1 << 2))

    @transaction_type.setter
    def transaction_type(self, transaction_type):
        if transaction_type == ProtTrans.DATA:
            self.bitwise_value |= ProtTrans.DATA
        else:
            self.bitwise_value &= ~ProtTrans.DATA

    def to_bitwise(self):
        return self.bitwise_value

    @classmethod
    def from_bitwise(cls, bitwise_value):
        return cls(bitwise_value)

    def __repr__(self):
        return (f"BitwiseFlags(mode={self.mode.name}, "
                f"security={self.security.name}, "
                f"transaction_type={self.transaction_type.name}, "
                f"bitwise_value={self.bitwise_value})")


