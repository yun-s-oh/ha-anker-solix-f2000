## 1. Sensor Platform Refinements

- [x] 1.1 Rename "12V Car Port 1 Timer Remaining" to "12V Car Port Timer Remaining" in sensor.py
- [x] 1.2 Add the new "AC Sockets Timer Remaining" sensor entity under SENSOR_DESCRIPTIONS in sensor.py

## 2. Validation & Deployment

- [x] 2.1 Run Python compile syntax check on all custom component files
- [x] 2.2 Run flake8 and mypy validations to ensure full code style compliance
- [x] 2.3 Verify all unit tests in the pytest suite pass cleanly
- [x] 2.4 Restart Home Assistant and manually verify the entities populate correctly on the UI
