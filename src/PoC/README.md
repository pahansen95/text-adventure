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

### What is the Vision of the PoC Game? What do I want to build?

To help guide my efforts in developing the GameEngine, I need to articulate a simple vision for a PoC Game. Let's base the PoC's Vision on the Vision of the final game. This means we should scope down the vision to some minimal, singular game loop. To recap, the vision of the final game is a sprawling text based adventure RPG whose world is simulated where NPCs are simulated through LLMs. Such a game would need to implement the following game features (non-exhaustive):

- NPCs: Some unique individual w/ a story & role; they are simulated using LLMs.
- Agents: Any other agent in the world not classified as an NPC; ie. Monsters, Pets, etc...
- The Environment: The physical space the game takes place in including any static objects like walls or mountains; entities would move around in this world.
- Game Fixtures: Items w/ no agency but that can be interacted with. Examples include consumables, materials or loot.
- World Events: Pre-Determined events that occur based on certain conditions like time or player level.
- Inventory: The ability to carry & store Game Fixtures.

So for our PoC let's narrow down a basic game feature/loop that A) requires use of all distributed system components (Message Broker, Control Loops, etc...), B) is relatively simple to implement & C) is player interactive. Here are my thoughts:

- There needs to be at least 2 seperate entities, 1 of which is the player. The player entity requires control loops to process both world events & engine events. The 2nd entity would need to process world events at a minimum.
- To keep things simple, a single player "action" should be implemented. This action, should cause some message propogation from the player to the 2nd entity. Ideally some response to the player entity should occur.

Here are a few ideas:

- Player Movement; Let the Player move their character within the boundary of the world:
  - Capture Control Input (ie. Movement)
  - Transform Player Position
  - Collision Detection
- NPC Interaction; Let the Player interact w/ an NPC (backed by an LLM):
  - Capture Control Input (ie. NPC Selection and Text Inputs)
  - Send/Recv Req/Resp
  - NPC "Memory"
- Player Movement & NPC Interaction:
  - See both requirements

Let's assume we do both & think through our design:

- What are our Entities?
  - Player: The Agent representing the Player.
  - NPC: An Agent the player interacts with.
  - 3DSpace: The space the player moves in
- What are our Capabilities?
  - Kinematics: The ability for entities to move within the 3DSpace including collision detection.
  - Interactivity: The ability for an Agent to be interacted with, in our case verbal communication.

### What is a controller, how is it designed & implemented?

First I will assert that a Controller is a piece of software that regulates the state of the (sub)system it's associated with. In our game engine there are multiple controllers that regulate multiple subsystems. Example Subsystems implementing a controller include, the Message Broker, Entities & the Engine Instance.

In a distributed system, the control loop processes system events & transitions state according to defined rules. For example, if a NPC Entity receives an interaction event from a player, the NPC's World Control Loop is responsible for transitioning the Entity into it's "interactive" state which would afford the Player Realtime interactivity.

With this model in mind, we need to consider how to design the controller. Let's think through the various responsibilities of the controller:

- Handling of external events & internal events.
- Reacting to the casual flow of events by transitioning process state.
- Management of Process State.
- Emitting Causal Events.

Based on these responsibilities, let's think through the components of the controller:

- Event Handler: Implementing functionality to send & receive causal events.
  - Interfaces with the Message Brokers to offload tx/rx implementation
- State Manager: Implementing CRUD functionality for process state.
  - Interfaces with the Entity Resource Spec & Status
- State Transition Engine: Implementing functionality to transition the state of the process.
  - "State Transitions" are the "runtime logic" of the entity including...
    - World Semantics; ex. Respond accordingly to a world event
    - Engine Integrations; ex. Injecting a movement event based on keyboard input.
  - State transitions aren't atomic; they are composed of atomic "actions" chained together. Therefore a state transition can be cancelled in between atomic actions resulting in a partial state transition.

Let's dig into how to implement the state transition engine. Various strategies include:

