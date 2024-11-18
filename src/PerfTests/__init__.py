from __future__ import annotations
from typing import Protocol, TypeVar, Generic, TextIO
from collections.abc import Mapping, Callable, Generator
import time, statistics, logging, enum, gc
import concurrent.futures as fut
from dataclasses import dataclass
from tqdm import tqdm

logger = logging.getLogger(__name__)

### Boilerplate

T = TypeVar('T')
class TestableDatastructure(Generic[T], Protocol):
  @classmethod
  def factory(cls, name: str, age: int) -> tuple[object, int]: ...
  @staticmethod
  def benchmark(o: object) -> int: ...

class BenchmarkRegistry:
  registry: list[TestableDatastructure] = []

  @classmethod
  def register(cls, o: type[T]) -> type[T]:
    if o not in cls.registry: cls.registry.append(o)
    return o

# Benchmarks

def attrib_benchmark(o: object) -> int:
  datum = time.perf_counter_ns()
  _ = o.name
  _ = o.age
  elapsed = time.perf_counter_ns() - datum
  return elapsed

def mapping_benchmark(o: Mapping) -> int:
  datum = time.perf_counter_ns()
  _ = o['name']
  _ = o['age']
  elapsed = time.perf_counter_ns() - datum
  return elapsed

def factory_kwarg_benchmark(cls: type[T], name: str, age: int) -> tuple[T, int]:
  datum = time.perf_counter_ns()
  o = cls(name=name, age=age)
  elapsed = time.perf_counter_ns() - datum
  return o, elapsed

def factory_arg_benchmark(cls: type[T], name: str, age: int) -> tuple[T, int]:
  datum = time.perf_counter_ns()
  o = cls(name, age)
  elapsed = time.perf_counter_ns() - datum
  return o, elapsed

def run_benchmarks(factory: Callable, access: Callable, count: int) -> list[tuple[int, int]]:
  times: list[tuple[int, int]] = []
  for i in tqdm(range(count)):
    o, t1 = factory("Name", i)
    t2 = access(o)
    times.append((t1, t2))
  return times

# Metrics Calculations

class MetricType(enum.Enum):
  CREATION = enum.auto()
  ACCESS = enum.auto()
  # TOTAL = enum.auto()

@dataclass
class Metrics:
  mean: float
  median: float
  stdev: float
  min: int
  max: int
  total: int
  ops_per_second: float

@dataclass
class DataStructureMetrics:
  creation: Metrics
  access: Metrics
  total: Metrics

def calculate_single_metrics(times: list[int]) -> Metrics:
  return Metrics(
    mean=statistics.mean(times),
    median=statistics.median(times),
    stdev=statistics.stdev(times),
    min=min(times),
    max=max(times),
    total=sum(times),
    ops_per_second=1_000_000_000 / statistics.mean(times)
  )

def calculate_metrics(results: list[tuple[int, int]]) -> DataStructureMetrics:
  creation_times = [t1 for t1, _ in results]
  access_times = [t2 for _, t2 in results]
  total_times = [t1 + t2 for t1, t2 in results]
  
  return DataStructureMetrics(
    creation=calculate_single_metrics(creation_times),
    access=calculate_single_metrics(access_times),
    total=calculate_single_metrics(total_times)
  )

# Pretty Printing, Utils & etc... 

def format_ns(ns: float) -> str:
  if ns < 1000: return f"{ns:.2f} ns"
  elif ns < 1_000_000: return f"{ns/1000:.2f} µs"
  elif ns < 1_000_000_000: return f"{ns/1_000_000:.2f} ms"
  else: return f"{ns/1_000_000_000:.2f} s"

def print_metrics_table(
  metrics_dict: Mapping[type, DataStructureMetrics],
  metric_type: MetricType,
  file: TextIO,
) -> None:
  metric_name = metric_type.name.lower()
  print(f"### {metric_type.name} Time Performance ###\n", file=file)
  headers = ["Type", "Mean", "Median", "StdDev", "Min", "Max", "Ops/sec"]
  
  # Calculate column widths
  widths = [max(len(str(cls.__name__)) for cls in metrics_dict),
            12, 12, 12, 12, 12, 15]
  
  # Print headers
  header = "  ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
  print(header, file=file)
  print("-" * len(header), file=file)
  
  # Get metrics for specified type
  for cls, metrics in metrics_dict.items():
    metric_data = getattr(metrics, metric_name)
    row = [
      cls.__name__,
      format_ns(metric_data.mean),
      format_ns(metric_data.median),
      format_ns(metric_data.stdev),
      format_ns(metric_data.min),
      format_ns(metric_data.max),
      f"{metric_data.ops_per_second:,.0f}"
    ]
    print("  ".join(f"{cell:<{w}}" for cell, w in zip(row, widths)), file=file)
  print('', file=file)

def print_relative_performance(
  metrics_dict: dict[type, DataStructureMetrics],
  metric_type: MetricType,
  file: TextIO
) -> None:
  metric_name = metric_type.name.lower()
  print(f"### {metric_type.name} Relative Performance (lower is better) ###\n", file=file)
  
  # Get means for the specified metric type
  means = [(cls.__name__, getattr(getattr(metrics, metric_name), 'mean'))
            for cls, metrics in metrics_dict.items()]
  fastest_mean = min(mean for _, mean in means)
  max_name_len = max(len(n[0]) for n in means)
  
  for name, mean in sorted(means, key=lambda x: x[1]):
    relative = mean / fastest_mean
    print(f"{name:>{max_name_len}}: {format_ns(mean):>15} ({relative:>6.2f}x)", file=file)
  print('\n', file=file)

def run_benchmarks_and_calculate_metrics(
  count: int,
  benchmark_registry: type[BenchmarkRegistry] = BenchmarkRegistry,
  pool: fut.Executor | None = None,
  disable_gc: bool = True,
) -> Mapping[type, DataStructureMetrics]:
  assert pool
  renable_gc = (disable_gc and gc.isenabled())
  if disable_gc: gc.disable()
  benchmark_results: dict[type, fut.Future[DataStructureMetrics]] = {}
  # Schedule everything
  for cls in benchmark_registry.registry:
    logger.debug(f'Running Benchmarks for `{cls.__qualname__}`')
    benchmark_results[cls] = pool.submit(
      calculate_metrics,
      run_benchmarks(
        cls.factory, cls.benchmark,
        count
      )
    )
  # Resolve all futures
  done, not_done = fut.wait(benchmark_results.values())
  assert len(not_done) == 0
  assert all(d.exception() is None for d in done)
  
  if renable_gc: gc.enable()
  return { cls: f.result() for cls, f in benchmark_results.items() }

# Avoid Cyclic Imports

from . import datastructures
