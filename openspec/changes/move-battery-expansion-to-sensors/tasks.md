## 1. Component Modifications

- [x] 1.1 Remove `entity_category=EntityCategory.DIAGNOSTIC` from `internal_pct` sensor in `sensor.py`
- [x] 1.2 Remove `entity_category=EntityCategory.DIAGNOSTIC` from `external_pct` sensor in `sensor.py`

## 2. Code Quality and Linting

- [x] 2.1 Run compilation check via `py_compile`
- [x] 2.2 Run formatting and styling checks via `flake8`

## 3. Testing and Verification

- [x] 3.1 Run isolated test suite via `pytest`
- [x] 3.2 Restart Home Assistant docker container to apply updates
