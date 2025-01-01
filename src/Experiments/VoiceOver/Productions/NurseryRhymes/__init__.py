"""

An Example Production

"""
from __future__ import annotations
from typing import NoReturn, Literal, BinaryIO, Protocol
from collections.abc import AsyncGenerator, Iterable, Mapping, Coroutine, Callable, ByteString, Generator
import logging, sys, os, asyncio, threading, signal, types, json, hashlib, pathlib
from dataclasses import dataclass, field
from collections import deque

### Package Imports
from ... import * # VoiceOver
from .. import *
###

CONTEXT = pathlib.Path(__file__).parent
DATADIR = CONTEXT / '.data'

logger = logging.getLogger(__name__)

@dataclass
class Rhyme:
  TITLE: str
  LYRICS: str

  @property
  def NAME(self) -> str: return type(self).__name__.rsplit('.', maxsplit=1)[-1]

  def scene(self, castings: Castings, tools: Tools) -> Scene: raise NotImplementedError

def compositor_factory(roles: set[Role]) -> Compositor:
  compositor = Compositor()
  for role in roles:
    assert isinstance(role.name, str), role.name
    compositor.add_layer(role.name)
  return compositor

@dataclass
class BlackSheep(Rhyme):
  TITLE: str = 'Baa, Baa Black Sheep'
  LYRICS: str = """
Baa, baa, black sheep,
Have you any wool?
Yes, sir, yes, sir,
Three bags full;
One for the master,
And one for the dame,
And one for the little boy
Who lives down the lane.
  """
  
  def scene(self, castings: Castings, tools: Tools) -> Scene:
    return Scene(
      self.NAME,
      castings,
      [],
      compositor_factory(castings.roles),
      tools=tools,
    ).add(
      SceneEvent(
        castings['FemaleNarrator'],
        when=1,
        voice_line=self.LYRICS,
      )
    )

@dataclass
class GirlsAndBoys(Rhyme):
  TITLE: str = 'Girls and Boys Come Out to Play'
  LYRICS: str = """
Girls and boys, come out to play,
The moon doth shine as bright as day;
Leave your supper, and leave your sleep,
And come with your playfellows into the street.

Come with a whoop, come with a call,
Come with a good will or not at all.
Up the ladder and down the wall,
A halfpenny roll will serve us all.

You find milk, and I'll find flour,
And we'll have a pudding in half an hour.
  """

  def scene(self, castings: Castings, tools: Tools) -> Scene:
    roles = list(castings.roles)
    return Scene(
      self.NAME,
      castings,
      [
        { SceneEvent(
          role=roles[idx % len(roles)],
          when=idx,
          voice_line=voice_line
        ) } for idx, voice_line in enumerate(self.LYRICS.split('\n\n'))
      ],
      compositor_factory(castings.roles),
      tools=tools,
    )

@dataclass
class HickoryDickoryDock(Rhyme):
  TITLE: str = 'Hickory Dickory Dock'
  LYRICS: str = """
Hickory dickory dock.
The mouse ran up the clock.
The clock struck one,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck two,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck three,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck four,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck five,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck six,
The mouse ran down,
Hickory dickory dock.


Hickory dickory dock.
The mouse ran up the clock.
The clock struck seven,
The mouse ran down,
Hickory dickory dock.


Hickory dickory dock.
The mouse ran up the clock.
The clock struck eight,
The mouse ran down,
Hickory dickory dock.


Hickory dickory dock.
The mouse ran up the clock.
The clock struck nine,
The mouse ran down,
Hickory dickory dock.


Hickory dickory dock.
The mouse ran up the clock.
The clock struck ten,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck eleven,
The mouse ran down,
Hickory dickory dock.

Hickory dickory dock.
The mouse ran up the clock.
The clock struck twelve,
The mouse ran down,
Hickory dickory dock.
  """

  def scene(self, castings: Castings, tools: Tools) -> Scene:
    roles = list(castings.roles)
    return Scene(
      self.NAME,
      castings,
      [
        { SceneEvent(
          role=roles[idx % len(roles)],
          when=idx,
          voice_line=voice_line
        ) } for idx, voice_line in enumerate(self.LYRICS.split('\n\n'))
      ],
      compositor_factory(castings.roles),
      tools=tools,
    )


