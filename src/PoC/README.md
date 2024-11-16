# Game Engine PoC

## Run the GameEngine

Let's think it through:

### What does the game engine do?

The game engine, is a distributed system (as defined my Lamport) such that every Lamport process in the engine contributes to the overall world state. The world is defined as the entities implemented by the engine's user. The design of the game engine is predicated on distributed systems theory, which implies:

* Implementation is inherently concurrent. Each entity is independently simulated requiring message passing to replicate state. Multiple `game engine instances` cooperate to provide a `logical game engine`; these instances are OS Processes or Threads running on one computer or multiple networked computers.
* There is a hierarchy of communication between Entities in the engine determined by their execution environment:
  * Entities sharing a logical slice of the Operating System ("local") can rely on OS synchronization primitives to communicate.
  * Entities logically isolated from each other, regardless is they are colocated on the same host or are distributed accross many, ("remote") must cooperatively communicate.
  * In practice, the Message Broker will provide a singular protocol & interface for inter-entity cooperative communication. The Message Broker then implements the various backends providing the local & remote functionality.

The `logical game engine` holds the primary goals to:

* Simulate the world
* Uphold world causality 

While the "game engine instance" holds the primary goals to:

* Maintain Entity State
* Distribute Event Messages
* Manage `Causality Clocks`
* Provide integrations for external systems (ex. a graphics engine)

### What does it mean to "run" the game engine?

Running the `logical game engine` involves running the union set of all `game engine instances` declared.

Running the `game engine instance` starts by executing the game engine process (herein instance). The Instance itself is composed of multiple components:

* The Game Engine Manager, managing the instance's participation in the `logical game engine' (a distributed system)
* The Message Broker, managing the distribution of events between entities in the `logical game engine'.
* The Entity Controller, managing the control loop lifecycle for each entity instance.
* The Entity Control Loop, managing the user implemented `capabilities` & entity state

### How does an `Entity` participate in the world?

First, we explicitly state that `Entities`, as implemented by the user, define the world. The features & functionality that users implement into their `entities` provide the features & functionality of the world. For example, if the user wants for some dimensional space in which objects move, then the user would implement an `entity` providing some Mathematical space & the ability to track position within that space. The game engine is merely a vessel to simulate the user's implementation.

So to participate in the concurrently simulated world, each `entity` must inform the world of it's events. Events are a byproduct of `capabilities`. A `Capability` implements the procedures providing the features & functionality as defined by the user. These procedures generate events through read & write interaction of internal & external state. A change in entity state is propogated to all other `entities` requiring it. Such state dependency is determined by the implemented `capabilities`. For a trite example, a "Move" `capability` implemented by a "Player" `Entity` would require exchanging of state between the "player" & the "space" (in which movement occured) as to determine if the destination location is occupied.

### What is a Capability? How is a Capability Implemented? How do multiple Entities implement a capability?

In context of the game engine design, a Capability is a set of procedures that either A) act on the world or B) observe the world. In context of the game engine source code, a Capability is a Protocol that defines a well established functional interface that entities can implement. By extension, capabilities are a form of structural typing: all entities implementing a capability share the same structure.

Capabilities rely on all implementing entities providing common state. For example, a "Movement" capability might expect an entity to track a "position" state; on applying the capability (ie. the entity moves) then the entity's "position" state would be mutated to reflect the transformation.

It is implied then that any entity not implementing a capability's protocol or expected state is not of a strucutral type that capability describes.

### How is an entity's state structured?

An entity's state comprises A) any conditions and data necessary for the entity's intrinsic implementation & B) all conditions and data necessary for any implemented capability protocol. In implementation, entity state is a nested mapping of key-value pairs where keys are strings & values are some data type implementing the common SeDer Protocol for un/marshaling from/to the wire. This mapping is called the `Entity State Object`. This State Object follows a loose schema where the only top level keys allowed are `Internal` & `Capability` each being nested objects themselves. The `Internal` object only holds state intrinsic to the entity as discussed above. The `Capability` object further constrains it's top level keys to names of registered capabilities whose values are nested objects of that capability's expected state.

The below example demonstrates this schema:

```yaml
EntityAStateObject:
  Internal:
    FooBar: ...
  Capability:
    CapA:
      Foo: ...
    CapB:
      Bar: ...
```

### How do we handle common state?

Let's consider a scenario where there is some common state between entities:

> The user wants to implement an engine where two players move in some 3D Space consisting of a discrete grid of points (ie. [x, y, z]). A single point in 3D space may accomodate only a single entity. Likewise, a player may only occupy a single point in this 3D space.

First, let's establish our entities & capabilities:

```python
class Player(Entity): ...
class Space3D(Entity): ...
class Kinematics(Capability):
  def move(*args, **kwargs): ...
