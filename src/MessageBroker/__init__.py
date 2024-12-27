from __future__ import annotations
from dataclasses import dataclass, field, KW_ONLY
from typing import TypedDict, TypeVar, Generic, Any, Protocol, Literal, NamedTuple
from collections.abc import Callable, ByteString, Iterator, AsyncGenerator, Mapping
from collections import deque

import logging, asyncio, time

logger = logging.getLogger(__name__)

_DATUM = time.monotonic_ns()
def _get_time() -> int: return time.monotonic_ns() - _DATUM # TODO: Refactor out

class StreamOverload(RuntimeError): ...

@dataclass
class MessageStream:
  """An ordered queue of streaming messages"""

  log: deque[Message] = field(default_factory=deque)
  """The Ordered Log of Messages in the stream"""
  capacity: int = field(default=int(10E6)) # 10MB
  """The Maximum capacity of the Message Stream in bytes"""

  _: KW_ONLY
  _size: int = field(default=0)
  """The current size of the message stream in bytes"""

  @property
  def size(self) -> int:
    """The current size of the message stream in bytes"""
    return self._size
  
  @property
  def count(self) -> int:
    """The current number of messages in the log"""
    return len(self.log)
  
  def __len__(self) -> int: return len(self.log)

  async def pop(self) -> Message:
    """Pop a Message from the head of the stream"""
    while len(self.log) <= 0: await asyncio.sleep(0) # Block until a Message is available
    m = self.log.popleft()
    # TODO: Update Size
    return m
  
  async def push(self, m: Message):
    """Push a Message onto the tail of the stream"""
    # TODO; Enforce Size limits
    self.log.append(m)
    # TODO: Update Size

class StreamIdx(NamedTuple):
  peer_id: str
  topic: str
  kind: Literal['pub', 'sub']

@dataclass
class StreamRevIdx:
  """Reverse Index for a Message Stream"""
  peer_id: dict[str, set[StreamIdx]] = field(default_factory=dict)
  topic: dict[str, set[StreamIdx]] = field(default_factory=dict)
  kind: dict[Literal['pub', 'sub'], set[StreamIdx]] = field(default_factory=dict)

  def add(self, idx: StreamIdx):
    assert idx.kind in ('pub', 'sub')
    if idx.peer_id not in self.peer_id: self.peer_id[idx.peer_id] = set()
    self.peer_id[idx.peer_id].add(idx)
    if idx.topic not in self.topic: self.topic[idx.topic] = set()
    self.topic[idx.topic].add(idx)
    if idx.kind not in self.kind: self.kind[idx.kind] = set()
    self.kind[idx.kind].add(idx)
  
  def remove(self, idx: StreamIdx):
    assert idx.kind in ('pub', 'sub')
    if idx.peer_id in self.peer_id:
      self.peer_id[idx.peer_id].remove(idx)
      if not self.peer_id[idx.peer_id]: del self.peer_id[idx.peer_id]
    if idx.topic in self.topic:
      self.topic[idx.topic].remove(idx)
      if not self.topic[idx.topic]: del self.topic[idx.topic]
    if idx.kind in self.kind:
      self.kind[idx.kind].remove(idx)
      if not self.kind[idx.kind]: del self.kind[idx.kind]
  
  def lookup(self, peer_id: str | None = None, topic: str | None = None, kind: Literal['pub', 'sub'] | None = None) -> set[StreamIdx]:
    """Lookup all Indices matching the provided set of keys; must provide at least 1 key"""
    assert not ( peer_id is None and topic is None and kind is None )
    assert kind is None or kind in ('pub', 'sub')
    sets = []
    if peer_id is not None: sets.append(self.peer_id.get(peer_id, set()))
    if topic is not None: sets.append(self.topic.get(topic, set()))
    if kind is not None: sets.append(self.kind.get(kind, set()))
    assert len(sets) > 0
    idx = sets[0]
    for s in sets[1:]: idx = idx & s
    return idx

