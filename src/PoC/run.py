from __future__ import annotations

from . import (
  ## Utils
  logger,
  ## Defined Resources
    CartesianSpace, Player, PlayerCapabilities,
  ## Game Engine
    # Core
    id_t,
    # World
    world_factory, world_t,
    # Capabilities
    get_capabilities, apply_capability, is_fixture, is_agent,
)

COORD_SYSTEM: CartesianSpace = {
  'kind': CartesianSpace.KIND,
  'metadata': {
    'id': '25f67dffa66e8908685092977732c681',
    'name': 'WorldCoordinates',
  },
  'spec': {
    'precision': 10, # 1 CM
    'bounds': { # 1,000 Base units (ie. 1 KM)
      'max': { 'x': 500 * 10, 'y': 500 * 10, 'z': 500 * 10 },
      'max': { 'x': -500 * 10, 'y': -500 * 10, 'z': -500 * 10 }
    }
  }
}
PLAYER: Player = {
  'kind': Player.KIND,
  'metadata': {
    'id': '837492d6dfdbcf9c11cdba5374013802',
    'name': 'PlayerOne',
  },
  'spec': {
    'pos': { 'x': 0, 'y': 0, 'z': 0, }
  },
  'status': {}, # Runtime Status; nothing to initialize pre-runtime
  }

async def run_game_engine():

  ### Bootstrap World
  world = await world_factory(
    [
      COORD_SYSTEM,
      PLAYER,
    ]
  )
  logger.debug(f'Loaded {len(world)} Entities into the World')

  await test_world(
    world,
    PLAYER['metadata']['id'],
    COORD_SYSTEM['metadata']['id'],
  )

  ### Teardown World
  # TODO...

async def test_world(
  world: world_t,
  player_one_id: id_t,
  world_coords_id: id_t,
):
  """Tests some things"""
  player_one: Player = world[player_one_id]
  world_coords: CartesianSpace = world[world_coords_id]

  ### Move the Player in the world

  """NOTE
  Movement is a capability of the Player.
  
  The Player "transforms" it's location.
  
  """
  # assert is_fixture(world_coords['kind'])
  # assert is_agent(player_one['kind'])
  # player_one_caps = get_capabilities(
  #   player_one['metadata']['id'],
  # )
  player_one_caps = PlayerCapabilities(player_one) # TODO: These capabilities need to be registered in the factory 
  assert isinstance(player_one_caps, PlayerCapabilities)
  assert player_one_caps.player is player_one
  
  ok = await apply_capability(
    player_one['metadata']['id'],
    player_one_caps.move_in_space(
      { 'x': 1, 'y': 1, 'z': 1 },
      world_coords,
    )
  )
  assert ok
  assert player_one['spec']['pos'] == { 'x': 1, 'y': 1, 'z': 1 }, player_one['spec']['pos'] # 0 + 1 is 1
  