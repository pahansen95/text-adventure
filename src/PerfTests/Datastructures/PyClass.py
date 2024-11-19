from __future__ import annotations

import PerfTests.Benchmarks.datastructures as ds

@ds.REGISTRY
class PersonClass(ds.FactoryMixin, ds.GetMixin, ds.SetMixin):
  def __init__(self, name: str, age: int):
    self.name = name
    self.age = age  

@ds.REGISTRY
class PersonSlotsClass(ds.FactoryMixin, ds.GetMixin, ds.SetMixin):
  __slots__ = ("name", "age")
  def __init__(self, name: str, age: int):
    self.name = name
    self.age = age
