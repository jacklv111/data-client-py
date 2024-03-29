# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Points3D

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Point3(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 12

    # Point3
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Point3
    def X(self): return self._tab.Get(flatbuffers.number_types.Float32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # Point3
    def Y(self): return self._tab.Get(flatbuffers.number_types.Float32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(4))
    # Point3
    def Z(self): return self._tab.Get(flatbuffers.number_types.Float32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(8))

def CreatePoint3(builder, x, y, z):
    builder.Prep(4, 12)
    builder.PrependFloat32(z)
    builder.PrependFloat32(y)
    builder.PrependFloat32(x)
    return builder.Offset()
