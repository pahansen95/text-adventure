from __future__ import annotations
from typing import TypeVar, ClassVar, Any
from collections.abc import Callable
from dataclasses import dataclass, field, KW_ONLY

T = TypeVar('T')
"""Any Type"""
R = TypeVar('R')
"""A Results Type"""
M = TypeVar('M')
"""A Metrics Type"""

@dataclass
class BenchmarkRegistry:
  name: str
  run_benchmarks: Callable[[type, int], R]
  calc_metrics: Callable[[R], M]
  render_metrics: Callable[[M], str]
  rank_metrics: Callable[[M], list]
  _: KW_ONLY
  class_registry: list[type[T]] = field(default_factory=list)
  _registry: ClassVar[dict[str, BenchmarkRegistry]] = dict()
  
  def __post_init__(self):
    assert self.name not in BenchmarkRegistry._registry
    BenchmarkRegistry._registry[self.name] = self

  def __str__(self) -> str:
    return f'{self.name.capitalize()}Registry{[ cls.__qualname__ for cls in self.class_registry ]}'

  def __call__(self, cls: type[T]) -> type[T]:
    if cls not in self.class_registry: self.class_registry.append(cls)
    return cls
  
  @classmethod
  def run_all_benchmarks(cls, iterations: int) -> dict[str, dict[type, Any]]:
    """Runs all the registered Benchmarks"""
    assert len(cls._registry) > 0
    results = {}
    for reg_name, reg in cls._registry.items():
      assert isinstance(reg, BenchmarkRegistry)
      results[reg_name] = {}
      for cls in reg.class_registry:
        results[reg_name][cls] = reg.run_benchmarks(cls, iterations)
    return results
  
  @classmethod
  def calc_all_metrics(cls, measurements: dict[str, dict[type, Any]]) -> dict[str, dict[type, Any]]:
    """Calculates all the metrics"""
    metrics = {}
    for reg_name, _measurements in measurements.items():
      assert reg_name in cls._registry
      metrics[reg_name] = {}
      reg = cls._registry[reg_name]
      for cls in reg.class_registry:
        metrics[reg_name][cls] = reg.calc_metrics(_measurements[cls])
    return metrics
  
  @classmethod
  def render_all_metrics(cls, metrics: dict[str, dict[type, Any]]) -> dict[str, dict[type, str]]:
    """Renders all the metrics"""
    tables = {}
    for reg_name, _metrics in metrics.items():
      assert reg_name in cls._registry
      tables[reg_name] = {}
      reg = cls._registry[reg_name]
      for cls in reg.class_registry:
        tables[reg_name][cls] = reg.render_metrics(_metrics[cls])
    return tables
  
  @classmethod
  def rank_all_metrics(cls, metrics: dict[str, dict[type, Any]]) -> dict[str, dict[type, list]]:
    """Ranks all metrics"""
    ranks = {}
    for reg_name, _metrics in metrics.items():
      assert reg_name in cls._registry
      ranks[reg_name] = {}
      reg = cls._registry[reg_name]
      for cls in reg.class_registry:
        ranks[reg_name][cls] = reg.rank_metrics(_metrics[cls])
    return ranks
  
from . import datastructures
