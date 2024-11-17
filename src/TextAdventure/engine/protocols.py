from __future__ import annotations
from typing import Any, Protocol
from collections.abc import AsyncGenerator, Mapping, Iterable
from contextlib import asynccontextmanager
import multiprocessing as mp
pid_t = bytes
topic_t = tuple[str]
event_t = Any
q_item_t = tuple[topic_t, event_t]

class MessageBroker(Protocol):
  """The Message Broker handles Event Messages in a Distributed System.

  A distributed system is one consisting of multiple processes each
  publishing messages of occured events to one another. Processes are
  only aware of events of another process if they receive such a message.
  
  Causal Ordering ("happened before" relation →) in a Distributed System is defined when:

  1. Events are in same process: 
    - If a and b are events in same process and a comes before b, then a → b
  2. Message sending/receiving:
    - If a is sending a message and b is receiving that same message, then a → b
  3. Transitivity:
    - If a → b and b → c, then a → c

  Concurrency:

  - Events a and b are concurrent if a -/→ b AND b -/→ a
  - Concurrent events have no causal relationship

  Important Distinctions:

  - Time(a) < Time(b) does NOT imply a → b
  - However, if a → b then the Clock Condition requires Time(a) < Time(b)
  - Physical time is not needed to define the happened-before relation

  Based on this we design our engine as follows:

  - We establish the terms:
    - `Process` being equivalent to some executing software w/ access to OS Synchronization Primatives. Normatively; an OS Process or Thread.
    - `Peer` mapping to a "Process" as defined by Lamport's Definition of Distributed Systems.
      - Which implies that peers are associated w/ logical clocks & can send & recieve events.
    - `Broker` which manages the implementation specifics of Event Distribution via Message Passing between `Peers`, both local or network addressable.
  - An Entity is a `Peer`.
  - A Capability applied maps to one or more "Events" that A) increments a Peer's Logical clock & B) can optionally result in the sending of a message.
  
  The Message Broker consists of:

  - Sending/Recieving Messages
  - Clock Synchronization
  - Causality Management

  First, an Entity must register itself as a Peer in the System w/ the Broker, it is assigned a unique ID it is addresable at.
  Next, the Peer must register those `topics` it wishes to send & recieve events on.
    - Every Peer is automatically registered under an `INTERNAL` publishing/subscribing topic which is used for
        A) internal synchronization for the peer &
        B) incrementing the peer's logical clock without publishing an event.
  The Broker will provide the entity a pair of queues, Send & Recv, that provide the peers an interface for
    A) registering events, both internal & external
    B) managing the logical clock
  The logical clocks are incremented when an event is put on or popped from the queue.
  The `Send` Queue will queue a message for transmission by the Broker. The `Recv` Queue will be populated by the Broker w/ recieved messages.
  The Broker will handle synchronization of logical clocks between Peers in the other processes.
  The Message Broker will detect conflicts in causal relationships. When a conflict is detected, the Send/Recv Queues are locked
  and won't be released until the peer resolves the conflict.
  Entity Message Ordering is guaranteed (& implemented) by the Broker.

  # TODO: Things to Implement

  The following concepts/features are necessary but not currently implemented:

  - Causal Conflict Resolution: How do peers resolve conflicts in causality.
  - Peer "Crash" handling: How does the system handle a peer crashing or otherwise misbehaving.
    - "Crash" can refer to any unintended behaviour including unexpected Partitioning (ex. 2 brokers lose network connectivity)

  """

  async def add_peer(self,
    id: pid_t | None = None,
    subscriptions: set[topic_t] | None = None,
    publishments: set[topic_t] | None = None,
  ) -> tuple[pid_t, tuple[send_queue_t, recv_queue_t]]:
    """Registers a peer with the System; considered an Event in the system.

    Args:
      `id`: A system-wide unique identity for the peer can be provided (ie. re-registration) or generated (by default).
      `subscriptions`: The set of event topics the peer will subscribe to. Always includes the `INTERNAL` loopback topic.
      `publishments`: The set of event topics the peer will publish to. Always includes the `INTERNAL` loopback topic.

    Returns:
      pid_t: The Peer ID
      tuple[queue_t, queue_t]: The Send & Recv Queue for the Peer
    """
    raise NotImplementedError
  
  async def remove_peer(self,
    id: pid_t,
    persist: bool = True,
  ):
    """Deregisters a peer from the System; considered an Event in the system.

    All Event Messages currently in the Send Queue will be drained first (that is all messages will be published to ensure state consistency).
    All Event Messages in the Recv Queue (after the Send Queue is drained) will be persisted for eventual repopulation during a re-registration.
      - If a peer is to be permanently removed set `persist` to False; the peer ID may never rejoin the system & the ID may never be re-used.
      - It is garunteed the Recv Queue will be lock immediately after the Send Queue is drained.
    """
    raise NotImplementedError
  
  async def tx_loop(self) -> AsyncGenerator:
    """Handles the Transmission of Messages to Peers (via itself or other brokers)"""
    raise NotImplementedError

  async def rx_loop(self) -> AsyncGenerator:
    """Handles the Receipt of Messages from Peers (from itself or other brokers)"""
    raise NotImplementedError
  
  async def causality_loop(self) -> AsyncGenerator:
    """Handles causality state in the system:

    - Synchronizes clock state.
    - Detects conflicts in causality.

    """
    raise NotImplementedError

