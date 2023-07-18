# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Points3D

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Rgb(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 3

    # Rgb
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Rgb
    def R(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # Rgb
    def G(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(1))
    # Rgb
    def B(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(2))

def CreateRgb(builder, r, g, b):
    builder.Prep(1, 3)
    builder.PrependUint8(b)
    builder.PrependUint8(g)
    builder.PrependUint8(r)
    return builder.Offset()