@dataclass
class StreamRegistry:
  """Manages the total set of Message Streams"""

  streams: dict[StreamIdx, MessageStream] = field(default_factory=dict)
  """Map[(PeerID, Topic, Kind), Stream]"""
  rev_idx: StreamRevIdx = field(default_factory=StreamRevIdx)

  def __getitem__(self, k: StreamIdx) -> MessageStream: return self.streams[k]
  def __iter__(self) -> Iterator[StreamIdx]: return iter(self.streams)
  def __contains__(self, k: StreamIdx) -> bool: return k in self.streams

  def add(self, peer_id: str, topic: str, kind: Literal['pub', 'sub'], stream: MessageStream | None = None) -> MessageStream:
    assert kind in ('pub', 'sub')
    k = StreamIdx(peer_id, topic, kind)
    assert k not in self.streams
    if stream is None: stream = MessageStream()
    self.streams[k] = stream
    self.rev_idx.add(k)
    return stream
  
  def remove(self, peer_id: str, topic: str, kind: Literal['pub', 'sub']):
    assert kind in ('pub', 'sub')
    k = StreamIdx(peer_id, topic, kind)
    assert k in self.streams
    self.rev_idx.remove(k)
    del self.streams[k]
  
  def lookup(self, peer_id: str, topic: str, kind: Literal['pub', 'sub']) -> MessageStream:
    assert kind in ('pub', 'sub')
    return self.streams[StreamIdx(peer_id, topic, kind)]

class AddrPath:

  @classmethod
  def unicast(cls, peer_id: str) -> str: return f'/UCAST/{peer_id}'
  @classmethod
  def is_unicast(cls, path: str) -> bool: return path.startswith('/UCAST/')
  @classmethod
  def multicast(cls, group: str) -> str: return f'/MCAST/{group.lstrip("/")}'
  @classmethod
  def is_multicast(cls, path: str) -> bool: return path.startswith('/MCAST/')
  @classmethod
  def broadcast(cls) -> str: return '/BCAST'
  @classmethod
  def is_broadcast(cls, path: str) -> bool: return path == '/BCAST'

@dataclass
class TopicPartition:
  """A Single Partition in the Broker"""

  topic: str
  """The Topic of this partition"""
  log: MessageStream = field(default_factory=MessageStream)
  """The Current ordered log of the Topic Partition"""
  publishers: dict[str, MessageStream] = field(default_factory=dict)
  """Mapping[PeerID, MessageStream]: The Message Streams for all producing peers"""
  subscribers: dict[str, MessageStream] = field(default_factory=dict)
  """Mapping[PeerID, MeasageStream]: The Message Streams for all consuming peers"""

  def add_publisher(self, peer_id: str, stream: MessageStream | None = None) -> MessageStream:
    assert peer_id not in self.publishers
    if stream is None: stream = MessageStream()
    self.publishers[peer_id] = stream
    return stream
  
  def remove_publisher(self, peer_id: str):
    assert peer_id in self.publishers
    del self.publishers[peer_id]

  def add_subscriber(self, peer_id: str, stream: MessageStream | None = None) -> MessageStream:
    assert peer_id not in self.subscribers
    if stream is None: stream = MessageStream()
    self.subscribers[peer_id] = stream
    return stream
  
  def remove_subscriber(self, peer_id: str):
    assert peer_id in self.subscribers
    del self.subscribers[peer_id]

  async def pull_msg(self) -> Message:
    """Pulls the next available message from the producers"""
    # TODO: Refactor; how can we be more efficient? How do we ensure fair scheduling?
    while True:
      for peer_id, stream in self.publishers.items():
        if stream.count > 0: return await stream.pop()
      await asyncio.sleep(0) # If no messages are available then yield to the event loop

  async def _listener_step(self):

    ### Get the first message available from all ingress members

    msg = await self.pull_msg()

    ### Add the message to the log
    try: await self.log.push(msg)
    except StreamOverload as e: raise NotImplementedError from e # TODO: Handle Log Overloads

    ### Inform the producer that the message has been sent
    msg.sent.set()

  async def listener(self) -> AsyncGenerator[None, None, None]:

    # TODO: Setup

    yield None # Yield to the event loop once setup is complete

    while True:
      await self._listener_step()
      yield None

  async def _router_step(self):

    ### Get the next available message from the Log

    msg = await self.log.pop()

    ### Route the Message

    # TODO: Refactor Peer ID Discovery
    if msg.is_unicast():
      
      peer_ids = [ msg.dst.removeprefix('/UCAST/') ]
    
    else:
      assert msg.is_broadcast() or msg.is_multicast(), msg.topic

      if msg.is_broadcast(): peer_ids = list(self.subscribers.keys())
      else: raise NotImplementedError

    # TODO: Refactor so we push things concurrently
    for peer_id in peer_ids:
      try: await self.subscribers[peer_id].push(msg.copy(recv=CasualEvent())) # TODO: Does this do what I think it does?
      except StreamOverload as e: raise NotImplementedError from e
    # TODO: What happens if we fail to route the message to a peer? Do we fail everything? Do we retry just the peer? Handle Now or Later?
    msg.recv.set() # TODO: Do we need to set this on the original message?

  async def router(self) -> AsyncGenerator[None, None, None]:
    """Route Messages"""
    # TODO: Setup

    yield None # Yield to the event loop once setup is complete

    while True:
      await self._router_step()
      yield None

