## Context

Refining several elements of the custom component and release pipelines to prepare the F2000 HACS
integration for a robust stable launch:
1. Solving the stuck primary battery entity display.
2. Correcting the invalid MDI switch icon key.
3. Enabling major release triggering in CI.
4. Aligning repository and agent documentation with the correct directory tree.

## Goals / Non-Goals

**Goals:**
- Dynamically fall back the primary battery badge to `internal_pct` when no expansion battery is present.
- Allocate the standard, working `mdi:car-power-outlet` icon to the 12V Car Port Master switch.
- Cap the pre-generated select dropdown options for both AC and DC shutdown timers to 18 hours to prevent overflow.
- Update the Automated Release CI workflow to bump major versions if commit message contains `"major"`
  or `"breaking"`.
- Clean up obsolete directory structures in `agent-guidelines.md` and document the new timer sensors in
  `README.md`.

**Non-Goals:**
- Creating new battery calculation entities or overriding user-customized dashboard badges.

## Decisions

### Decision 1: Smart dynamic battery percent fallback
- **Options Considered**:
  - Option A: Re-key the primary battery sensor directly to `internal_pct`.
  - Option B: Use property-level dynamic logic inside `native_value` to check if `external_pct` is `None`
    and return `internal_pct` as a fallback.
- **Decision**: Option B.
- **Rationale**: Retains combined total capacity tracking for users with physical expansion batteries
  connected, while dynamically presenting accurate main unit percentages for single-unit setups.

### Decision 2: 12V Car Port Switch Icon allocation
- **Options Considered**:
  - Option A: Custom SVG asset injection.
  - Option B: Reallocate to the standard `mdi:car-power-outlet` icon.
- **Decision**: Option B.
- **Rationale**: Highly descriptive and globally available in Home Assistant's default Material
  Design Icon set.

### Decision 3: CI Release Pipeline Bump Logic
- **Options Considered**:
  - Option A: Retain patch/minor bump rules.
  - Option B: Parse the git log for `major` / `breaking` keywords to trigger a major semver release.
- **Decision**: Option B.
- **Rationale**: Allows triggering release milestones (like `v1.0.0`) directly via commit logs.

### Decision 4: Cap pre-generated shutdown timer options to 18 hours
- **Options Considered**:
  - Option A: Handle OverflowError inside select.py when converting seconds to 2 bytes.
  - Option B: Cap the pre-generated dropdown options list to a maximum of 18 hours (64,800 seconds).
- **Decision**: Option B.
- **Rationale**: Since a 2-byte uint16 payload can only hold up to 65,535 seconds (18.2 hours), any option above
  this limit is physically impossible to transmit on the wire and will always fail. Capping the select options
  to 18 hours completely eliminates the runtime error by design and improves user experience.

## Risks / Trade-offs

- **[Risk] CI parsing failure**: Tampering with the CI workflow shell scripts might cause release
  failures on pushes to main.
  - *Mitigation*: Run validation runs or inspect code structure closely before pushes.
