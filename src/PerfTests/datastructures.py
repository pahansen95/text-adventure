from __future__ import annotations
from typing import TypedDict, NamedTuple
from dataclasses import dataclass
from attr import define
from functools import cached_property
from types import SimpleNamespace
from collections import OrderedDict
import array, ctypes, weakref, mmap, operator, time, struct

from . import BenchmarkRegistry, attrib_benchmark, mapping_benchmark, factory_kwarg_benchmark, factory_arg_benchmark

@BenchmarkRegistry.register
class PersonClass:
  def __init__(self, name: str, age: int):
    self.name = name
    self.age = age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonClass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonClass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonSlotsClass:
  __slots__ = ("name", "age")
  def __init__(self, name: str, age: int):
    self.name = name
    self.age = age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonSlotsClass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonSlotsClass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@dataclass
class PersonDataclass:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonDataclass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonDataclass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@dataclass(frozen=True)
class PersonFrozenDataclass:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonFrozenDataclass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonFrozenDataclass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@dataclass(slots=True)
class PersonSlotsDataclass:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonSlotsDataclass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonSlotsDataclass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@dataclass(frozen=True, slots=True)
class PersonFrozenSlotsDataclass:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonFrozenSlotsDataclass, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonFrozenSlotsDataclass) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonNamedTuple(NamedTuple):
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonNamedTuple, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonNamedTuple) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonTypedDict(TypedDict):
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonTypedDict, int]:
    # NOTE: We need to override this since TypedDicts are for static typing
    datum = time.perf_counter_ns()
    o = {
      'name': name,
      'age': age,
    }
    elapsed = time.perf_counter_ns() - datum
    return o, elapsed
  
  @staticmethod
  def benchmark(o: PersonTypedDict) -> int: return mapping_benchmark(o)

@BenchmarkRegistry.register
class PersonSubclassDict(dict):

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonSubclassDict, int]:
    # L
    datum = time.perf_counter_ns()
    o = PersonSubclassDict({
      'name': name,
      'age': age,
    })
    elapsed = time.perf_counter_ns() - datum
    return o, elapsed
  
  @staticmethod
  def benchmark(o: PersonSubclassDict) -> int: return mapping_benchmark(o)

@BenchmarkRegistry.register
@define
class PersonAttrs:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonAttrs, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonAttrs) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@define(slots=True)
class PersonAttrsSlots:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonAttrsSlots, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonAttrsSlots) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@define(frozen=True)
class PersonAttrsFrozen:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonAttrsFrozen, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonAttrsFrozen) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
@define(frozen=True, slots=True)
class PersonAttrsFrozenSlots:
  name: str
  age: int

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonAttrsFrozenSlots, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonAttrsFrozenSlots) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonWithProperties:
  def __init__(self, name: str, age: int):
    self._name = name
    self._age = age
      
  @property
  def name(self) -> str:
    return self._name
      
  @property 
  def age(self) -> int:
    return self._age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonWithProperties, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonWithProperties) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonWithCachedProperties:
  def __init__(self, name: str, age: int):
    self._name = name
    self._age = age
      
  @cached_property
  def name(self) -> str:
    return self._name
      
  @cached_property
  def age(self) -> int:
    return self._age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonWithCachedProperties, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonWithCachedProperties) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonSimpleNamespace:
  @classmethod
  def factory(cls, name: str, age: int) -> tuple[SimpleNamespace, int]:
    return factory_kwarg_benchmark(cls, name, age)
    
  @staticmethod
  def benchmark(o: SimpleNamespace) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonOrderedDict:
  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonOrderedDict, int]:
    datum = time.perf_counter_ns()
    o = OrderedDict([('name', name), ('age', age)])
    elapsed = time.perf_counter_ns() - datum
    return o, elapsed
  
  @staticmethod
  def benchmark(o: PersonOrderedDict) -> int: return mapping_benchmark(o)

# @BenchmarkRegistry.register
# class PersonWeakRef:
#   """Uses weak references for attributes - useful for cache-like structures"""
#   def __init__(self, name: str, age: int):
#     self._name = weakref.ref(name)
#     self._age = weakref.ref(age)
  