- **Event Callbacks**

  When an event is received, it invokes an associated functional interface of the capability. In the example of "movement", the "kinematics" interface implemented by the entity would be invoked. Whether or not a callback is idempotent is up to the implementation: multiple movements should stack while multiple "interactive" requests should only apply once per "session". There is no "engine" that holistically orchestrates transition of state; transitions can be concurrently invoked by callbacks. The "engine" is implicit in the imperative statement, evaluations & conditions distributed across all of the entity's capability interfaces.

- **Behavior Trees**

  An Entity's capabilities are modeled as a hierarchical tree of behavior. The root nodes serves as the entry point to the capability & each node implements specific functionality associated w/ the capability. As events & conditions occur, the tree is walked adjusting entity behavior. For example, in a "movement" capability, let there be a root "idle" node sharing an edge w/ a "walk" node. When a transform event is received, the current index would transition from "idle" to "walk". After the transformation concludes, then the behavior tree completes & the state resets to the root node.

- **Petri Nets**

  A Directed Graph of Places & Transitions where places detail a possible substate & transitions encapsulate a particular capability. Tokens are associated w/ places to indicate the current substate of the system. On graph evaluation (triggered by some event for example), transitions are evaluated if they can be triggered (all input places have an associated token); if so the transition's input tokens are consumed, the capability is applied & tokens are set on the output places. In this model, a capability is broken down into atomic transactions which the controller incrementally evaluates. In this way, a capability can be partially applied if some event occurs that disrupts and/or redirects input tokens from the capability arc/path. This can also be used to determine concurrency deadlocks for an entity or to conduct advanced analysis of the implementation.

All things considered, the Petri net appears to be the preferred implementation strategy for the State Transition Engine based on A) it's provided functionality & B) it's seemingly straightforward ability to integrate incremental evaluation into a control loop.

Let us discuss how the controller implementation is formatted & organized:

- Every Entity Kind registers corresponding controllers; one for the world & one for the engine.
- Controllers are composed of multiple parts:
  - A Central Control Loop that continuously iterates
  - A Event Handler that integrates between the Message Broker & the Entity
  - A State Manager that provides causal state functionality.
  - A State Engine that implements the state transition & logic of an entity.
    - The Entity also associates and/or implements capabilities through functional interfaces. The State Engine orchestrates application of these capabilities.
- The Control loop manages scheduling & lifecycle of the controller's various subtasks. It walks through a predetermined set of steps.

### How does the State Transition Engine integrate w/ an Entity's capabilities?

To start our discussion, let's recall how we proposed capabilities are designed & implemented:

- Capabilities define functional protocols & common state which any participating entity must implement, thereby providing structural typing for capabilities.
- Capability State has ownership; either singular, shared or federated.
  - In singular ownership, a single entity owns all state & all other entities must request read/write operations against this entity in order to observe or act on this state. IE. The 3D Space fronts R/W Operations for all entity positions.
  - In shared ownership, the same state is replicated between entities. Before read/writes can occur, entities must reach a consensus on the current state version. IE. The Positions for each Entity are replicated between the respective Entity & the 3D Space; any R/W Operations on entity position requires consensus between the Entity & 3DSpace.
  - In federated ownership, the state is modeled as a set of individual substates each owned by discrete entities. These substates define that entity's specific condition of being in time. IE. Every entity capable of having a position in the 3D Space owns its own 3D Position; any R/W Operations on an Entity's Position requires the other entity requesting the operation against the owning Entity.
- Invoking a Capability Protocol requires message passing between entities (ie. Lamport Processes) thereby creating a casual dependency between discrete entities. The approach to invoking a remote entity's capability protocol is effectively asynchronous RPC irrespective of the stylistic programming interface provided to the developer (ie. Calling a class member vs constructing a RPC Message).

These fundamental design conditions imply that an entity, processing world events in synchronous order, can be fully blocked by another entity causing a potential world deadlock if all entities form a cyclical graph of blocking dependencies. It is therefore imperative that implementation of capabilities are A) fully asynchronous, B) decomposed into atomic unit operations & C) designed to cooperatively avoid cyclical blocking dependencies.

This leads us to discuss how to integrate entity capabilities & the state transition engine. Up till now we have largely avoided articulating specific implementation patterns for capabilities. It is here, now, that we manifest the implementation of capabilities.

Firstly, let us assert constraining conditions:

