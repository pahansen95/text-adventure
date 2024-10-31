# Text Adventure

A text driven adventure game that affords players the use of Natural Language as the "controller".

## Design & Theory

The player(s) interact with the `World` through natural language. An LLM maps player intent into the functional procedures provided by the `World Interface`. The game state is maintained through the `World State`.

The `World` is defined as the union set of all `Entities` each having A) `Capabilities` & B) `State`. The `World Interface` is therefore defined as the union set of all `Entity Capabilities`. Likewise, the `World State` is defined as the union set of all `Entity State`. A `Capability` defines some possible A) `Observation`, B) `Action` or C) `Reaction` an `Entity` is capable of. A `State` is some collection of data representing the current condition of the `Entity`.

The `World` is distributed, there is no concept of omnipotence *from within the boundary of the world*. Entities form `causal relationships` with one another in a concurrent manner; these relationships are propogated to neighboring peers. Any grouping of Entities whose `causal` graph is fully contained is called a `microcosm`. `Causal` events do not propogate beyond `microcosms`; `microcosms` are independent of each other.

Any singular programatic object that contributes to the Game `World` is an `Entity`. `Entities` are either active (`Agents`) or passive (`Fixtures`). `Entities` can apply actions to the `world`, recieve re/actions from the `world` & observe the `world`. What delineates an `Agent` from a `Fixture` is it's `Agency`, any `entity` with the intrinsic capability to take action is considered to have `Agency`. Likewise, any `Entity` that relies on external inputs has no `Agency` & is therefore a `Fixture`

When an Entity observes the `World`, the `World State` of the corresponding `microcosm` "collapses" & all `causal relationships` are resolved; in otherwords, within the scope of a `microcosm`, all state caches are replicated.
