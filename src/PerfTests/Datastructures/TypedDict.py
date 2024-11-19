from __future__ import annotations
from typing import TypedDict
import time

import PerfTests.Benchmarks.datastructures as ds

@ds.REGISTRY
class PersonTypedDict(TypedDict):
  name: str
  age: int

  @classmethod
  def factory(cls) -> tuple[PersonTypedDict, ds.Metrics]:
    name, age = ds.FactoryMixin.NAME, ds.FactoryMixin.AGE
    start = time.perf_counter_ns()
    o = {
      'name': name,
      'age': age
    }
    end = time.perf_counter_ns()
    return o, (end - start)

  @staticmethod
  def get(o: PersonTypedDict) -> list[int]:
    res = []

    for k in (
      'name', 'age'
    ):
      start = time.perf_counter_ns()
      _ = o[k]
      end = time.perf_counter_ns()
      res.append(end-start)

    return res
  
  @staticmethod
  def set(o: PersonTypedDict) -> list[int]:
    res = []

    for k, v in (
      ('name', ds.SetMixin.NAME),
      ('age', ds.SetMixin.AGE)
    ):
      start = time.perf_counter_ns()
      o[k] = v
      end = time.perf_counter_ns()
      res.append(end-start)

    return res