ACTORS = {
  n: Actor(n) for n in (
    'Lily', 'Roger'
  )
}
ROLES = {
  n: Role(n) for n in (
    'FemaleNarrator', 'MaleNarrator'
  )
}
CASTINGS = Castings(
  roles=set(ROLES.values()),
  actors=set(ACTORS.values()),
  castings={
    ROLES[r]: ACTORS[a]
    for r, a in {
      'FemaleNarrator': 'Lily',
      'MaleNarrator': 'Roger',
    }.items()
  }
)
MANUSCRIPT = Manuscript().add_act()

@dataclass
class NurseryRhymes:

  data: pathlib.Path = field(default=DATADIR)
  castings: Castings = field(default_factory=lambda: CASTINGS)
  manuscript: Manuscript = field(default_factory=lambda: MANUSCRIPT)

  async def render_manuscript(self, cfg: Cfg):

    self.data.mkdir(exist_ok=True)
    cache_dir = self.data / 'cache'
    cache_dir.mkdir(exist_ok=True)

    ### Setup consumables
    voices_cache_file = cfg['WorkCache'] / 'voices.json'
    logger.debug('Establishing an API Session w/ ElevenLabs')
    async with elvn.api_session(
      api_key=cfg['ElevenLabsAPIKey'],
    ) as api_session:
      if voices_cache_file.exists():
        logger.debug('Loading the ElevenLabs Voices Cache')
        voices = json.loads(voices_cache_file.read_bytes())
      else:
        logger.debug('Caching the ElevenLabs Voices')
        voices = await elvn.voices(api_session)
        voices_cache_file.write_bytes(json.dumps(voices).encode())
  
      ### Generate the Runtime Tools Protocol
      @dataclass
      class RuntimeTools:

        ### Caching
        cache: pathlib.Path = field(default=cache_dir)
        def key(self, *k: str) -> str: return hashlib.md5('|'.join(k).encode()).hexdigest()
        def exists(self, *k: str) -> bool: return (self.cache / self.key(*k)).exists()
        def slurp(self, *k: str) -> bytes: return (self.cache / self.key(*k)).read_bytes()
        def dump(self, v: bytes, *k: str): (self.cache / self.key(*k)).write_bytes(v)
        async def load(self, *k: str, chunk_size: int = CHUNK_SIZE) -> AsyncGenerator[BinaryIO, None]:
          with (self.cache / self.key(*k)).open('rb') as f:
            while (c := f.read(chunk_size)): yield c
        async def save(self, *k: str, src: AsyncGenerator[ByteString, None]):
          with (self.cache / self.key(*k)).open('wb') as f:
            async for c in src: f.write(c)

        ### Tool Protocol
        async def dub(self, text: str, actor: str, sink: BinaryIO | None = None) -> bytes | None:
          
          ### Cache Results on a Cache Miss
          if not self.exists(text, actor): await self.save(text, actor, src=(
            elvn.tts(text, voices[actor], api_session, chunk_size=CHUNK_SIZE)
          ))
          assert self.exists(text, actor)

          ### Load the Results from Cache
          if sink is None: return self.slurp(text, actor)
          else:
            async for c in self.load(text, actor):
              sink.write(c)

      TOOLS = RuntimeTools()
      BLACK_SHEEP = BlackSheep()
      GIRLS_AND_BOYS = GirlsAndBoys()
      HICKORY_DICKORY_DOCK = HickoryDickoryDock()
      self.manuscript.add_scene(
        BLACK_SHEEP.NAME, 1, BLACK_SHEEP.scene(self.castings, TOOLS),
      ).add_scene(
        GIRLS_AND_BOYS.NAME, 1, GIRLS_AND_BOYS.scene(self.castings, TOOLS),
      ).add_scene(
        HICKORY_DICKORY_DOCK.NAME, 1, HICKORY_DICKORY_DOCK.scene(self.castings, TOOLS),
      )
      
      ### Render the Manuscript
      
      manuscript_workdir = self.data / 'manuscript'
      manuscript_workdir.mkdir(exist_ok=True)
      logger.info(f'Rendering Manuscript under {manuscript_workdir.as_posix()}')
      await self.manuscript.render(manuscript_workdir)

PRODUCTION_REGISTRY.add(__name__.rsplit('.', maxsplit=1)[-1], NurseryRhymes())
