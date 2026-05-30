## 1. Standalone Exploration Script Setup

- [x] 1.1 Create `tests/explore_controls.py` exploration script with interactive menu
- [x] 1.2 Implement automatic unencrypted checksum generation in `explore_controls.py`
- [x] 1.3 Implement continuous notifications sniffer and hex grid logger

## 1.4 Standalone Controls Verification (Extensive Discovery)

- [x] 1.4.1 Verify unencrypted AC Output Toggle commands and validate State ACK updates
- [x] 1.4.2 Verify unencrypted DC Output Toggle commands and validate State ACK updates
- [ ] 1.4.3 Verify unencrypted Power Saving Mode toggle commands
- [ ] 1.4.4 Test LED Brightness level commands (Off, Low, Mid, High, SOS)
- [ ] 1.4.5 Test Screen Timeout commands (20s, 30s, 1m, 5m, 30m)
- [ ] 1.4.6 Test Screen Brightness adjustment commands
- [ ] 1.4.7 Test AC Recharging Power Limit commands (200W - 2200W)
- [ ] 1.4.8 Document finalized byte structures and ACK patterns in the Design Document

## 2. Core Home Assistant Controls Integration

- [ ] 2.1 Add `switch.py` exposing AC Output, DC Output, and Power Saving Mode
- [ ] 2.2 Add `select.py` exposing LED Brightness, Screen Brightness, and Screen Timeout
- [ ] 2.3 Add `number.py` exposing AC Recharging Power limit
- [ ] 2.4 Update HASS setup registration under `__init__.py` to load new control platforms

## 3. Documentation & Verification

- [ ] 3.1 Update `README.md` to document control entities and test scripts
- [ ] 3.2 Verify all changes compile and pass validation tests
