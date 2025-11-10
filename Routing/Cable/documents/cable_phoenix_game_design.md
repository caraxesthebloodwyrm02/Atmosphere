# Cable & Phoenix: Game Design Document (Roguelike + Dual Campaign)

## Core Concept
A roguelike action-strategy game built around **timeline loops**. Each run represents a different timeline. The player alternates between **Cable** and a **Phoenix Host**. Progress across runs unlocks new abilities, narrative layers, and global system upgrades.

## Game Identity
- **Genre:** Roguelike Timeline Progression
- **Core Loop:** Attempt → Learn → Evolve → Repeat
- **Primary Theme:** Power has a cost. Every ability consumes stability.

## Dual Play Structure
The game switches perspective:

1. **Cable Runs** (Tactical Action)
   - Limited resources
   - Virus is constantly draining power
   - Objective: Stabilize timeline enough to reach Phoenix Zone

2. **Phoenix Runs** (High-Intensity Power Expression)
   - Near-limitless power
   - But stability decays with every action
   - Objective: Rebuild, renew, or reshape existence

The alternation creates meaningful contrast:
- Cable runs teach **discipline and optimization**
- Phoenix runs teach **self-restraint while being overwhelming**

## Shared Progression Across Runs
Progress persists through:
- **Memory Shards** (Narrative unlocking)
- **Genetic Resonance Upgrades** (Shared skill tree between Cable & Phoenix)
- **Hope Signals** (Metacurrency for unlocking late-game forms)

## Cable Gameplay
- **Primary Loop:** Survive the timeline while keeping the T-O Virus contained.
- **Key Mechanic:** Every ability drains *Control* (mental processing resource).

### Cable Stats
- **Health:** Physical survival
- **Control:** Limits telekinesis/telepathy usage
- **Viral Pressure:** Rising threat; spikes on mistakes

### Cable Playstyle
- Close Quarter + Mid-Range tactical combat
- Environmental manipulation using telekinesis
- Moment-to-moment decision: Spend power to survive now or save power to stabilize later

### Cable Failure Condition
If **Control** hits zero → **Virus Overrun** → Cable becomes a boss variant in future runs.

## Phoenix Gameplay
- **Primary Loop:** Reshape worlds, but avoid collapse into Dark Phoenix.

### Phoenix Stats
- **Stability:** Governs how long the host can maintain coherence
- **Flare:** High-power burst resource

### Phoenix Playstyle
- Reality-warping abilities
- Creative destruction
- You are not trying to survive. You are trying to **manage inevitability**.

### Phoenix Failure Condition
If **Stability** hits zero → **Dark Phoenix Break** → Universe resets a timeline prematurely.

## Hope Summers (Meta-System)
Hope is not playable. She is the **system reward function**.
- Every stabilized timeline produces **Hope Signals**.
- These unlock permanent upgrades in the shared genetic tech tree.

Hope is the **final win state**, requiring enough stable timelines.

## World Structure
Every run consists of:
1. **Distorted Earth Zone** (Cable)
2. **Phoenix Expanse Zone** (Phoenix Host)
3. **Nexus Chamber** (Choice-based timeline resolution)

## Run-Level Strategy
The player balances:
- Short-term survival (Cable)
- Long-term existential shaping (Phoenix)

Each run subtly shifts the next starting conditions.

## Endgame
The goal is to create a timeline where:
- Cable stabilizes the virus permanently
- Phoenix stabilizes identity and power
- Hope awakens fully

The final state is a single, unified timeline where **both power and self remain intact**.


## System Architecture Overview (Corporate UE-Style)
```
+-----------------------------------------------------------+
|                     META SYSTEM LAYER                     |
|                 (HOPE SUMMERS: PERSISTENCE)               |
|  Saves progression, unlocks genetic skill tree, updates   |
|        global parameters affecting all future runs.       |
+---------------------------+-------------------------------+
                            |
                            v
+-----------------------------------------------------------+
|                 ROGUELIKE TIMELINE EXECUTION              |
| Each run = one timeline. Outcomes feed back into Meta.    |
+-------------+-----------------------------+---------------+
              |                             |
              v                             v
+---------------------------+    +---------------------------+
|      CABLE RUNTIME        |    |     PHOENIX RUNTIME       |
| (Resource-Constrained)    |    | (Power-Unbounded)         |
| - Control Meter           |    | - Stability Meter         |
| - Virus Pressure          |    | - Flare / Burst Output    |
| - Tactical Combat         |    | - Reality Manipulation     |
+---------------------------+    +---------------------------+
              |                             |
              +-------------+---------------+
                            |
                            v
+-----------------------------------------------------------+
|                     TIMELINE RESOLUTION NODE              |
| Player chooses: Preserve / Reset / Mutate the timeline.   |
+-----------------------------------------------------------+
```

## One-Page Gameplay Cheat Sheet

**Goal:** Create a stable timeline where Cable survives and the Phoenix remains controlled.

### Cable Loop (Survival + Efficiency)
- You start weakened.
- Every ability **increases Virus Pressure**.
- You must choose when to use power or conserve it.
- **If Pressure maxes out → Cable becomes a future boss.**

**Win as Cable:** Enter a Phoenix Zone with Control remaining.

### Phoenix Loop (Power + Restraint)
- You start overwhelmingly strong.
- Every power causes **Stability Decay**.
- Your challenge is emotional restraint, not strength.
- **If Stability hits zero → Dark Phoenix wipes the run.**

**Win as Phoenix:** Reshape timeline without collapse.

### Shared Progression
- Runs give **Hope Signals**.
- Hope Signals unlock **Genetic Resonance Tree** (permanent upgrades).
- Cable & Phoenix both scale off the same tree differently.

---

## Lore-Mechanic Continuity Map

| Lore Concept | Game Mechanic | Gameplay Meaning |
|---|---|---|
| Summers-Grey Genome | Shared Skill Tree | Both characters evolve together |
| Techno-Organic Virus | Background CPU drain | Power is always a tradeoff |
| Phoenix Cosmic Power | Unlimited power w/ stability loss | Power must be earned by discipline |
| Hope Summers | Meta progression currency store | The future gets better only if you survive long enough |
| Timeline Loops | Roguelike run cycles | Failure is learning, not loss |

---

## Final Vision Statement
**Every run is a negotiation between strength and consequence.**