- The state transition engine invokes the capability's functional protocol. 
- It then leads that the individual members of the functional protocol are the originators of...
  - Remote Procedure Calls to external entities (ie. External Events).
  - Local Procedure Calls to the internal entity (ie. Internal Events).
  - State Manipulation of the internal entity.

Next, let us articulate what specifically is a capability protocol member:

- A Member is simply some callable software fragment such as a function or callable object.
- Member implementation occurs in multiple locations; namely...
  - The Protocol itself; ie. A shared or common Implementation
  - The Participating Entity; ie. An overridden or extended function
- Member implementation may occur at both at the protocol & at the participating entity; dependent on the needs & design of the capability.

Next, let us articulate how a member manipulates the internal state and/or generates internal events respective to the entity which called the member:

- When an entity calls the member, beyond passing the capability's expected arguments, it injects into the member the required dependencies of that member, such as the entity's state manipulation interface, the entity's messaging bus & any other interfaces necessary to invoke state changes.
- As the member evaluates its procedural logic, it hooks into the entity's interface as the mechanism by which to invoke change.
- Members may end up calling, through the entity, other members thereby creating dependencies between sibling members or members of other capabilities. These dependencies can be graphed & analyzed to determine the presence of certain concurrency pitfalls such as cyclical dependencies.

Through this approach, the Entity embodies a capability without the need to explicitly implement the capability. The entity may still, optionally, extend or override the capability interface.

Now let us articulate the mechanism by which the state transition engine originally invokes a capability:

- When the State transition engine evaluates its input conditions, if any conditions are met, then that transition is triggered.
- Triggered transitions are subsequently scheduled. These triggered transitions themselves invoke the members of the associated capability protocol.

Let us then articulate what is a state transition & a state "place":

- A state place is a specific named condition of being; ex. "idle" or "walking". When certain conditions are held, then it can be said that the (sub)state is in a certain place. Tokens indicate currently held places.
- A state transition describes a path that maps between two sets of places, an input set & an output set. If all places in the input set are held (ie. Have tokens), then the transition can be evaluated. Tokens are placed on the output set dependent on the evaluation.

This considered implies several statements...

- Capabilities not only describe a protocol & common state but also describe a set of places & transitions. The State network is therefore a superset of the place & transition sets of all participating capabilities.
- Evaluation of triggered transitions in the State Network is asynchronous of evaluation of transitions themselves. This is b/c transitions can call on other capability members which can adjust the distribution of tokens in the state network thereby triggering other transitions. In other words, transitions can be dependent on or cascade other transitions.

### How is a Capability Formally Implemented?

A Capability implements:

- State
  - The specific conditions of being at a specific moment in time.
  - Implemented as a Key-Value Registry.
- Protocol
  - The functional interface encapsulating the procedures implementing the semantics of the capability.
  - The callable members of the protocol are classified as intrinsic/internal or extrinsic/external.
    - Intrinsic/Internal members provide common implementation specific to that protocol's semantics.
    - Extrinsic/External members are entity specific implementation of the protocol's semantics.
  - Participating Entities must implement the extrinsic members of a capability; The intrinsic members call these as hooks. This allows entity implementations to inject semantic dependencies.
  - When calling Intrinsic members, any stateful conditions must be passed at runtime. Such an example would be the calling entity or the message handling interface for the entity.
- State Transition (sub)Graph
  - The set of Places & Transitions describing the sequencing, conditions & mapping of the protocol's procedures.

### How is the State Transition Engine Designed & Implemented?

The State Transition Engine design & architecture is based on the Petri Net. It consists of a set of named `conditions` & `transitions`. `Transitions` map between input & output `conditions`. During runtime, tokens are placed on input `conditions` that currently exist. When the network is evaluated, `transitions` are triggered contingent on all input conditions existing.

Let's explore this concept of modeling state & state transitions. To articulate our mental model we should start by answering some questions:

- What is state?
- What is implied by the phrase `state transition`?
- How do we model this?

First, let's scope ourselves to the cognitive realm of the Game Engine World composed of Entities.

Let's define state: A measurable "condition of being" for a discrete entity at a particular point in (causal) time; manifests as the explicitly declared data-structure owned by the entity which can be read from & written to.

