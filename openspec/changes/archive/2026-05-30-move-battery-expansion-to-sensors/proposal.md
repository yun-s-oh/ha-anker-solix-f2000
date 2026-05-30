## Why

Currently, the "Internal Battery" (`internal_pct`) and "External Battery Expansion" (`external_pct`) capacity sensors are categorized as `EntityCategory.DIAGNOSTIC`. This hides them from default Home Assistant dashboard cards and primary entity views. Since users with external batteries need to monitor their individual battery states and expansion capacities alongside the main battery percentage, these should be first-class, standard sensor entities without the diagnostic classification.

## What Changes

- Modify `sensor.py` to remove `entity_category=EntityCategory.DIAGNOSTIC` from the `"Internal Battery"` (`internal_pct`) sensor description.
- Modify `sensor.py` to remove `entity_category=EntityCategory.DIAGNOSTIC` from the `"External Battery Expansion"` (`external_pct`) sensor description.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `ha-sensors`: Promote internal battery and external battery expansion capacity metrics to standard sensors to ensure they are visible in primary Home Assistant dashboards.

## Impact

- The entities `sensor.<device_name>_internal_battery` and `sensor.<device_name>_external_battery_expansion` will no longer have `entity_category` set to `diagnostic`, making them visible as standard entities in the Home Assistant UI by default.
