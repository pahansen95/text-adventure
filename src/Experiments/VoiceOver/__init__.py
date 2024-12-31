"""

A simple experiment in generating voice overs for a story

"""
from __future__ import annotations
from typing import TypedDict, Iterable, Protocol, Any, Iterator, Callable
from collections.abc import Mapping, ByteString
from dataclasses import dataclass, field, KW_ONLY

import asyncio, logging, random, pathlib, json, hashlib, io, tempfile
from mutagen.mp3 import MP3

from . import (
  ElevenLabs as elvn,
  FFMPEG as ffmpeg
)

logger = logging.getLogger(__name__)

class Cfg(TypedDict):
  ElevenLabsAPIKey: str
  WorkCache: pathlib.Path

def load_cfg_from_env(env: Mapping[str, str]) -> Cfg:
  return {
    'ElevenLabsAPIKey': elvn.load_api_key_from_env(env),
    'WorkCache': pathlib.Path(env.get('WORK_CACHE', env.get('TMPDIR', './')).rstrip('/')) / 'elevenlabs',
  }

# async def run(
#   cfg: Cfg,
#   quit_event: asyncio.Event,
#   seed: int | bytes | None = None
# ):
#   random.seed(seed)
#   voice_line = (
#     """
#     Come on down to the barbecue y'all; you won't want to miss it!
#     """
#   )
#   voice_line_fingerprint = hashlib.md5(voice_line.strip().encode()).hexdigest()[:16]
#   voices_cache = cfg['WorkCache'] / 'voices.json'
#   logger.debug('Establishing an API Session w/ ElevenLabs')
#   async with elvn.api_session(
#     api_key=cfg['ElevenLabsAPIKey'],
#   ) as api_session:
#     if voices_cache.exists():
#       logger.debug('Loading the ElevenLabs Voices Cache')
#       voices = json.loads(voices_cache.read_bytes())
#     else:
#       logger.debug('Caching the ElevenLabs Voices')
#       voices = await elvn.voices(api_session)
#       voices_cache.write_bytes(json.dumps(voices).encode())

#     voice_name = random.choice(tuple(voices))
#     logger.debug(f'Dubbing some text w/ {voice_name}')
#     voice = await elvn.tts(
#       voice_line,
#       voices[voice_name],
#       api_session
#     )
#     assert isinstance(voice, bytes)
#   voice_file = cfg['WorkCache'] / f'tts-{voice_name}-{voice_line_fingerprint}.mp3'
#   logger.info(f'DEV: Writing Voice Data to {voice_file}')
#   voice_file.write_bytes(voice)
#   # await quit_event.wait()
#   return

async def run(
  cfg: Cfg,
  quit_event: asyncio.Event,
  seed: int | bytes | None = None
):
  
  ### Setup consumables
  vocies_cache_file = cfg['WorkCache'] / 'voices.json'
  logger.debug('Establishing an API Session w/ ElevenLabs')
  async with elvn.api_session(
    api_key=cfg['ElevenLabsAPIKey'],
  ) as api_session:
    if vocies_cache_file.exists():
      logger.debug('Loading the ElevenLabs Voices Cache')
      voices = json.loads(vocies_cache_file.read_bytes())
    else:
      logger.debug('Caching the ElevenLabs Voices')
      voices = await elvn.voices(api_session)
      vocies_cache_file.write_bytes(json.dumps(voices).encode())
 
    ### Generate the Runtime Tools Protocol
    @dataclass
    class RuntimeTools:

      ### Caching
      (cfg['WorkCache'] / 'rt-cache').mkdir(exist_ok=True)
      cache: pathlib.Path = field(default=cfg['WorkCache'] / 'rt-cache')
      def key(self, *k: str) -> str: return hashlib.md5('|'.join(k).encode()).hexdigest()
      def load(self, *k: str) -> Any | None:
        cache_file = self.cache / self.key(*k)
        if cache_file.exists(): return cache_file.read_bytes()
        return None
      def save(self, v: bytes, *k: str): (self.cache / self.key(*k)).write_bytes(v)

      ### Tool Protocol
      async def dub(self, text: str, actor: str) -> bytes:
        result = self.load(text, actor)
        if result is None:
          result = await elvn.tts(text, voices[actor], api_session)
          self.save(result, text, actor)
        return result
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

    scene = Scene(
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
    )

    ### Render the Scene

    scene_audio = await scene.render()
    (cfg['WorkCache'] / f'{scene.name}.mp3').write_bytes(
      scene_audio
    )

class Tools(Protocol):

  async def dub(self, text: str, actor: str) -> bytes: ...

@dataclass
class ShortStory:
  """The Original Short Story"""

@dataclass
class Actor:
  """An individual that can act in the scene"""
  name: str
  """Identifying Name of the Actor"""

  def __hash__(self): return hash(self.name)

@dataclass
class Role:
  """A Role in a Scene"""
  name: str
  """Identifying Name of the Role"""

  def __hash__(self): return hash(self.name)