@dataclass
class TopicRegistry:

  topics: dict[str, TopicPartition] = field(default_factory=dict)
  """Map[Path, Record]"""
  streams: StreamRegistry = field(default_factory=StreamRegistry)
  _: KW_ONLY
  _gens: dict[str, dict[Literal['router', 'listener'], AsyncGenerator]] = field(default_factory=dict)

  def __getitem__(self, k: str) -> TopicPartition: return self.topics[k]
  def __iter__(self) -> Iterator[str]: return iter(self.topics)
  def __contains__(self, k: str) -> bool: return k in self.topics

  def _add_topic(self, topic: str):
    assert topic not in self.topics
    self.topics[topic] = TopicPartition(topic)
    # Create the Generators
    self._gens[topic] = {
      'router': self.topics[topic].router(),
      'listener': self.topics[topic].listener()
    }
  
  def _remove_topic(self, topic: str):
    assert topic in self.topics
    assert not self.topics[topic].publishers # Can only remove a topic w/ no active publishers
    assert not self.topics[topic].subscribers # (Maybe?) Can only remove a topic w/ not active subscribers
    del self.topics[topic]
    del self._gens[topic] # Drop the Generators; TODO: Cleanup?
  
  async def _wait_for_topic(self, topic: str):
    # TODO: Refactor
    while topic not in self.topics: await asyncio.sleep(0)

  async def publish(self, peer_id: str, topic: str):
    if topic not in self.topics: self._add_topic(topic)
    assert peer_id not in self.topics[topic].publishers
    # TODO: Refactor
    stream = self.topics[topic].add_publisher(peer_id)
    self.streams.add(peer_id, topic, 'pub', stream=stream)
  
  async def unpublish(self, peer_id: str, topic: str):
    assert topic in self.topics
    assert peer_id in self.topics[topic].publishers
    self.topics[topic].remove_publisher(peer_id)
    self.streams.remove(peer_id, topic, 'pub')
    if not self.topics[topic].publishers: # If no publishers remain
      self._remove_topic(topic)
      assert topic not in self.topics

  async def subscribe(self, peer_id: str, topic: str):
    if topic not in self.topics: await self._wait_for_topic(topic)
    assert peer_id not in self.topics[topic].subscribers
    # TODO: Refactor
    stream = self.topics[topic].add_subscriber(peer_id)
    self.streams.add(peer_id, topic, 'sub', stream=stream)
  
  async def unsubscribe(self, peer_id: str, topic: str):
    assert topic in self.topics
    assert peer_id in self.topics[topic].subscribers
    self.topics[topic].remove_subscriber(peer_id)
    self.streams.remove(peer_id, topic, 'sub')

pub_msg_t = tuple[dict, asyncio.Event]
sub_msg_t = tuple[dict, asyncio.Event]

@dataclass
class CasualEvent:
  """Some Event in time; can only be set once"""

  when: int | None = field(default=None)
  event: asyncio.Event = field(default_factory=asyncio.Event)

  def set(self):
    assert not self.event.is_set()
    self.when = _get_time()
    self.event.set()
  
  async def wait(self):
    await self.event.wait()
    assert self.when is not None

@dataclass
class Message:
  """A Message in the Broker"""

  id: str
  src: str
  dst: str
  topic: str
  payload: ByteString
  _: KW_ONLY
  sent: CasualEvent = field(default_factory=CasualEvent)
  recv: CasualEvent = field(default_factory=CasualEvent)

  def copy(self, **kwargs) -> Message:
    """Create a shallow copy of the Message; useful for overridding certain things such as destination or casual events"""
    return Message(**{
      'id': self.id,
      'src': self.src,
      'dst': self.dst,
      'topic': self.topic,
      'payload': self.payload,
      'sent': self.sent,
      'recv': self.recv,
      **kwargs,
    })

  def is_broadcast(self) -> bool: return AddrPath.is_broadcast(self.dst)
  def is_multicast(self) -> bool: return AddrPath.is_multicast(self.dst)
  def is_unicast(self) -> bool: return AddrPath.is_unicast(self.dst)