#   @property
#   def name(self) -> str:
#     return self._name()
  
#   @property
#   def age(self) -> int:
#     return self._age()

#   @classmethod
#   def factory(cls, name: str, age: int) -> tuple[PersonWeakRef, int]:
    # return factory_kwarg_benchmark(cls, name, age)
  
#   @staticmethod
#   def benchmark(o: PersonWeakRef) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonCTypes:
  """Using ctypes for direct memory access and C-like structures"""
  class _CTPerson(ctypes.Structure):
    _fields_ = [
      ("name", ctypes.c_char * 64), # Fixed-size string field
      ("age", ctypes.c_int)
    ]

  def __init__(self, name: str, age: int):
    self._data = self._CTPerson()
    self._data.name = name.encode('utf-8')
    self._data.age = age

  @property
  def name(self) -> str:
    return self._data.name.decode('utf-8').rstrip('\0')

  @property
  def age(self) -> int:
    return self._data.age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonCTypes, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonCTypes) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonArray:
  """Using array module for memory-efficient storage"""
  def __init__(self, name: str, age: int):
    self._name = array.array('u', name)
    self._age = array.array('i', [age])
  
  @property
  def name(self) -> str:
    return self._name.tounicode()
  
  @property
  def age(self) -> int:
    return self._age[0]

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonArray, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonArray) -> int: return attrib_benchmark(o)

# @BenchmarkRegistry.register
# class PersonMemoryMapped:
#   """Using memory mapping for large datasets or shared memory"""
#   _FORMAT = 'utf-8'
#   _BUFFER_SIZE = 1024
  
#   def __init__(self, name: str, age: int):
#     self._buffer = mmap.mmap(-1, self._BUFFER_SIZE)
#     name_bytes = name.encode(self._FORMAT)
#     self._buffer.write(len(name_bytes).to_bytes(4, 'big'))
#     self._buffer.write(name_bytes)
#     self._buffer.write(age.to_bytes(4, 'big'))
#     self._buffer.seek(0)
  
#   @property
#   def name(self) -> str:
#     self._buffer.seek(0)
#     name_len = int.from_bytes(self._buffer.read(4), 'big')
#     return self._buffer.read(name_len).decode(self._FORMAT)
  
#   @property
#   def age(self) -> int:
#     self._buffer.seek(4) # Skip name length
#     name_len = int.from_bytes(self._buffer.read(4), 'big')
#     self._buffer.seek(8 + name_len) # Skip name
#     return int.from_bytes(self._buffer.read(4), 'big')

#   @classmethod
#   def factory(cls, name: str, age: int) -> tuple[PersonMemoryMapped, int]:
#     return factory_kwarg_benchmark(cls, name, age)
  
