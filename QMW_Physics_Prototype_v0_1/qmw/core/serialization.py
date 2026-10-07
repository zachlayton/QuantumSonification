"""Portable JSON representation with explicit complex real/imag components."""
from dataclasses import fields, is_dataclass
from enum import Enum
import numpy as np


def jsonable(value):
    if is_dataclass(value):
        return {f.name: jsonable(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Enum): return value.value
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value): return {"real": value.real.tolist(), "imag": value.imag.tolist()}
        return value.tolist()
    if isinstance(value, np.generic): return jsonable(value.item())
    if isinstance(value, complex): return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict): return {str(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [jsonable(v) for v in value]
    return value