# @dataclass
# class TopicRegistryPeerView:
#   """A Peer Specific View on the Topic Registry"""

#   peer_id: str
#   _: KW_ONLY
#   registry: TopicRegistry

#   @property
#   def topics(self) -> set[str]: return set(self.registry.topics.keys())
#   @property
#   def publishments(self) -> set[str]: raise NotImplementedError
#   @property
#   def subscriptions(self) -> set[str]: raise NotImplementedError

#   async def publish(self, topic: str): raise NotImplementedError
#   async def unpublish(self, topic: str): raise NotImplementedError
#   async def subscribe(self, topic: str): raise NotImplementedError
#   async def unsubscribe(self, topic: str): raise NotImplementedError

class Publish(Protocol):

  @property
  def publishments(self) -> set[str]: raise NotImplementedError
  async def publish(self, peer_id: str, topic: str): raise NotImplementedError
  async def unpublish(self, peer_id: str, topic: str): raise NotImplementedError

class Subscribe(Protocol):

  @property
  def subscriptions(self) -> set[str]: raise NotImplementedError
  async def subscribe(self, peer_id: str, topic: str): raise NotImplementedError
  async def unsubscribe(self, peer_id: str, topic: str): raise NotImplementedError

class Produce(Protocol):
  async def send(self, src: str, dst: str, topic: str, payload: ByteString): raise NotImplementedError
  async def wait_till_empty(self): raise NotImplementedError
  def cancel(self): raise NotImplementedError

class Consume(Protocol):
  async def recv(self, topic: str) -> Message: raise NotImplementedError

@dataclass
class MessageProducer:
  """A Single Producer of Messages"""

  peer_id: str
  stream: StreamRegistry
  _: KW_ONLY
  _inflight: set[asyncio.Task] = field(default_factory=set, init=False)

  async def send(self,
    src: str,
    dst: str,
    topic: str,
    payload: ByteString,
  ):
    self._inflight.add(asyncio.current_task())
    try:
      ### TODO: Optimize Message Creation Process
      msg = Message(
        id=hex(_get_time()), # TODO: Need some external construct to assign an ID to the Message; probably the broker?
        src=src,
        dst=dst,
        topic=topic,
        payload=payload
      )
      
      ### Queue the message to be sent
      assert StreamIdx(self.peer_id, topic, 'pub') in self.stream
      try: await self.stream.lookup(self.peer_id, topic, 'pub').push(msg)
      except StreamOverload as e: raise NotImplementedError from e # TODO: Handle Overloads

      ### Wait for the Message to be sent
      await msg.sent.wait()
      assert msg.sent.when is not None

      ### Return the Message ID
      return msg.id
    finally: self._inflight.remove(asyncio.current_task())

  async def wait_till_empty(self): # TODO: Refactor
    while self._inflight: await asyncio.sleep(0)
  
  def cancel(self):
    for t in self._inflight: t.cancel()

@dataclass
class MessageConsumer:
  """A Consumer of Messages"""

  peer_id: str
  stream: StreamRegistry

  async def recv(self, topic: str) -> Message:
    assert StreamIdx(self.peer_id, topic, 'sub') in self.stream

    ### Pull a Message from the Broker

    msg = await self.stream.lookup(self.peer_id, topic, 'sub').pop() # TODO: How do we ensure Message Ordering in Delivery

    ### Let the Broker know we recieved the Message
    
    msg.recv.set()
    assert msg.recv.when is not None

    ### Return the Message

    return msg

@dataclass
class TopicMember:
  """An individual contributor able to publish & subscribe to topics"""

  peer_id: str
  registry: TopicRegistry
  _: KW_ONLY
  publishments: set[str] = field(default_factory=set)
  subscriptions: set[str] = field(default_factory=set)

  async def publish(self, topic: str):
    await self.registry.publish(self.peer_id, topic)
    self.publishments.add(topic)

  async def unpublish(self, topic: str):
    await self.registry.unpublish(self.peer_id, topic)
    self.publishments.remove(topic)

  async def subscribe(self, topic: str):
    await self.registry.subscribe(self.peer_id, topic)
    self.subscriptions.add(topic)

  async def unsubscribe(self, topic: str):
    await self.registry.unsubscribe(self.peer_id, topic)
    self.subscriptions.remove(topic)

