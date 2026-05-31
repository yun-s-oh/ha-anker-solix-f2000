## 1. Sensor & Switch Platform Updates

- [x] 1.1 Implement smart dynamic battery fallback in sensor.py
- [x] 1.2 Update the 12V Car Port Master switch icon in switch.py to use mdi:car-electric
- [x] 1.3 Cap the pre-generated select dropdown options for AC/DC shutdown timers to 18 hours in select.py

## 2. CI Release & Documentation Updates

- [x] 2.1 Refactor the release workflow versioning check to detect major/breaking commit keywords
- [x] 2.2 Correct obsolete change directory references in agent-guidelines.md
- [x] 2.3 Document the new AC Sockets Timer and refined 12V Car Port Timer in README.md

## 3. Validation & Testing

- [x] 3.1 Run Python compile syntax check on all custom component files
- [x] 3.2 Run flake8 validation to ensure full code style compliance
- [x] 3.3 Verify all unit tests in the pytest suite pass cleanly
- [x] 3.4 Restart Home Assistant and manually verify the entities and icons render correctly on the UI
