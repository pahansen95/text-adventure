from __future__ import annotations
from typing import Protocol
from collections.abc import Iterator
from dataclasses import dataclass, field

from .. import *

class Production(Protocol):

  @property
  def cfg(self) -> Cfg: ...
  @cfg.setter
  def cfg(self, cfg: Cfg): ...
  async def render_manuscript(self): ...

@dataclass
class ProductionRegistry:

  productions: dict[str, Production] = field(default_factory=dict)

  def __getitem__(self, k: str) -> Production: return self.productions[k]
  def __iter__(self) -> Iterator[str]: return iter(self.productions)
  def __contains__(self, k: str) -> bool: return k in self.productions

  def add(self, name: str, prod: Production):
    assert name not in self.productions
    self.productions[name] = prod

PRODUCTION_REGISTRY = ProductionRegistry()

__all__ = [
  'Production', 'ProductionRegistry',
  'PRODUCTION_REGISTRY'
]

from . import Example