```

As declared above, `Player` & `Space3D` implement our Players & 3D Space respectively. Likewise `Kinematics` becomes the protocol providing for Movement of players in the 3D space.

Next, let's consider how state is managed in this system. Informally, we have established that:

* `Space3D` provides "Points in Space" that players can occupy.
* `Players` have "Positions" in 3D Space.

Therefore, we can say the common state is "Player Positioning being a point in 3D Space":

```python
class Point3D(TypedDict):
  x: int
  y: int
  z: int
```

Let's now consider various ways we can implement this common state:

1. Players & 3DSpace both track state position:

   Players maintain their current positions as 3D Points. The 3D Space maintains a record of player positions. `Player` & the `Space3D` implement the `Kinematics` Protocol. The Player's protocol calls into the Space3D's protocol w/ their desired transformation; Space3D informs the Player the movement is valid (ie. Point in space is unoccupied) &, if so, the player mutates it state informing Space3D of its new location. It should be noted that each exchange of information is an "Event" in terms of distributed computing.

2. Only 3DSpace track position State:

   3D Space maintains an object of occupied 3D Grid points. Players maintain no positioning state.  `Player` & the `Space3D` implement the `Kinematics` Protocol. The Player's protocol calls into the Space3D Protocol requesting a transformation of location; the Space3D protocol will run the procedures to compute & validate the transformation returning if the movement was valid or not. For a player to later access its current position, it must call into the Space3D Protocol to request its position.

3. Only Players track position state:

   Players maintain their positions. Space3D retains no positional state. When a Player's protocol requests a transformation, the Space3D protocol must request from every participating player their current position before it can compute & validate the transformation; if valid, Space3D returns the result & the player mutates it's state.

Let's consider these implementations from the context of an external player (herein `Player 2`) entity currently positioned in the point the original player intends to move into:

1. Players & 3DSpace both track state position:

   Assuming the state of `Player 2` & `Space3D` are synced, then `Player 2` is never made aware of `Player 1's` attempt to move into it's position b/c `Space3D` informs `Player 1` the desired transformation is invalid.

2. Only 3DSpace track position State:

   Identical to Scenario 1

3. Only Players track position state: 

   In this scenario, `Player 2` receives a request from `3DSpace` for its current position.

Let's reframe our mental model by first asking a question: In a Lamport Distributed System, how does the "flow of causality" play into the ordering of events.

To recap:

- A → B if Clock(A) < Clock(B) where → is not commutative
- If A -/> B & B -/> A then A & B are concurrent
- Sending & Receiving a Message are Events in the System which implies A → B when A is sending a message & B is receiving that message.

With that in mind, Player movement comprises many events:

- Send/Recv of Transformation Intent
- Mutation of State

We break down the scenario by entity, ordering each entity's event order

- Player 1:
  - Send Message: transformation intent
  - Recv Mssage: transformation success
- Player 2
  - Send Message: transformation intent
  - Recv Mssage: transformation success
- 3DSpace
  - Recv Message: P2 transformation
  - Recv Message: P1 transformation
  - Internal: Evaluate P2 transformation
  - Send Message: Inform P2 transformation success
  - Internal: Evaluate P1 transformation
  - Send Message: Inform P1 transformation success

However if the causal ordering of the transformation intent messages are reversed:

- Player 1:
  - Send Message: transformation intent (to P2's current position)
  - Recv Mssage: transformation failed (P2 already in that position)
- Player 2
  - Send Message: transformation intent (to elsewhere)
  - Recv Mssage: transformation success (Position empty)
- 3DSpace
  - Recv Message: P1 transformation
  - Recv Message: P2 transformation
  - Internal: Evaluate P1 transformation
  - Send Message: Inform P1 transformation failed
  - Internal: Evaluate P2 transformation
  - Send Message: Inform P2 transformation success

This implies that the causal ordering of messages (ie. "Flow of causality") ultimately defines the "world state". This has implications on how we implement our systems. Let's again consider the common state scenarios. First, we should understand the flow of causality in each. Next, we should glean the complexity of implementation. Finally, we should seek to simplify our design:

1. Players & 3DSpace both track state position:

   Both Players & 3DSpace share ownership of state thereby creating a need for replication & consensus on state related transactions. All message passing between Player & 3DSpace are events: Player informing of intent; 3DSpace informing of validity; Player informing 3DSpace of mutated state. If multiple players are attempting to move into the same position, then player ownership of position state creates a "causal race condition" since Player state mutation happens asynchronously of transformation evaluation. This will assumedly cause (more) frequent causal violations that would need fixing.

2. Only 3DSpace tracks position State:

   3DSpace owns state thereby centralizing state management. Any attempt to mutate that state is strictly tied to the "flow of causality" since players must exchange messages w/ 3DSpace to A) retrieve state & B) mutate state. The scope of causal violations reduce to just that of a player.

