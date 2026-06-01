## Context

The `AnkerSolixSelect` entities representing `ac_outlet_timer` and `dc_12v_port1_timer` convert the physical device's remaining seconds (e.g., 597 seconds) to rounded options (e.g., `"10m"`) for display in Home Assistant. When Home Assistant components or external integrations synchronise states, they often trigger a redundant write command (`select.select_option`) with the current option string (e.g. `"10m"`). This causes a BLE control packet containing `600` seconds to be sent back to the unit, resetting the timer. 

Simultaneously, the codebase documentation has evolved, leaving test setup instructions in `README.md` redundant with `tests/README.md`, while `agent-guidelines.md` lists an outdated file structure, and `README.md` contains an unprofessional snarky warning quote.

## Goals / Non-Goals

**Goals:**
* Short-circuit redundant write updates in `select.py` if the requested option already matches the current rounded representation.
* Ensure the physical countdown timer can make continuous progress without resetting every 5 minutes.
* Refactor and polish `README.md`, `tests/README.md`, and `agent-guidelines.md` to remove outdated directory layouts and redundant testing setups, and present warnings professionally.

**Non-Goals:**
* Modifying the unencrypted command structures or GATT UUID definitions.
* Rewriting the Bleak connection or update loop inside `coordinator.py`.

## Decisions

### Decision 1: Short-Circuit Redundant Writes in select.py
* **Rationale**: By adding `if option == self.current_option:` inside `async_select_option`, we immediately return for matching states. This halts feedback loops from Home Assistant UI updates, state restorations, or external voice assistant syncs.
* **Alternatives Considered**: 
  * *Stateless memory cache of configured timer values*: This would track the originally configured duration in an entity property. However, this is complex to manage, does not persist across Home Assistant restarts, and fails to handle timer changes made outside Home Assistant (e.g., via the physical button or Anker app). The chosen rounding comparison is simple, stateless, and robust.

### Decision 2: Consolidate Testing Setup under `tests/README.md`
* **Rationale**: Moving the standalone testing CLI setup instructions out of the landing `README.md` avoids duplication, prevents documentation drift, and keeps the root landing page highly focused on end-user setup.
* **Alternatives Considered**: 
  * *Maintain docs in both locations*: Leads to inevitable divergence and outdated commands as utility scripts are added or modified.

## Risks / Trade-offs

* **[Risk]**: A user who wishes to reset an active timer from 595 seconds back to exactly 600 seconds by clicking the same `"10m"` dropdown item again will have their action ignored.
* **[Mitigation]**: The user can reset or extend the timer by briefly choosing another value (or `"Disabled"`) and then selecting `"10m"` again. This is a highly acceptable trade-off to solve the severe automatic resetting bug.
