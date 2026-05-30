## Context

The integration exposes "Internal Battery" (`internal_pct`) and "External Battery Expansion" (`external_pct`) as diagnostic sensor entities. Home Assistant standard conventions recommend categorizing system-level internal/external battery metrics as diagnostic if they are secondary properties. However, for battery expansion systems like the F2000, individual battery capacity monitoring is a key primary concern for real-time dashboard monitoring, making standard sensor classification highly desirable.

## Goals / Non-Goals

**Goals:**
- Promote `"Internal Battery"` (`internal_pct`) and `"External Battery Expansion"` (`external_pct`) to standard sensor entities by removing the `entity_category` property from their descriptions in `sensor.py`.
- Ensure standard entity registry behavior in Home Assistant (the sensors will render in default auto-generated dashboards by default).
- Verify that unit tests continue to pass and correctly cover the modified descriptions.

**Non-Goals:**
- Modifying underlying BLE telemetry structure, communication rate, parsing scales, or other metrics.
- Removing or changing diagnostic status on auxiliary properties such as system logs or settings.

## Decisions

### Decision: Native Promotion via SensorEntityDescription
We will modify the descriptions for `internal_pct` and `external_pct` in `SENSOR_DESCRIPTIONS` inside `sensor.py` directly by deleting `entity_category=EntityCategory.DIAGNOSTIC`.

- **Alternative 1: Keep diagnostic classification but instruct users to manually enable them in Home Assistant Settings.**
  - *Cons*: Poor user onboarding experience; users must manually search and toggle them.
- **Alternative 2: Directly remove the category classification in the python description schema.**
  - *Pros*: Provides out-of-the-box visibility on all dashboards immediately upon discovery or manual installation.

## Risks / Trade-offs

- **[Risk]**: The default Home Assistant overview page might look busier due to two new battery entities being exposed as primary cards.
  - *Mitigation*: This is a minor trade-off as users explicitly want to see these details alongside the total battery capacity.
