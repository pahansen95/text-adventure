from __future__ import annotations
from typing import Literal, TypedDict
from dataclasses import dataclass
from . import Entity, EntitySpec, EntityStatus, Capability, CapabilityResult

### Entities

class CartesianSpace(Entity):
  """A (Mathematical) Space implemented as absolute units."""
  kind: Literal['Engine/Entity/CartesianSpace']
  KIND = 'Engine/Entity/CartesianSpace'
  spec: CartesianSpec
  status: CartesianStatus

class CartesianSpec(EntitySpec):
  precision: int # ie. 1000
  """The number of sub-units in 1 base unit. ie. 1000 would imply 1 milli-unit"""
  bounds: BoundingBox
  """The Boundary of the World"""

class CartesianStatus(EntityStatus): ...

class Player(Entity):
  kind: Literal['Engine/Entity/Player']
  KIND = 'Engine/Entity/Player'
  spec: PlayerSpec
  status: PlayerStatus

class PlayerSpec(EntitySpec):
  pos: Point3D

class PlayerStatus(EntityStatus): ...

@dataclass
class PlayerCapabilities(Capability):
  player: Player

  async def move_in_space(self, transform: Vector3D, space: CartesianSpace) -> CapabilityResult[Point3D]:
    """Moves the Player in Cartesian Space"""
    return {
      'kind': Player.KIND,
      'capability': PlayerCapabilities.move_in_space.__name__,
      'result': {
        'x': self.player['spec']['pos']['x'] + transform['x'],
        'y': self.player['spec']['pos']['y'] + transform['y'],
        'z': self.player['spec']['pos']['z'] + transform['z'],
      }
    }

### Supporting Datastructures

class Point3D(TypedDict):
  """A Three Dimensional Point in a Cartesian Space"""
  x: int
  y: int
  z: int

class Vector3D(Point3D):
  """A Three Dimensional Vector representing direction & scale"""
  ...

class BoundingBox(TypedDict):
  """A 3D Bounding box represented as 2 opposing points a Cartesian Space"""
  max: Point3D
  min: Point3D