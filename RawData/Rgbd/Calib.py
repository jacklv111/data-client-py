# automatically generated by the FlatBuffers compiler, do not modify

# namespace: Rgbd

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Calib(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Calib()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsCalib(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Calib
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Calib
    def Extrinsics(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Float32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # Calib
    def ExtrinsicsAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float32Flags, o)
        return 0

    # Calib
    def ExtrinsicsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Calib
    def ExtrinsicsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # Calib
    def Intrinsics(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Float32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # Calib
    def IntrinsicsAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float32Flags, o)
        return 0

    # Calib
    def IntrinsicsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Calib
    def IntrinsicsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

def CalibStart(builder): builder.StartObject(2)
def Start(builder):
    return CalibStart(builder)
def CalibAddExtrinsics(builder, extrinsics): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(extrinsics), 0)
def AddExtrinsics(builder, extrinsics):
    return CalibAddExtrinsics(builder, extrinsics)
def CalibStartExtrinsicsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def StartExtrinsicsVector(builder, numElems):
    return CalibStartExtrinsicsVector(builder, numElems)
def CalibAddIntrinsics(builder, intrinsics): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(intrinsics), 0)
def AddIntrinsics(builder, intrinsics):
    return CalibAddIntrinsics(builder, intrinsics)
def CalibStartIntrinsicsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def StartIntrinsicsVector(builder, numElems):
    return CalibStartIntrinsicsVector(builder, numElems)
def CalibEnd(builder): return builder.EndObject()
def End(builder):
    return CalibEnd(builder)