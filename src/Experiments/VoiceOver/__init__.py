"""

A simple experiment in generating voice overs for a story

"""
from __future__ import annotations
from typing import TypedDict, Protocol, Any, BinaryIO
from collections.abc import Mapping, ByteString, AsyncGenerator, Iterator, Iterable, Callable
from dataclasses import dataclass, field, KW_ONLY

import asyncio, logging, random, pathlib, json, hashlib, io, tempfile, itertools, shlex
from mutagen.mp3 import MP3

from . import (
  ElevenLabs as elvn,
  FFMPEG as ffmpeg
)

logger = logging.getLogger(__name__)

CHUNK_SIZE = int(16 * 1024)

def _ms(s: float) -> float: return s * 1E3

class Cfg(TypedDict):
  ElevenLabsAPIKey: str
  WorkCache: pathlib.Path

def load_cfg_from_env(env: Mapping[str, str]) -> Cfg:
  return {
    'ElevenLabsAPIKey': elvn.load_api_key_from_env(env),
    'WorkCache': pathlib.Path(env.get('WORK_CACHE', env.get('TMPDIR', './')).rstrip('/')) / 'elevenlabs',
  }
  
class Tools(Protocol):

  async def dub(self, text: str, actor: str, sink: BinaryIO | None = None) -> bytes | None: ...

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

  artifact: pathlib.Path
  start: float
  end: float

  def __repr__(self) -> str: return f'{self.__class__.__name__}(artifact={self.artifact.as_posix()}, start={self.start}, end={self.end})'

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
  
  def insert(self, artifact: pathlib.Path, start: float, end: float):
    """Insert the event into the timeline"""

    event = TimelineEvent(artifact, start, end)

    ### Get the index, by start time, where this event takes place
    idx = len(self.events)
    for i, e in enumerate(self.events):
      if e.after(event):
        idx = i # Record the Insertion Index
        break
    
    idx_in_bounds: Callable[[int], bool] = lambda i: i >= 0 and i < len(self.events)

    # Check the Preceeding Event isn't concurrent
    if idx_in_bounds(idx - 1):
      preceding_event = self.events[idx - 1]
      if event.concurrent(preceding_event): raise ValueError(f'Event {event} Conflicts w/ the Preceding Event {preceding_event}')

    # Check the Proceeding Event isn't concurrent
    if idx_in_bounds(idx):
      proceeding_event = self.events[idx]
      if event.concurrent(proceeding_event): raise ValueError(f'Event {event} Conflicts w/ the Proceeding Event {proceeding_event}')

    self.events.insert(idx, event)

    ### TODO: DEBUG
    for idx in range(len(self.events)):
      if idx == 0: continue
      assert idx > 0
      now = self.events[idx]
      prev = self.events[idx - 1]
      assert now is not prev
      assert now.after(prev), f'{now=}, {prev=}'
      assert prev.before(now), f'{now=}, {prev=}'
      assert not now.concurrent(prev), f'{now=}, {prev=}'
    ### TODO: DEBUG

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

  def append_voice_line(self, layer: str, voice_line: pathlib.Path):
    """Adds a voice line on a layer immediately after the compositor's newest (right most) event"""
    assert layer in self.layers, layer
    self.insert_voice_line(layer, voice_line, self.end)
  
  def insert_voice_line(self, layer: str, voice_line: pathlib.Path, when: float):
    """Adds a voice line on a layer at the specified time"""
    assert layer in self.layers, layer

    # Get the duration of the voice line
    assert voice_line.stat().st_size > 0
    with voice_line.open('rb') as f:
      metadata = MP3(f).info
      duration = metadata.length
    logger.debug(f'{(when, when + duration)}')

    # Insert the Voice Line
    self.layers[layer].insert(voice_line, when, when + duration)

  async def composite(self, output: pathlib.Path):
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
    assert output.parent.exists()
    assert output.suffixes[-1] == '.mp3'
    outputs: list[ffmpeg.AudioSink] = [
      ffmpeg.AudioSink(
        output.as_posix(),
          codec=ffmpeg.AudioCodec('libmp3lame'),
          # fmt='mp3',
          # map='artifact'
      ),
    ]
    filter_graph = ffmpeg.FilterGraph()
    for name, timeline in self.layers.items():
      logger.debug(f'Processing Layer: {name}')
      filter_chain = ffmpeg.FilterChain()

      ### Add the Events
      for i, e in enumerate(timeline.events):
        logger.debug(f'Processing Layer Event: {i}')
        ### Add as input
        assert e.artifact.exists()
        assert e.artifact.suffixes[-1] == '.mp3'
        inputs.append(
          ffmpeg.AudioSource(e.artifact.as_posix())
        )
        assert e.artifact is not None
        input_idx = len(inputs) - 1
        ### Delay each input
        filter_chain.add(
          ffmpeg.Filter(
            'adelay'
          ).label(
            'in', f'{input_idx}:a'
          ).label(
            'out', f'layer_{name}_event_{i}'
          ).set(
            f'{_ms(e.start)}',
            ('all', '1'),
          )
        )
      
      ### Mix the Events
      filter_chain.add(
        ffmpeg.Filter(
          'amix'
        ).label(
          'in', *( f'layer_{name}_event_{i}' for i in range(len(timeline.events)) )
        ).label(
          'out', f'layer_{name}'
        ).set(
          ( 'inputs', len(timeline.events) ),
          ( 'duration', 'longest' ),
        )
      )

      ### Add the Chain
      filter_graph.add(filter_chain)
    
    ### Mix all the Layers together & Normalize Volume
    filter_graph.add(
      ffmpeg.FilterChain().add(
        ffmpeg.Filter(
          'amix'
        ).label(
          'in', *( f'layer_{name}' for name in self.layers )
        ).set(
          ( 'inputs', len(self.layers) ),
          ( 'duration', 'longest' )
        )
      ).add(
        ffmpeg.Filter(
          'loudnorm'
        )
      )
    )
    logger.debug(f'Filter Graph...\n{filter_graph.sprint()}')
    logger.debug(f'Filter Graph LibAV Syntax...\n{filter_graph.libav_syntax()}')

    ### Create a temporary working directory, cache inputs to disk
    argv = list(itertools.chain(
      ### Computed Flags
      itertools.chain.from_iterable( x.argv() for x in inputs ),
      filter_graph.argv(),
      itertools.chain.from_iterable( x.argv() for x in outputs ),
      ### Global Flags
      (
        '-loglevel', 'info',
      )
    ))
    logger.debug('FFMPEG Argv...\n' + '\n'.join(f'`{x}`' for x in argv))
    logger.debug(f'FFMPEG CMD...\nffmpeg {shlex.join(argv)}')
    cmd = await asyncio.create_subprocess_exec(
      'ffmpeg', *argv,
      stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await cmd.communicate()
    logger.debug(f'FFMPEG Output...\n' + stdout.decode() + '\n' + stderr.decode())
    assert cmd.returncode is not None
    if cmd.returncode != 0:
      logger.warning(f'FFMPEG failed on {cmd.returncode}\n' + stdout.decode() + '\n' + stderr.decode())
      raise RuntimeError(f'FFMPEG failed on {cmd.returncode}')

@dataclass
class Scene:
  """The smallest self-contained unit of a Manuscript"""

  name: str
  castings: Castings
  chronology: Iterable[set[SceneEvent]]
  compositor: Compositor

  _: KW_ONLY

  tools: Tools

  async def render(self, workdir: str | pathlib.Path) -> pathlib.Path:
    """Render the Scene; returns the path to the output artifact"""
    if isinstance(workdir, str): workdir = pathlib.Path(workdir)
    assert workdir.exists()
    assert workdir.resolve().is_dir()

    inputs_dir = workdir / 'inputs'
    inputs_dir.mkdir(exist_ok=True)
    outputs_dir = workdir / 'outputs'
    outputs_dir.mkdir(exist_ok=True)

    ### Let's iteratively construct the scene
    for events in self.chronology:
      ### TODO: DEBUGGING
      _roles = [ e.role for e in events ]
      assert all( _roles.count(e.role) == 1 for e in events ), _roles
      ###

      ### Render Voice Lines
      async def _dub(text: str, actor: str, file: pathlib.Path):
        with file.open('wb') as sink:
          res = await self.tools.dub(text, actor, sink)
          assert res is None
        assert file.stat().st_size > 0

      voice_lines: dict[SceneEvent, pathlib.Path] = {}
      async with asyncio.TaskGroup() as tg:
        for e in filter(
          lambda e: e.voice_line,
          events
        ):
          voice_line_fingerprint = hashlib.md5(f'{e.role}_{e.when}_{e.voice_line}'.encode()).hexdigest()[0:16]
          voice_lines[e] = inputs_dir / f'{voice_line_fingerprint}.mp3'
          tg.create_task(_dub(
            e.voice_line,
            self.castings.actor_by_role(e.role).name,
            voice_lines[e],
          ))
      
      ### Composite the Voice Lines on the Scene's Compositor Axis
      end = self.compositor.end
      for e in events:
        # Insert the voice lines at the current end on their respective layers
        assert isinstance(voice_lines[e], pathlib.Path)
        self.compositor.insert_voice_line(
          layer=e.role.name,
          voice_line=voice_lines[e],
          when=end,
        )

    ### Finally Render the Scene
    artifact_file = outputs_dir / 'artifact.mp3'
    artifact_file.unlink(missing_ok=True) # Cleanup old renders
    await self.compositor.composite(artifact_file)
    return artifact_file

@dataclass
class Manuscript:
  """A Manuscript of a short story; Acts are indexed 1"""

  scenes: dict[str, Scene] = field(default_factory=dict)
  """All scenes keyed by name"""
  acts: list[list[str]] = field(default_factory=lambda: [])
  """The Acts & their scenes"""

  def add_act(self):
    self.acts.append([])
    return self
  def add_scene(self, name: str, act: int, scene: Scene):
    assert name not in self.scenes
    self.scenes[name] = scene
    act_idx = act - 1
    assert act_idx < len(self.acts)
    self.acts[act_idx].append(name)
    return self

  async def render(self, workdir: str | pathlib.Path):
    """Render the Manuscript in it's entirety"""
    if isinstance(workdir, str): workdir = pathlib.Path(workdir)
    assert workdir.exists() and workdir.resolve().is_dir()

    scenes_dir = workdir / 'scenes'
    scenes_dir.mkdir(exist_ok=True)
    scene_tasks: dict[str, asyncio.Task] = {}
    async with asyncio.TaskGroup() as tg:
      for name, scene in self.scenes.items():
        scene_workdir = scenes_dir / name
        scene_workdir.mkdir(exist_ok=True)
        scene_tasks[name] = tg.create_task(
          scene.render(
            workdir=scene_workdir
          )
        )
    
    acts_tree = workdir / 'acts'
    acts_tree.mkdir(exist_ok=True)
    for act_num, act in enumerate(self.acts, start=1):
      act_dir = acts_tree / f'Act {act_num:02d}'
      act_dir.mkdir(exist_ok=True)
      for scene_num, scene_name in enumerate(act, start=1):
        scene_artifact = scene_tasks[scene_name].result()
        assert isinstance(scene_artifact, pathlib.Path)
        assert scene_artifact.exists()
        ( act_dir / f'Act {act_num} - Scene {scene_num:02d} - {scene_name}{''.join(scene_artifact.suffixes)}' ).symlink_to(
          scene_artifact
        )

@dataclass
class ShortStory:
  """The Original Short Story"""

### Avoid Circular Imports

from . import (
  ElevenLabs as elvn,
)

__all__ = [
  'CHUNK_SIZE',
  'Cfg', 'load_cfg_from_env',
  'Tools',
  'Actor', 'Role', 'Castings',
  'VoiceLine', 'SceneEvent', 'TimelineEvent', 'Timeline',
  'Compositor', 'Scene', 'Manuscript', 'ShortStory',
  'elvn',
]