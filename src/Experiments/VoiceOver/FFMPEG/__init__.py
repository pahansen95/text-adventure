from __future__ import annotations
from typing import Literal
from collections.abc import ByteString
from dataclasses import dataclass, field, KW_ONLY

import asyncio, logging, pathlib, io, tempfile, itertools
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

@dataclass
class Codec:
  """Some Media [En/De]Coder"""

  name: str
  """Name of the Codec"""
  args: list[str | tuple[str, str]] = field(default_factory=list)
  """List of configurable arguments to pass to the codec"""

  def set(self, *x: str | tuple[str, str]):
    """Set arguments on the Codec"""
    self.args.extend(x)
    return self

@dataclass
class AudioCodec(Codec):
  """Some Audio En/Decoder"""

  def argv(self) -> list[str]:
    """return the FFMPEG CLI Args"""
    return [
      '-c:a', f'{self.name}', *(
        (
          ( f'-{a[0]}', f'{a[1]}' )
          if isinstance(a, tuple) else
          ( f'-{a}', )
        ) for a in self.args
      )
    ]

@dataclass
class MediaTarget:
  """Some Media Source or Sink"""

  url: str
  """The Media's URL"""
  args: list[str | tuple[str, str]] = field(default_factory=list)
  """List of configurable arguments to pass to the target media"""
  fmt: str | None = field(default=None)
  """[Optional] The Format of the Media"""
  codec: Codec | None = field(default=None)
  """[Optional] The Codec of the Media"""
  duration: float | None = field(default=None)
  """[Optional] The extents of the Media"""

  def set(self, *x: str | tuple[str, str]):
    """Set arguments on the Media"""
    self.args.extend(x)
    return self
  
@dataclass
class MediaSource(MediaTarget):
  """A Media Input"""

@dataclass
class AudioSource(MediaSource):
  """An Audio Input"""

  codec: AudioCodec
  """[Optional] The Audio Codec of the Audio Source"""

  def argv(self):
    argv = []
    if self.fmt: argv.append(( '-f', f'{self.fmt}' ))
    if self.duration: argv.append(( '-t', f'{self.duration}' ))
    if self.codec: argv.append( self.codec.argv() )
    _url = self.url
    if self.args:
      _url += '=' + ':'.join(
        (
          f'{a[0]}={a[1]}'
          if isinstance(a, tuple) else
          f'{a}'
        ) for a in self.args
      )
    argv.append(( '-i', _url ))
    return list(itertools.chain.from_iterable(argv))

@dataclass
class MediaSink(MediaTarget):
  """A Media Output"""

  target: str | None = field(default=None)
  """[Optional] The Target File Type of the Output File"""
  map: str | None = field(default=None)
  """[Optional] The Stream to map to this sink; either an input identifier or a link label: see -map"""

@dataclass
class AudioSink(MediaSink):
  """An Audio Output"""

  codec: AudioCodec | None = None
  """[Optional] The Audio Codec of the Audio Sink"""

  def argv(self):
    argv = []
    if self.fmt: argv.append(( '-f', f'{self.fmt}' ))
    if self.duration: argv.append(( '-t', f'{self.duration}' ))
    if self.codec: argv.append( self.codec.argv() )
    if self.target: argv.append(( '-t', self.target ))
    if self.map: argv.append(( '-map', self.map ))
    _url = self.url
    if self.args:
      _url += '=' + ':'.join(
        (
          f'{a[0]}={a[1]}'
          if isinstance(a, tuple) else
          f'{a}'
        ) for a in self.args
      )
    argv.append(( _url, ))
    return list(itertools.chain.from_iterable(argv))

@dataclass
class Filter:
  
  name: str
  """The name of the filter"""
  pads: dict[Literal['in', 'out'], set[str]] = field(default_factory=lambda: { 'in': set(), 'out': set() })
  """The set of input/output pad labels"""
  args: list[str | tuple[str, str]] = field(default_factory=list)
  """The set of arguements for the Filter"""
  
  def set(self, *x: str | tuple[str, str]) -> Filter:
    """Set arguments on the Filter"""
    self.args.extend(x)
    return self
  
  def label(self, k: Literal['in', 'out'], *name: str) -> Filter:
    """Add an input/output pad labels"""
    assert isinstance(name, tuple)
    self.pads[k].update(name)
    return self

  def sprint(self, idnt: int = 0) -> str:
    """Pretty Print to string"""
    t = idnt * ' '
    t2 = (idnt + 2) * ' '
    return '\n'.join((
      f'{t}{self.__class__.__name__}(',
        '\n'.join(f'{t2}{x}' for x in (
          f'Name: {self.name}',
          f'Input Pads: {self.pads["in"]}',
          f'Output Pads: {self.pads["out"]}',
          f'Args: {[ ( f'{x[0]}={x[1]}' if isinstance(x, tuple) else x ) for x in self.args ]}',
        )),
      f'{t})',
    ))
  
  def libav_syntax(self) -> str:
    """Converts the FilterGraph into the Syntax Expected by libavfilter"""
    l = []
    if self.pads['in']:
      for lbl in self.pads['in']:
        l.append(f'[{lbl}]')
    l.append(self.name)
    if self.args:
      l[-1] += "='" + ':'.join(
        (
          f'{a[0]}={a[1]}'
          if isinstance(a, tuple)
          else
          a
        ) for a in self.args
      ) + "'"
    if self.pads['out']:
      for lbl in self.pads['out']:
        l.append(f'[{lbl}]')
    assert l
    return ' '.join(l)

@dataclass
class FilterChain:
  
  seq: list[Filter] = field(default_factory=list)
  """The Sequence of Filters to Chain"""
  
  def add(self, *f: Filter) -> FilterChain:
    """Add the sequence of Filters"""
    self.seq.extend(f)
    return self

  def sprint(self, idnt: int = 0) -> str:
    """Pretty Print to string"""
    t = idnt * ' '
    return '\n'.join((
      f'{t}{self.__class__.__name__}(',
      '\n'.join( f'{s.sprint(idnt+2)}' for s in self.seq ),
      f'{t})',
    ))
  
  def libav_syntax(self) -> str:
    """Converts the FilterGraph into the Syntax Expected by libavfilter"""
    return ',\n'.join(s.libav_syntax() for s in self.seq)

@dataclass
class FilterGraph:
  
  seq: list[FilterChain] = field(default_factory=list)
  """The Sequence of FilterChains"""

  def add(self, *f: FilterChain) -> FilterGraph:
    """Add a Filter Chain to the Graph"""
    self.seq.extend(f)
    return self
  
  def sprint(self, idnt: int = 0) -> str:
    """Pretty Print to string"""
    t = idnt * ' '
    return '\n'.join((
      f'{t}{self.__class__.__name__}(',
      '\n'.join( f'{s.sprint(idnt+2)}' for s in self.seq ),
      f'{t})',
    ))
  
  def libav_syntax(self) -> str:
    """Converts the FilterGraph into the Syntax Expected by libavfilter"""
    return ';\n'.join(s.libav_syntax() for s in self.seq)

  def argv(self) -> list[str]:
    """return the FFMPEG CLI Args"""
    return [ '-filter_complex', self.libav_syntax() ]