@dataclass
class PeerSession:
  """Connection lifecycle of a peer to a broker. Manages session state & provides an interface to interact w/ the broker.

  The provided interface allows a Peer to

  - Disconnect from the session
  - Setup publishments on topic partitions
  - Setup subscriptions on topic partions
  - Setup subscription watches on topic trees
  - Teardown publishments, subscriptions & subscription watches
  - Send Messages on Topics
  - Recieve Messages on Topics

  """
  peer_id: str
  """The ID of this Peer"""
  pub: Publish
  """Protocol for publishing on topics"""
  sub: Subscribe
  """Protocol for subscribing to topics"""
  tx: Produce
  """Protocol for Producing Messages"""
  rx: Consume
  """Protocol for Consuming Messages"""

  async def disconnect(self, force: bool = False):
    """Disconnect the Client from the Distributed System.
    
    If `force` then:
      - cancel all inflight messages

    """

    ### First Block All Actions
    async def _block_action(*args, **kwargs): raise RuntimeError(f'Action Blocked: Peer {self.peer_id} is disconnecting')
    publish = self.publish
    self.publish = _block_action
    unpublish = self.unpublish
    self.unpublish = _block_action
    put = self.put
    self.put = _block_action
    subscribe = self.subscribe
    self.subscribe = _block_action
    unsubscribe = self.unsubscribe
    self.unsubscribe = _block_action
    get = self.get
    self.get = _block_action
    
    ### Next Teardown
    async def _unpublish():
      """Unpublish all publishments"""
      if force: self.tx.cancel() # Go ahead & cancel inflight messages if we are forcing a disconnection
      await unpublish(*self.pub.publishments)
      await self.tx.wait_till_empty()
    
    async def _unsubscribe():
      """Unsubscribe all subscriptions"""
      await unsubscribe(*self.sub.subscriptions)
    
    async with asyncio.TaskGroup() as tg:
      unpub = tg.create_task(_unpublish())
      unsub = tg.create_task(_unsubscribe())
    
    ... # TODO ?

  async def publish(self, *topic: str):
    """Declare the Client will Publish to the provided topics"""
    async with asyncio.TaskGroup() as tg:
      for t in topic:
        if t not in self.pub.publishments:
          tg.create_task(self.pub.publish(t))
  
  async def unpublish(self, *topic: str):
    """Declare the Client will stop publishing to the provided topics"""
    async with asyncio.TaskGroup() as tg:
      for t in topic:
        if t in self.pub.publishments:
          tg.create_task(self.pub.unpublish(t))

  async def subscribe(self, *topic: str):
    """Declare the Client will Subscribe to the provided topics"""
    async with asyncio.TaskGroup() as tg:
      for t in topic:
        if t not in self.sub.subscriptions:
          tg.create_task(self.sub.subscribe(t))

  async def unsubscribe(self, *topic: str):
    """Declare the Client will stop subscribing to the provided topics"""
    async with asyncio.TaskGroup() as tg:
      for t in topic:
        if t in self.sub.subscriptions:
          tg.create_task(self.sub.unsubscribe(t))

  async def put(self, topic: str, dst: str, payload: ByteString):
    """Enqueue a Topic for transmission; blocks until the message is pulled from the queue"""
    assert topic in self.pub.publishments
    await self.tx.send(
      src=AddrPath.unicast(self.peer_id),
      dst=dst,
      topic=topic,
      payload=payload,
    )

  async def get(self, topic: str) -> Message:
    """Pull the next available message on the topic"""
    assert topic in self.sub.subscriptions
    return await self.rx.recv(topic)

@dataclass
class MessageBroker:

  peers: dict[str, PeerSession] = field(default_factory=dict)
  """All peers w/ an active connection to the Broker"""
  topics: TopicRegistry = field(default_factory=TopicRegistry)
  """The Registry of Topics managed by the Message Broker"""

  async def connect(self,
    peer_id: str,
  ) -> PeerSession:
    assert peer_id not in self.peers

    # TODO: Refactor: Need to Move Stream Registry creation out of the Topic Registry dataclass factory function

    topic_member = TopicMember(
      peer_id=peer_id,
      registry=self.topics
    )
    
    session = PeerSession(
      peer_id=peer_id,
      pub=topic_member,
      sub=topic_member,
      tx=MessageProducer(
        peer_id=peer_id,
        stream=self.topics.streams,
      ),
      rx=MessageConsumer(
        peer_id=peer_id,
        stream=self.topics.streams,
      ),
    )
    self.peers[peer_id] = session
    return session

