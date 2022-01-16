from enum import IntEnum, auto
import typing
from . import util


class TypeKind(IntEnum):
    """
    Simple RTTI mechanism for `Type`.
    """
    INT = auto()
    FLOAT = auto()
    STR = auto()
    DTYPE = auto()
    TUPLE = auto()
    LIST = auto()


class Type:
    """
    Base class for all expression types.
    """
    kind: TypeKind

    prim_kinds = [TypeKind.INT, TypeKind.FLOAT, TypeKind.STR]

    def __eq__(self, other: 'Type'):
        """
        Compare structural equality of two type.
        :param other: The other type to be compared.
        :return: Whether the two types are structurally equal.
        """
        return self.kind == other.kind


class Int(Type):
    """
    Integer type.
    """
    kind = TypeKind.INT


class Float(Type):
    """
    Float type.
    """
    kind = TypeKind.FLOAT


class Str(Type):
    """
    String type.
    """
    kind = TypeKind.STR


class DType(Type):
    """
    Type for tensor data type.
    """
    kind = TypeKind.DTYPE


class Tuple(Type):
    """
    Type for fixed-length array of possibly heterogeneous elements.
    """
    kind = TypeKind.TUPLE

    def __init__(self, *field_ty: Type):
        self.field_ty_ = field_ty
        self.is_homo_ = self._is_homo()

    def __eq__(self, other: Type):
        if not super().__eq__(other):
            return False
        other = typing.cast(Tuple, other)
        if len(self.field_ty_) != len(other.field_ty_):
            return False
        return all(map(lambda p: p[0] == p[1], zip(self.field_ty_, other.field_ty_)))

    def _is_homo(self):
        if len(self.field_ty_) <= 1:
            return True
        return all(map(lambda t: t == self.field_ty_[0], self.field_ty_[1:]))


class List(Type):
    """
    Type for variable-length array of homogeneous elements.
    """
    kind = TypeKind.LIST

    def __init__(self, elem_ty: Type):
        self.elem_ty_ = elem_ty

    def __eq__(self, other: Type):
        if not super().__eq__(other):
            return False
        other = typing.cast(List, other)
        return self.elem_ty_ == other.elem_ty_


PyTypeable = typing.Union[int, float, str, tuple, list]


def type_py_value(v: PyTypeable) -> Type:
    """
    Find the corresponding type of Python value.
    :param v: Any acceptable Python object.
    :return: Type of `v`.
    """
    if isinstance(v, int):
        return Int()
    elif isinstance(v, float):
        return Float()
    elif isinstance(v, str):
        return Str()
    elif isinstance(v, tuple):
        return Tuple(*(type_py_value(f) for f in v))
    elif isinstance(v, list):
        return List(type_py_value(v[0]))
    else:
        raise TypeError(
            'Cannot type Python object of type \'{}\''.format(
                util.cls_name(v))
        )
