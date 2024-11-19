"""

Implements Benchmarks for measuring performance of Datastructures

"""
from __future__ import annotations
from typing import Protocol, TypeVar, Generic, TypedDict
from tqdm import tqdm
from tabulate import tabulate
import statistics, time

__all__ = [
  "CreationMetrics",
  "DatastructFactory",
  "Creation",
]

from . import T, BenchmarkRegistry

class Benchmarkable(Generic[T], Protocol):
  @classmethod
  def factory(cls: type[T]) -> tuple[T, int]: ...
  @staticmethod
  def get(o: T) -> list[int]: ...
  @staticmethod
  def set(o: T) -> list[int]: ...

class FactoryMixin:
  NAME = 'Name'
  AGE = 0
  @classmethod
  def factory(cls: type[T]) -> tuple[T, Metrics]:
    name, age = FactoryMixin.NAME, FactoryMixin.AGE
    start = time.perf_counter_ns()
    o = cls(name=name, age=age)
    end = time.perf_counter_ns()
    return o, (end - start)

class GetMixin:
  @staticmethod
  def get(o: T) -> list[int]:
    res = []

    for k in (
      'name', 'age'
    ):
      start = time.perf_counter_ns()
      _ = getattr(o, k)
      end = time.perf_counter_ns()
      res.append(end-start)

    return res

class SetMixin:
  NAME = 'Foobar'
  AGE = 100
  @staticmethod
  def set(o: T) -> list[int]:
    res = []

    for k, v in (
      ('name', SetMixin.NAME),
      ('age', SetMixin.AGE)
    ):
      start = time.perf_counter_ns()
      setattr(o, k, v)
      end = time.perf_counter_ns()
      res.append(end-start)

    return res

class Measurements(TypedDict):
  """Measurements for every iteration"""

  init: list[int]
  """Time in nanoseconds to create the Datastructure"""
  get: list[int]
  """Mean access time for all attributes"""
  set: list[int]
  """Mean assignment time for all attributes"""

def run_benchmarks(datastruct: Benchmarkable[type[T]], iterations: int) -> Measurements:
  measure: Measurements = {
    'init': [],
    'get': [],
    'set': [],
  }
  for _ in tqdm(range(iterations), desc=datastruct.__qualname__):
    o, r = datastruct.factory()
    measure['init'].append(r)
    g = datastruct.get(o)
    measure['get'].append(round(sum(g) / len(g)))
    s = datastruct.set(o)
    measure['set'].append(round(sum(s) / len(s)))
  return measure

class Metrics(TypedDict):
  mean: float
  median: float
  stdev: float
  min: float
  max: float
  total: float
  ops_per_second: float

def _calc_metrics(
  measure: list[float],
) -> Metrics:
  assert isinstance(measure, list), type(measure)
  return {
    'mean': statistics.mean(measure),
    'median': statistics.median(measure),
    'stdev': statistics.stdev(measure),
    'min': min(measure),
    'max': max(measure),
    'total': sum(measure),
    'ops_per_second': 1_000_000_000 / statistics.mean(measure)
  }

def calc_metrics(
  results: Measurements,
) -> dict[str, Metrics]:
  assert isinstance(results, dict) and all(isinstance(v, list) for v in results.values())
  return { k: _calc_metrics(v) for k, v in results.items() }

def render_metrics(
  metrics: dict[str, Metrics]
) -> str:
  tables = ''
  for k, _metrics in metrics.items():
    table = tabulate(
      [[metric, f"{value:,.2f}"] for metric, value in _metrics.items()],
      headers=['Metric', 'Value'],
      tablefmt='grid'
    )
    lines = table.split('\n')
    width = len(lines[0]) - 2
    assert width > 0, width
    title = k.capitalize()
    tables += '\n'.join([
      lines[0],
      ( lines[1][0] + f"{title:^{width}}" + lines[1][-1] ),
      table
    ]) + '\n'
  return tables.rstrip()

REGISTRY = BenchmarkRegistry(
  'datastructures',
  run_benchmarks,
  calc_metrics, render_metrics,
  lambda *args: None
)