3. Only Players track position state:

   Players own state thereby distributing state management. Attempts to mutate state, while evaluated by 3DSpace, ultimately requires players to communicate state. The act of observing & mutating state is propagated through the "world" via message passing; this "collapses" causality as messages propogate. This concept of replication of entity-owned state better reflects physical systems of information propagation.

### How do Protocols "call into" each other

Capability protocols implement procedures which act on or observe the world; events. This "flow of causality" is implemented through message passing between entities. The ingress & egress point of messages in a system diagram can be thought of as the "protocol". So the question "how do protocols call into each other?" is really a question of "how is message passing implemented?". We ask this question in the context of the developer as they implement entities & capabilities.

Let's consider a few approaches.

1. Entity Protocol Function Call:

   Each Entity Class implements the member functions as defined by the protocol. To invoke a capability, the member function is called. Assuming a dependency exists on a peer entity's capability, then the assumption is the former entity calls the peer entity's member function. However, in this distributed system, events are propagated as messages. Calling the peer entity's member function would not directly invoke the peer's capability, nor would it inject any state data. Instead this member function would need to handle the necessary message passing to send a message & receive a response. This then opens a line of questioning around how such messages are differentiated from unsolicited messages.

2. Message Handling:

   Again, each Entity Class implements the member functions as defined by the protocol. To invoke a capability, the member function is called. However, instead of the originating peer calling the member function of a neighboring peer, it publishes a Remote Procedure Call (RPC) Message addressed to that neighbor peer awaiting for a RPC reply message from the neighboring peer. It then proceeds w/ evaluation of the protocol.

### What functionality does the Message Broker provide?

Processes in a distributed system exchange messages, there are a few ways to implement this:

1. Processes themselves manage the tx/rx of messages between peers.
2. A Message Broker handles tx/rx of messages between peers.

In our game engine, we use a Message Broker to separate the implementation details of message passing & entity behavior so as to reduce development burden on the user of the game engine.

We must then design & implement a Message Broker. First we identify the design goals of the Message Broker:

- Provide Topics allowing for logical isolation of message streams.
- Exchange Messages between Entities.
- Allow for fine-grained delivery of messages between entities.
- Handle inter-process & inter-computer message passing.
- (Maybe?) Synchronization of clocks within the distributed system.

Let's articulate each design goal.

- **Exchange Messages between Entities**

  To participate in the World, entities must act on & observe the world. They do this through writing or querying state from other entities. This communication is cooperative, both entities must be programmed to understand the messages sent to them & to act accordingly. Therefore:

  - Messages must include some classification (ie. kind) that denotes its semantic content.
  - Entities must register those kinds they recognize; the broker should filter out any message to & from an entity not registered.

- **Provide Topics allowing for logical isolation of message streams.**

  As the distributed system grows, so too does the complexity as new capabilities & messages kinds are introduced & the number of entities balloons. To handle scaling, entities should logically isolate themselves into partitions organized by semantic relevance. Topics are hierarchical namespaces managed by the broker that must be provisioned by entities:

  - Entities must first register topics to make available.
  - Entities must then submit publishments or subscriptions to an available topic.

  Managing topics should occur at initialization & teardown of an entity; the developer should avoid leveraging topics as a tool to "relocate" the entity based on entity behavior they have implemented. Treat topics as static & expensive conditions as they must be propagated between game engine instances.

- **Allow for fine-grained delivery of messages between entities.**

  Entities should also have fine grained abilities on the delivery destination of messages. In computing terms, entities must be able to unicast, multicast & broadcast messages. Let's consider implementation strategies:

  - Messages are addressed to some destination; a single entity for unicast, a group of entities for multicast, or "all" for broadcast. Destination Addresses are sets of entity ids.
  - A second Topic System exists that provides a hierarchical tree of peers in the system:

    - `/Peer/ID`:  The complete list of entities by id. This uniquely identifies each peer in the system.
    - `/Group/GROUP_ALIAS[/SUBGROUP_ALIAS]/PEER_ID`: Lists of active multicast groups. Groups are themselves hierarchical allowing for subgroups.
    - `/Broadcast`: Broadcasts a message to all Peers.

- **Handle inter-process & inter-computer message passing.**

  The `logical game engine` consists of multiple concurrently executing game engine instances, either colocated on the same  OS or networked together. The Message Broker must therefore implement IPC & Networking communications to exchange messages between entities owned by other game engine instances. Entities are owned by individual engine instances (at least for now) so Brokers are responsible for routing of entity messages between one another. Many Message Brokers together form the communication network for the distributed system.

- **Synchronization of clocks within the distributed system.**
  To ensure causality, brokers must maintain synchronization of their (Lamport) clocks.

  > This needs to be expanded on