#   @staticmethod
#   def benchmark(o: PersonMemoryMapped) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonDescriptor:
  """Using descriptors for attribute access control"""
  class TypedDescriptor:
    def __init__(self, type_):
      self._name = '_' + type_.__name__
      self._type = type_
    
    def __get__(self, instance, owner):
      if instance is None:
        return self
      return getattr(instance, self._name)
    
    def __set__(self, instance, value):
      if not isinstance(value, self._type):
        value = self._type(value)
      setattr(instance, self._name, value)

  name = TypedDescriptor(str)
  age = TypedDescriptor(int)

  def __init__(self, name: str, age: int):
    self.name = name
    self.age = age

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonDescriptor, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonDescriptor) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonOperatorSlots:
  """Using operator module and __slots__ for optimized attribute access"""
  __slots__ = ('name', 'age')
  
  def __init__(self, name: str, age: int):
    object.__setattr__(self, 'name', name)
    object.__setattr__(self, 'age', age)
  
  name_getter = property(operator.attrgetter('name'))
  age_getter = property(operator.attrgetter('age'))

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonOperatorSlots, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonOperatorSlots) -> int: 
    return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonStruct:
  """
  Uses struct module to pack data into binary format.
  Format: 
  - name length (unsigned int): 4 bytes
  - name (variable length str): name_length bytes
  - age (unsigned int): 4 bytes
  """
  # Format for storing name length and age
  _HEADER_FORMAT = '!I' # unsigned int, network byte order (4 bytes)
  _AGE_FORMAT = '!I'   # unsigned int, network byte order (4 bytes)
  
  def __init__(self, name: str, age: int):
    # Convert name to bytes and get its length
    self._name_bytes = name.encode('utf-8')
    name_length = len(self._name_bytes)
    
    # Pack the length, name bytes, and age into a binary structure
    self._data = (
      struct.pack(self._HEADER_FORMAT, name_length) +
      self._name_bytes +
      struct.pack(self._AGE_FORMAT, age)
    )
  
  @property
  def name(self) -> str:
    # Unpack name length from first 4 bytes
    name_length = struct.unpack(self._HEADER_FORMAT, self._data[:4])[0]
    # Extract and decode name bytes
    return self._data[4:4+name_length].decode('utf-8')
  
  @property
  def age(self) -> int:
    # Unpack age from last 4 bytes
    name_length = struct.unpack(self._HEADER_FORMAT, self._data[:4])[0]
    return struct.unpack(self._AGE_FORMAT, self._data[4+name_length:])[0]

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonStruct, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonStruct) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonStructFixed:
  """
  Uses struct module with fixed-length fields.
  Format: '<32sI' means:
  - name (str): 32 bytes, null padded
  - age (unsigned int): 4 bytes
  Little-endian byte order for better performance on most systems.
  """
  _FORMAT = '<32sI' # fixed-length string (32 bytes) + unsigned int (4 bytes)
  _struct = struct.Struct(_FORMAT)
  
  def __init__(self, name: str, age: int):
    # Ensure name fits in fixed length field
    name_bytes = name.encode('utf-8')
    if len(name_bytes) > 32:
      raise ValueError("Name too long - must be ≤ 32 bytes when UTF-8 encoded")
    
    # Pad name to fixed length
    name_bytes = name_bytes.ljust(32, b'\0')
    
    # Pack data into binary structure
    self._data = self._struct.pack(name_bytes, age)
  
  @property
  def name(self) -> str:
    # Unpack and convert back to string, stripping null padding
    name_bytes = self._struct.unpack(self._data)[0]
    return name_bytes.decode('utf-8').rstrip('\0')
  
  @property
  def age(self) -> int:
    # Unpack age
    return self._struct.unpack(self._data)[1]

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonStructFixed, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonStructFixed) -> int: return attrib_benchmark(o)

@BenchmarkRegistry.register
class PersonStructArray:
  """
  Uses struct module to manage an array of fixed-length records.
  Useful for handling multiple records efficiently.
  """
  _RECORD_FORMAT = '<32sI' # same as PersonStructFixed
  _struct = struct.Struct(_RECORD_FORMAT)
  _RECORD_SIZE = _struct.size
  
  def __init__(self, name: str, age: int):
    # Allocate space for multiple records (we'll just use one for the benchmark)
    self._buffer = bytearray(self._RECORD_SIZE)
    self.set_record(0, name, age)
  
  def set_record(self, index: int, name: str, age: int) -> None:
    name_bytes = name.encode('utf-8')
    if len(name_bytes) > 32:
      raise ValueError("Name too long - must be ≤ 32 bytes when UTF-8 encoded")
    
    name_bytes = name_bytes.ljust(32, b'\0')
    offset = index * self._RECORD_SIZE
    self._struct.pack_into(self._buffer, offset, name_bytes, age)
  
  def get_record(self, index: int) -> tuple[str, int]:
    offset = index * self._RECORD_SIZE
    name_bytes, age = self._struct.unpack_from(self._buffer, offset)
    return name_bytes.decode('utf-8').rstrip('\0'), age
  
  @property
  def name(self) -> str:
    return self.get_record(0)[0]
  
  @property
  def age(self) -> int:
    return self.get_record(0)[1]

  @classmethod
  def factory(cls, name: str, age: int) -> tuple[PersonStructArray, int]:
    return factory_kwarg_benchmark(cls, name, age)
  
  @staticmethod
  def benchmark(o: PersonStructArray) -> int: return attrib_benchmark(o)
