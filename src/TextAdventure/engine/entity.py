from __future__ import annotations
from typing import Literal

from .. import core

class Entity(core.Resource, total=False):
  kind: Literal['Engine/Entity/*']
  spec: EntitySpec
  status: EntityStatus
class EntitySpec(core.Spec, total=False): ...
class EntityStatus(core.Status, total=False): ...
