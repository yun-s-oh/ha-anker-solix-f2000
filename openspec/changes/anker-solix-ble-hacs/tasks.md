## 1. Research and Documentation

- [x] 1.1 Document the known BLE services, characteristics, and custom packet hex layout for Anker Solix F2000 in `specs/ble-protocol/spec.md`
- [x] 1.2 Create `agent-guidelines.md` detailing the project structure, BLE protocol specifications, and coding patterns for developer/agent alignment

## 2. Standalone Command Line Test Scripts

- [x] 2.1 Set up a clean Python virtual environment structure, including a requirements file with `bleak` and `SolixBLE`
- [x] 2.2 Create `test_telemetry.py` standalone CLI script to scan for nearby Anker BLE devices, connect to a designated MAC address, and print formatted parsed telemetry
- [x] 2.3 Create `test_heartbeat.py` standalone CLI script that maintains an active connection and issues keep-alive pings to verify timeout prevention

## 3. Docker Test Environment

- [x] 3.1 Create a `Dockerfile` (utilizing `venv`) and `docker-compose.yml` to package unit tests and local Home Assistant
- [x] 3.2 Implement a mock BLE client parser module in Python to generate mock byte streams for automated testing
- [ ] 3.3 Create a comprehensive `pytest` suite that feeds mock byte packets to the parser and asserts correct extraction of battery and power metrics

## 4. Core Home Assistant Integration

- [ ] 4.1 Scaffold the `custom_components/anker_solix_f2000/` directory structure with `manifest.json` and requirements
- [ ] 4.2 Implement `config_flow.py` supporting automatic BLE advertisement discovery and user pairing UI
- [ ] 4.3 Implement `coordinator.py` to register the `BluetoothDataUpdateCoordinator`, managing passive notification listeners and coordinating sensor state updates
- [ ] 4.4 Implement `sensor.py` defining HA entities (Battery %, AC output power, DC output power, temperature) with official HA DeviceClasses and units

## 5. Failover and Connection Recovery

- [ ] 5.1 Implement active 5-minute heartbeats inside the integration coordinator to bypass the F2000's 12-hour Bluetooth radio sleep timeout
- [ ] 5.2 Implement an exponential back-off reconnection handler in the BLE client to recover gracefully from connection drops or exclusive phone-app lockouts
- [ ] 5.3 Verify log warning triggers for exclusive connection limits and ensure system state defaults gracefully during downtime
