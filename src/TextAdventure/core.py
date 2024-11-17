from __future__ import annotations
from typing import TypedDict
from collections.abc import Hashable

id_t = Hashable

class Resource(TypedDict):
  kind: str
  metadata: Metadata
  spec: Spec
  status: Status

class Metadata(TypedDict, total=False):
  id: str
  name: str

class Spec(TypedDict, total=False): ...
class Status(TypedDict, total=False): ...