### How does a Message Broker match Hierarchical Topics?

Topics in the message broker are hierarchical, they form a tree. Message Publishments must be destined for a single, particular topic but subscriptions match the entire subtree rooted at the given topic.

Let's consider multiple topics `/T/A/1` , `/T/A/2`, `/T/B/3` & `/X/Y/Z` ; each actively being published to by various entities:

- Subscribing to `/T/A/1` will yield messages destined only for that Topic.
- Subscribing to `/T/A` will yield messages destined for all children; namely `/T/A/1` & `/T/A/2`.
- Subscribing to `/T` will yield messages destined for all children; namely `/T/A/1`, `/T/A/2` & `/T/B/3`.
- Subscribing to `/` (ie. root) will yield all messages destined for all topics; namely `/T/A/1` , `/T/A/2`, `/T/B/3` & `/X/Y/Z` .

Explicitly said, the Pub/Sub messaging pattern when implementing Hierarchical Topics is asymmetric in design:

- Publishment is a one to one relationship: Messages can be published to only one Topic.
- Subscription is a one to many relationship: One Topic can source many messages (ie. The specified topic & all children)

If Topics were flat instead of hierarchical, then the pub/sub pattern would be symmetric.

With asymmetry identified, should the design afford optionality in emulating the symmetric design patterns during subscription? With respect to the above example, when subscribing to `/T` in "flat" mode, then an error should be raised as no single entity is actively publishing to `/T`, only children thereof.

Does this imply implicit types of topics; namespaces & active objects? Namespaces being logical containers of other namespaces & active objects? This further implies that active topics are registered w/ the broker & the broker assumes management of the topic namespace hierarchy. Likewise, Entities may not publish to topic namespaces but only to active objects. Therefore, in the implementation of subscriptions, entities subscribing to topic namespaces are really bulk subscribing to all active objects contained within that namespace's set.

Should we then allow namespaces to be promoted to active objects? Let's consider this scenario:

- An existing namespace `/T` holds a set of active objects (irrespective if those objects are contained within nested namespaces).
- An entity subscribes to the namespace `/T`; in effect this is a bulk registration to all contained active objects.
- The namespace `/T` is promoted to an active object.
- The entity again subscribes to, the now active object, `/T`. Multiple scenarios can play out dependent on implemented functionality:
  - If namespace functionality is retained...
    - Subscribing to `/T` should again bulk register all contained active objects, this time including `/T` itself.
  - If namespace functionality is not retained...
    - Then it is an illegal program state for there to exist child active objects. Either the children must be ejected or promoting the namespace must raise an error in the first place.
      - Ejection of children causes cascading effects, any publishers on the ejected children would being to fail as they try to send messages to a now defunct topic. To mitigate, topics could instead be moved but that would then require the publishing entities to handle this state change. This likely has far reaching implications which in effect breaks the fundamental design of Topics as semantic partitions.

I would assert, based on these considerations, that promoting topics to active objects cause no major problems. It does shift the mental model for topics then:

1. Topics may provide logical partitions for message streams.
2. Topics provide hierarchical groups of message streams.
3. These functionalities are not mutually exclusive.

To reflect this shift in mental model, I'll introduce new terms:

- `Topic Partition` identifying a singular stream of messages.
- `Topic Trees` providing hierarchical grouping of `Topic Partitions`
- `Topic Path` referring to the raw path string identifying a partition or tree.

I'll also adjust my earlier statements to reflect the new mental model:

- `Publishments` form one to one relationships with `Partitions`.

- `Subscriptions` form one to one relationships with `Partitions`.
  - Bulk Subscriptions can be made by resolving a `Topic Tree` to it's set of `Topic Partitions`.
  - You cannot subscribe to a `Topic Tree` itself.

As such, `Topic`, used plainly, is a misnomer when referring to implementation behavior.

### Is Topic Management a unique functionality?

Plainly put, yes. The Message Broker implements functionality concerned with the passing of messages between entities. Having the broker also implement functionality of managing topics overloads the message broker & further couples broker functionality to the nature of topics. The Message broker should be agnostic to identification & grouping of message streams, instead relying on an external dependency to inject that functionality as needed. Further this allows the re-use of the Topic design pattern to be re-used across other functionalities, such as in unicast/multicast/broadcasting as mentioned above in the Broker design.

I assert Topic Management functionality provides the following features:

- `Topic Registry`: Managing registration lifecycle of Topic Partitions.
- Management of `Topic Trees` including resolution of `Partition` sets belonging to a specific tree.
- `Topic Path` manipulation, searching, matching, etc...

Correlation of identities to topics would be implemented by the message broker:

- Subscriptions & Publishments are tied to Entity Identities & are modified by runtime conditions (ie. Topic Partition must exist before a subscription or publishment can be made).

