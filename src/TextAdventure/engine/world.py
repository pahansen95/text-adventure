"""

The Game Engine

"""
from __future__ import annotations
from typing import Any
from collections.abc import Hashable, Iterable, MappingView, MutableMapping
import asyncio, logging
from .. import entity
from ..core import id_t
logger = logging.getLogger(__name__)

entity_t = entity.Entity
world_t = dict[id_t, entity_t]

async def world_factory(
  frozen_world: Iterable[entity_t],
) -> world_t:
  """Build the set of entities which define the world"""

  world: world_t = {}

  for frozen_entity in frozen_world:
    logger.debug(f'Initializing {frozen_entity['kind']} {frozen_entity['metadata']['name']}')
    entity: entity_t = await entity_factory(
      **frozen_entity
    )
    entity_id = entity['metadata']['id']
    # assert entity[]['id'] not in world
    assert entity_id not in world
    ... # Assert that the entity's declared capabilities exist
    world[entity_id] = entity
  
  return world

async def entity_factory(**kwargs) -> entity_t: return kwargs # TODO: If necessary, this is probably some sort of dependency injection