@dataclass
class Castings:

  roles: set[Role]
  actors: set[Actor]
  castings: dict[Role, Actor]

  def __getitem__(self, k: str) -> Actor | Role:
    for r in self.roles:
      if r.name == k: return r
    for a in self.actors:
      if a.name == k: return a
    raise KeyError(k)
  def __iter__(self) -> Iterator[Actor | Role]: return iter(sorted(self.roles, key=lambda x: x.name) + sorted(self.actors, key=lambda x: x.name))
  def __contains__(self, k: str) -> bool:
    try: self.__getitem__(k)
    except KeyError: return False
    else: return True
  
  def actor_by_role(self, role: Role | str) -> Actor:
    if isinstance(role, str): role = self[role]
    assert isinstance(role, Role)
    return self.castings[role]

  def role_by_actor(self, actor: Actor | str) -> Role:
    if isinstance(actor, str): actor = self[actor]
    assert isinstance(actor, Actor)
    return { a: r for r, a in self.castings.items() }[actor]

@dataclass
class VoiceLine:
  """A Single Voice Line"""
  text: str
  actor: Actor

@dataclass
class SceneEvent:
  """An occurance of something in a scene"""

  role: Role
  """Who owns this event"""
  when: int
  """The casual time, relative to the scene, when the event occurs"""
  voice_line: VoiceLine | None
  """The voice line associated with the event if any"""

  def __hash__(self): return id((self.role, self.when))

@dataclass
class TimelineEvent:

  artifact: Any
  start: float
  end: float

  def __repr__(self) -> str: return f'{self.__class__.__name__}(artifact=bytes(size={len(self.artifact)}), start={self.start}, end={self.end})'

  def __post_init__(self):
    assert isinstance(self.start, float)
    assert isinstance(self.end, float)
    assert self.start >= 0
    assert self.end >= self.start
  
  @property
  def duration(self) -> float: return self.end - self.start
  
  def before(self, e: TimelineEvent) -> bool: return self.start <= e.start
  def after(self, e: TimelineEvent) -> bool: return self.start >= e.start
  def concurrent(self, e: TimelineEvent) -> bool:
    l, r = (self, e) if self.before(e) else (e, self)
    assert r.after(l)
    # If the Left event stops after the right event starts then it's overlapping/concurrent
    return l.end > r.start

@dataclass
class Timeline:
  """A Chronological Ordering of Events"""
  
  events: list[TimelineEvent] = field(default_factory=list)

  @property
  def start(self) -> float:
    if len(self.events) > 0: return self.events[0].start
    else: return 0.0
  @property
  def end(self) -> float:
    if len(self.events) > 0: return self.events[-1].end
    else: return 0.0
  @property
  def duration(self) -> float: self.end - self.start
  
  def insert(self, artifact: Any, start: float, end: float):
    """Insert the event into the timeline"""

    event = TimelineEvent(artifact, start, end)

    ### Get the index, by start time, where this event takes place
    idx = 0
    for i, e in enumerate(self.events):
      if e.after(event):
        idx = i
        break
    
    if idx - 1 >= 0 and idx - 1 < len(self.events):
      preceding_event = self.events[idx - 1]
      if event.concurrent(preceding_event): raise ValueError(f'Event {event} Conflicts w/ the Preceding Event {preceding_event}')

    if idx >= 0 and idx < len(self.events):
      proceeding_event = self.events[idx]
      if event.concurrent(proceeding_event): raise ValueError(f'Event {event} Conflicts w/ the Proceeding Event {proceeding_event}')

    self.events.insert(idx, event)