class Peer(Protocol):
  """A Participating Peer in the Distributed System"""

  async def connect(self):
    """Connect the Peer to the Distributed System"""
    raise NotImplementedError
  
  async def disconnect(self):
    """Disconnect the Peer from the Distributed System"""
    raise NotImplementedError

  async def event_loop(self) -> AsyncGenerator:
    """The Event Processing Loop for the Peer."""
    raise NotImplementedError

op_t = Any
state_t = Mapping
state_log_t = Iterable[op_t]
class PeerState(Protocol):
  """Manage, over time, the State of a Peer in a Distributed System.

  In our engine, world state is defined as the collective state of all peers. Peers own & maintian their own internal
  state. Peers maintain a replica of the relevant subset of the world state.

  A Peer's current state is represented as a nested object of recursive substates (ie. a Mapping). Peer State must implement a
  JSON SeDer Interface. We'll call this the `state object`.

  As events modifying peer state occur, each `state operation` is appended to a `state log`. The `state log` when
  evaluated (ie. collapsed), produces the current `state object`. As a runtime optimization, the log is incrementally
  collapsed thereby maintaining a cache of the current state.

  When a Peer requires the substate of a neighboring peer (such as when a capability procedure applies onto another peer)
  then the originating peer must subscribe for the subset of neighboring peer state. The Message Broker will then replicate
  such state.

  """

  def log(self) -> state_log_t:
    """Get an immutable view of the state log"""
    ...

  def push(self, op: op_t) -> None:
    """Push a State Operation onto the HEAD of the State Log"""
    ...
    
  def collapse(self) -> Mapping:
    """Collapse the State Log into the current state"""
    ...

class AsyncMutexProto(Protocol):
  """An Asynchronous Mutual Exclusion Protocol for a resource"""

  async def lock(self):
    """Lock the Clock"""
    raise NotImplementedError

  async def unlock(self):
    """Release the lock"""
    raise NotImplementedError

  @asynccontextmanager
  async def mutex(self) -> AsyncGenerator[None, None, None]:
    """Async Context Interface to hold the clock's lock"""
    raise NotImplementedError

class LogicalClockProto(Protocol):
  """A Logical Clock used to determine causal relationships in a distributed system"""

  async def increment(self, n: int = 1):
    """Increments the clock's counter by a specific amount."""
    raise NotImplementedError

  async def read(self) -> int:
    """Get the current value to the Logical Clock."""
    raise NotImplementedError
  
class EventQueueProto(Protocol):
  """A Queueing Protocol for Events in a distributed system."""

  async def peek(self, idx: int = 0) -> q_item_t:
    """Peek at an event on the queue; by default the head of the queue. No garuntees this value remains consistent accross multiple calls."""
    raise NotImplementedError

  async def push(self, item: q_item_t):
    """Push an event onto the queue"""
    raise NotImplementedError
  
  async def pop(self) -> q_item_t:
    """Pop an event  from the queue"""
    raise NotImplementedError
  
  def size(self) -> int:
    """The current number of events in the Queue"""
    raise NotImplementedError

class RecvProto(Protocol):
  """The Protocol for recieveing events on a declared set of subscription"""

  async def recv(self) -> tuple[topic_t, event_t]:
    """Recieve the next Event on the queue & it's corresponding topic, blocking until an event arrives. Increments the Logical Clock"""
    raise NotImplementedError

class SendProto(Protocol):
  """The Protocol for publishing an event"""

  async def send(self, topic: topic_t, event: event_t):
    """Publish an Event onto the queue, blocking until the event can be pushed. Increments the Logical Clock"""
    raise NotImplementedError

### Protocol TypeHints
class send_queue_t(EventQueueProto, SendProto): ...
class recv_queue_t(EventQueueProto, RecvProto): ...
