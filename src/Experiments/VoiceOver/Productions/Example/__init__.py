"""

An Example Production

"""
from __future__ import annotations
from typing import NoReturn, Literal, BinaryIO
from collections.abc import AsyncGenerator, Iterable, Mapping, Coroutine, Callable, ByteString
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
class ExampleProduction:

  data: pathlib.Path = field(default=DATADIR)

  async def render_manuscript(self, cfg: Cfg):

    self.data.mkdir(exist_ok=True)

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
        (cfg['WorkCache'] / 'rt-cache').mkdir(exist_ok=True)
        cache: pathlib.Path = field(default=cfg['WorkCache'] / 'rt-cache')
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
      
      ### Build the Scene

      actors = {
        n: Actor(n) for n in (
          'Lily', 'Roger', 'Callum'
        )
      }
      roles = {
        n: Role(n) for n in (
          'Narrator', 'Protagonist', 'Antagonist'
        )
      }
      castings = Castings(
        roles=set(roles.values()),
        actors=set(actors.values()),
        castings={
          roles[r]: actors[a]
          for r, a in {
            'Narrator': 'Lily',
            'Protagonist': 'Roger',
            'Antagonist': 'Callum',
          }.items()
        }
      )

      def compositor_factory(roles: set[Role]) -> Compositor:
        compositor = Compositor()
        for role in roles:
          assert isinstance(role.name, str), role.name
          compositor.add_layer(role.name)
        return compositor

      intro_factory: Callable[[str], str] = lambda k: f'Hello! My name is {castings.actor_by_role(k).name} and I play the role of {castings[k].name}.'

      manuscript = Manuscript().add_act().add_scene(
        'Example', 1, Scene(
          name='Example',
          castings=castings,
          chronology=[
            set( SceneEvent(when=when, **e) for e in events ) for when, events in enumerate((
              (
                { 'role': castings['Narrator'], 'voice_line': 'Scene Start.' },
              ),
              (
                { 'role': castings['Narrator'], 'voice_line': intro_factory('Narrator') },
              ),
              (
                { 'role': castings['Protagonist'], 'voice_line': intro_factory('Protagonist') },
                { 'role': castings['Antagonist'], 'voice_line': intro_factory('Antagonist') },
              ),
              (
                { 'role': castings['Narrator'], 'voice_line': 'Scene End.' },
              )
            ))
          ],
          compositor=compositor_factory(castings.roles),
          tools=TOOLS,
      ))

      ### Render the Manuscript
      
      manuscript_workdir = self.data / 'manuscript'
      manuscript_workdir.mkdir(exist_ok=True)
      logger.info(f'Rendering Manuscript under {manuscript_workdir.as_posix()}')
      await manuscript.render(manuscript_workdir)

PRODUCTION_REGISTRY.add(__name__.rsplit('.', maxsplit=1)[-1], ExampleProduction())