@dataclass
class Compositor:

  layers: dict[str, Timeline] = field(default_factory=dict)

  @property
  def start(self) -> float:
    if self.layers: return min(l.start for l in self.layers.values())
    else: return 0.0
  @property
  def end(self) -> float:
    if self.layers: return max(l.end for l in self.layers.values())
    else: return 0.0
  @property
  def duration(self) -> float: return self.end - self.start

  def add_layer(self, name: str, timeline: Timeline | None = None):
    assert name not in self.layers
    if timeline is None: timeline = Timeline()
    self.layers[name] = timeline

  def append_voice_line(self, layer: str, voice_line: bytes):
    """Adds a voice line on a layer immediately after the compositor's newest (right most) event"""
    assert layer in self.layers, layer

    logger.debug(f'{[l.end for l in self.layers.values()]}')
    when = max(l.end for l in self.layers.values())

    # Get the duration of the voice line
    metadata = MP3(io.BytesIO(voice_line)).info
    duration = metadata.length
    logger.debug(f'{(when, when + duration)}')

    self.layers[layer].insert(voice_line, when, when + duration)
  
  async def composite(self) -> bytes:
    """Render into a single MP3 File"""

    """"NOTE On FFMPEG Filter Maps

    ```
    The complex filter graph can be described by the following:

    - The final output, is the overlay of every layer's timeline.
    - Every layer itself is an overlay of multiple sublayers:
      - A base sublayer of empty input spanning the extent of the compositor's timeline (silence for audio, black frame for video, etc...)
      - Every artifact, arranged chronologically, is another sublayer & is delayed by its start time. If an artifact has no value, then an empty input is used.
    ```

    FilterGraph syntax is a sequence of FilterChains which is a sequence of Filters.

    """
    inputs: list[ffmpeg.AudioSource] = [
      ffmpeg.AudioSource(
        'anullsrc', fmt='lavfi',
      ).set(
        ( 'channel_layout', 'stereo' ),
        ( 'sample_rate', '44100' ),
        ( 'duration', self.end ), # TODO: Should this be abosulte (end) or relative (duration)?
      ),
    ]
    write_tasks: dict[str, ByteString] = {}
    outputs: list[ffmpeg.AudioSink] = [
      ffmpeg.AudioSink('outputs/artifact.mp3', codec=ffmpeg.AudioCodec('libmp3lame'), map='artifact')
    ]
    filter_graph = ffmpeg.FilterGraph()
    for name, timeline in self.layers.items():
      filter_chain = ffmpeg.FilterChain()

      ### Add the Events
      for i, e in enumerate(timeline.events):
        ### Add as input
        inputs.append(
          ffmpeg.AudioSource(f'inputs/layer_{name}_event_{i}.mp3')
        )
        assert e.artifact is not None
        write_tasks[f'inputs/layer_{name}_event_{i}.mp3'] = e.artifact
        input_idx = len(inputs) - 1
        ### Delay each input
        filter_chain.add(
          ffmpeg.Filter('adelay').label(
            'in', f'{input_idx}:a'
          ).label(
            'out', f'layer_{name}_event_{i}'
          ).set(
            f'{e.start}s',
            ('all', '1'),
          )
        )
      
      ### Mix the Events
      filter_chain.add(
        ffmpeg.Filter(
          'amix'
        ).label(
          'in', *( f'layer_{name}_event_{i}' for i in range(timeline.events) )
        ).label(
          'out', f'layer_{name}'
        ).set(
          ( 'inputs', len(timeline.events) ),
          ( 'duration', 'longest' ),
        )
      )

      ### Add the Chain
      filter_graph.add(filter_chain)
    
    ### Mix all the Layers together
    filter_graph.add(
      ffmpeg.FilterChain().add(
        ffmpeg.Filter(
          'amix'
        ).label(
          'in', *( f'layer_{name}' for name in self.layers )
        ).label(
          'out', 'artifact'
        ).set(
          ( 'inputs', len(self.layers) ),
          ( 'duration', 'longest' )
        )
      )
    )
    logger.debug(f'Filter Graph: {filter_graph.sprint()}')

    ### Create a temporary working directory, cache inputs to disk
    with tempfile.TemporaryDirectory() as _workdir:
      workdir = pathlib.Path(_workdir)
      ( workdir / 'inputs' ).mkdir(exist_ok=True)
      for file, data in write_tasks.items(): ( workdir / file ).write_bytes(data)
      ( workdir / 'outputs' ).mkdir(exist_ok=True)
      argv = [
        ### Computed Flags
        *( x.argv() for x in inputs ),
        *filter_graph.argv(),
        *( x.argv() for x in outputs ),
        ### Global Flags
        '-loglevel', 'info',
      ]
      logger.debug(f'FFMPEG CMD...\nffmpeg {" ".join(argv)}')
      cmd = await asyncio.create_subprocess_exec(
        'ffmpeg', *argv,
        stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        cwd=_workdir,
      )
      stdout, stderr = await cmd.communicate()
      assert cmd.returncode is not None
      if cmd.returncode != 0:
        logger.warning(f'FFMPEG failed on {cmd.returncode}\n' + stdout.decode() + '\n' + stderr.decode())
        raise RuntimeError(f'FFMPEG failed on {cmd.returncode}')
      return ( workdir / 'outputs' / 'artifact.mp3' ).read_bytes()

@dataclass
class Scene:
  """The smallest self-contained unit of a Manuscript"""

  name: str
  castings: Castings
  chronology: Iterable[set[SceneEvent]]
  compositor: Compositor

  _: KW_ONLY

  tools: Tools

  async def render(self) -> bytes:
    """Render the Scene"""

    ### Let's iteratively construct the scene
    for events in self.chronology:
      ### Render Voice Lines
      async with asyncio.TaskGroup() as tg:
        voice_line_tasks = {
          e: tg.create_task(self.tools.dub(
            e.voice_line,
            self.castings.actor_by_role(e.role).name,
          ))
          for e in events
          if e.voice_line
        }
      voice_lines = { e: v.result() for e, v in voice_line_tasks.items() }
      
      ### Composite the Voice Lines on the Scene's Compositor Axis
      for e, v in voice_lines.items():
        self.compositor.append_voice_line(
          layer=e.role.name,
          voice_line=v
        )
    
    ### Finally Render the Scene
    raise NotImplementedError

@dataclass
class Manuscript:
  """A Manuscript of a short story"""

  async def render(self) -> bytes:
    """Render the Manuscript in it's entirety"""
    raise NotImplementedError
