"""

Capabilities.

Manages the contractural interface between all registered entities.

"""
from __future__ import annotations
from collections.abc import Coroutine
from typing import TypeVar, Generic, TypedDict, Protocol
import logging

from ..core import id_t

logger = logging.getLogger(__name__)

class Capability(Protocol): ...

T = TypeVar('T')
class CapabilityResult(Generic[T], TypedDict):
  kind: str
  capability: str
  result: T

def get_capabilities(
  id: id_t
) -> Capability:
  raise NotImplementedError

async def apply_capability(
  originator: id_t,
  cap: Coroutine[None, None, CapabilityResult]
) -> bool:
  """Attempts to apply a Capability"""
  try: _ = await cap
  except: return False
  return True

def is_fixture(
  id: id_t,
) -> bool:
  """An Entity w/ no Agency; can only react"""
  raise NotImplementedError

def is_agent(
  id: id_t,
) -> bool:
  """An Entity w/ Agency; can independently act w/ no external pre-action"""
  raise NotImplementedError
