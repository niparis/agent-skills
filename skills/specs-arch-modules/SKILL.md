---
name: specs-arch-modules
description: Project Documentation
disable-model-invocation: true
---

This document describes how our technical documentation should be organised


I will first introduce all files very briefly, and then give a deeper understanding of when to use eeach of them.

Your goal is to keep all architecture discussion and documents in sync with that organiation:
- whenever new information is added by the engineer, add them to the appropriate file
- if the engineer invokes this skill, you should read all the files as below and verify that each data point is the right file

## Overall


docs/
    product/
        vision.md                   
            - overal product vision. not features, not specs. 
            - As invariant as possible
            - includes non goals (what the product IS NOT)
    architecture/
        system-functional.md
            -  main architecture decisions made for the project
            - includes overall system context, functional architecture, runtime architecture, data architecture, and optionally integration and deployment
        agent-design.md 
            - OPTIONAL : only if the code base includes some agents
            - agents, skills, policies, memory, evaluation
    ADR/
        001-abc-xyz.md          >> why and how do we perform changes
    visual/
        abc.html                >> visual representation of the architecture, produced by the
                                   architecture-drilldowns skill. This is where component
                                   ownership and the process/library/store split are documented -
                                   as maps, not as prose. See "Components" below.
    specs/                      >> here OR in a tracker (usually described in AGENTS.md or architecture.md)

## Product 

Owns why the product exists, user, outcomes, enduring product principles/boundaries

### Vision

```markdown
   # Product Vision — <product>

   ## Purpose

   <!-- One sentence: what change does this product create, for whom? -->

   ## Audience

   <!-- Primary users and the context in which they use the product. -->

   ## Problem

   <!-- The enduring problem, independent of a particular solution. -->

   ## Desired outcomes

   <!-- Observable user or business outcomes, not features. -->

   - <outcome>
   - <outcome>

   ## Product principles

   <!-- Durable trade-offs. Write “prefer X over Y because Z.” -->

   - **<principle>:** <trade-off and reason>

   ## Success measures

   <!-- Measures that indicate value. Avoid implementation-health metrics. -->

   | Measure | Desired direction |
   |---|---|
   | <measure> | <increase/decrease/threshold> |

   ## Product boundaries

   ### The product does

   - <responsibility>

   ### The product does not

   - <explicit non-goal>

   ## Long-term direction

   <!-- Capabilities or qualities expected beyond the current release.
        Do not turn this into a feature backlog. -->

   ## Linked product decisions

   <!-- Issues or ADRs still requiring resolution. Remove if empty. -->

   - <link>
 ```



## Architecture

### System-Functional

Describes what the system does and how its major parts collaborate: functional architecture, logical boundaries, authority, state ownership, major flows, and runtime/deployment shape. It should be understandable without reading the source code.

Template

```
# System Architecture

## System context
What exists around the system?
Who are the external actors and systems, and where is the system boundary?

## Functional architecture
What capabilities exist?
What is the end-to-end behavior from input to outcome?
How are responsibilities divided between the user, the product, and external systems?
What cross-cutting behavioral policies apply across workflows?
How do major workflows behave, including failure, escalation, and human intervention?
Who owns key decisions and state?

## Runtime architecture
What executes what?
What are the main processes/agents/services?
How do control, supervision, concurrency, and lifecycle work?

## Data architecture
What are the main data stores and flows?
Which system or module is authoritative for each durable fact?

## Integration architecture
What external systems exist?
What role does each integration play in the system?

## Deployment architecture
Where does everything run?
What are the important deployment and trust boundaries?
```

## Components

**There is no components-interfaces.md.** We tried it and deleted it.

A markdown file with one Responsibility / Does not own / Interface / Dependencies / Patterns
block per component fails for one reason: it applies the same template, at the same altitude,
to things that are not the same kind of thing. A daemon, a shared library, a database table
and a four-line wrapper around a binary all get identical headings and roughly thirty lines
each, so they read as peers. A reader then cannot tell which ones run, which ones are code
inside something else, and which ones are not code at all - and they ask exactly those
questions, one after another, because the document caused them.

Component ownership and the runtime split are documented visually instead, by the
`architecture-drilldowns` skill, in `docs/visual/`:

| Page | Answers |
|---|---|
| `component-map.html` | Which components exist, what each owns, what it is prevented from owning, what travels between them |
| `process-map.html` | What has a PID, what is only linked into something that does, what crosses a process boundary |

The process map carries the altitude rule the prose could not: a box either runs or it does
not, and a box drawn inside another box is code in that process rather than a peer of it.

Whatever is genuinely normative - ordering, invariants, contracts, exact operations - belongs
in `docs/specs/`, not in a component document. That is where it survived when
components-interfaces.md was deleted.


## ADR


Structure

```
   # NNN: Title

   ## Status
   ## Context
   ## Decision
   ## Alternatives considered
   ## Consequences
```