A State transition can then be described as a mutation in state; ex. Entity's moving. State Mutability is constrained by the semantic rules governing behavior; ex. Two Entities implementing Kinematics can't occupy the same position in 3d Space. These rules are further predicated on pre-existing conditions; An entity cannot mutate its position without first having some intent to transform its orientation in 3D Space. The resultant of a state transition is another discrete state; if no mutation of state occurs then no transition occurred.

This implies, assuming a standard procedural programming model, that we first must evaluate if a state transition can occur. If the evaluation holds true then the state mutation is applied. In a distributed system, where we are concurrently simulating the world, this mutation evaluation is only valid if the underlying state preconditions & the initial state hold; if they change before applying the mutation then there exists a probability the transition violated causality & was thereby implausible.

Let us then consider an extreme scenario in which vast numbers of entities are simultaneously evaluating state transitions each somehow dependent on a subset of all other potential transitions; ex. 1 trillion entities moving within a finite, dense 3D Space. In this scenario, let us assert that:

- Just 1 entity mutating its state (ie. Position) invalidates at least 1 other peer entity's evaluation almost always.
- State Mutation is never instantaneous; evaluation always introduces some gap in time between intent to mutate & applied mutation.
  - It is this gap in time that causes conflicts in causality as 1 entity's state mutation could invalidate another entity's computed evaluation before it is able to mutate its state.

From the perspective of a developer implementing a "world" we can conjure up a few mental models to inform an implementation supporting this extreme scenario:

- We ensure no violations of causality occur through exhaustive control over the simulation; every mutation is evaluated sequentially thereby ensuring that every intent to mutate is predicated on the true state of the world. In this mental model, we effectively "freeze time" in the world simulation in order to evaluate a transition. For a "small" world, freezing time can still feel instantaneous for players since it can happen on timescales well below the threshold of human cognitive processing. However the player experience degrades for "large" worlds where the computational burden of simulation exceeds the subjective timescale of "smooth" gameplay. In either case, the world is simulated w/ 100% casual accuracy.
- We allow entities to concurrently & independently evaluate state transitions based on their "observable" world state, tolerating violations of causality to maximize throughput & scale of world simulation. In this approach, the quantity of causal violations is based on some probabilistic model. In the event of a detected violation, the offending entities would need to reconcile their state. A byproduct of this mental model is that inter-entity communication scales exponentially relative to population size, assuming that the main mode of communication is broadcasting. To manage scaling, we should instead use multicasting patterns where entity's proactively manage their group memberships.

As it relates to our design & implementation goals, the later mental model is preferred. But what implications does this have on our mental model of State & State Transitions?

- State has ownership as discussed in prior sections; the relevant data must be maintained.
- Transitions reliant on external state are predicated on a snapshot of observable conditions; refresh of the snapshot is triggered on some event.
- Entities must request state from peers in order to observe the world.
- State Mutation is an Event (in a distributed system) & should be published to interested parties.
- To manage issues introduced by scaling, the semantic model of a capability should incorporate the concept of microcosms; the effects of a transition should be scoped to only those entities most immediately affected as opposed to broadcasting to all entity's in the world. This could be implemented via Multicast Groups.

Let us loop back to our discussion on the implementation of the State Transition Graph & scrutinize the concepts of "places", "transitions" & "tokens":

- A transition is the process by which an entity's state is mutated.
- A place is some named condition mapping to a discrete substate configuration.
- A token indicates the existence of a place in a moment in time. Tokens therefore are sortable by (casual) time.
- Places are connected through transitions as mappings of Inputs to Outputs.
- Evaluation of the entire State Network is asynchronous.
- Applied transitions consume tokens immediately after a state mutation; this implies an evaluation occurs before the token is consumed.
- Placement & Consumption of tokens, which map to state mutation, are internal events that should trigger re/evaluation of the state graph. This implies that no modification of tokens results in no evaluation of the state graph.
- A failed evaluation of a transition implies no mutation & no consumption of tokens. Note that by failed evaluation, we imply the evaluation of the state transition resulted in an illegal state & is thereby rejected.

How does this then iterate our design & implementation of the State Network?

- ...
