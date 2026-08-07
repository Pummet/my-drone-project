[README(1).md](https://github.com/user-attachments/files/30827089/README.1.md)
# Autonomous Drone Control System

An autonomous flight control system built around **ArduPilot** and **pymavlink**, developed and tested end-to-end in **Gazebo Harmonic / SITL simulation**, with the goal of deploying to a real **Holybro X650** quadcopter running a **Raspberry Pi 5** companion computer.

The core of the project is a custom Python `Drone` class that wraps pymavlink to handle mode switching, arming, takeoff, mission upload, and autonomous flight execution.

In the future, I want to add a video feed with image recognition so the drone can be controlled via hand signals. The ultimate goal is a drone swarm, with a mothership running on an Nvidia Jetson Orin Nano directing the rest of the fleet.

## Features

- **Mode control** — GUIDED, AUTO, RTL, STABILIZE, LAND
- **Arming** — with blocking wait for confirmed motor arm
- **Guided takeoff** — climbs to a target altitude with live telemetry monitoring
- **Waypoint loading** — parses QGC WPL format mission files
- **Mission upload** — sends waypoint count + mission items over MAVLink, switches to AUTO to execute
- **Live telemetry streaming** — requests all data streams at 10Hz on connection

## Stack

- **ArduPilot** (SITL) — flight controller firmware, running in simulation
- **Gazebo Harmonic** — 3D physics simulation, using the `ardupilot_gazebo` plugin and the Iris quadcopter model
- **pymavlink** — Python MAVLink implementation used to talk to the flight controller directly (chosen over DroneKit, which is deprecated and no longer maintained)
- **MAVProxy** — ground control station used alongside Gazebo for live console/map monitoring during development
- **Ubuntu 24.04** — development environment, dual-booted alongside Windows

## Architecture

`drone.py` defines a `Drone` class that wraps a `pymavlink.mavlink_connection`. Each method (`mode_guided`, `drone_arm`, `drone_takeoff`, `upload_mission`, etc.) sends the relevant MAVLink message(s) and, where needed, blocks until a confirming message is received — for example, `drone_takeoff` polls `GLOBAL_POSITION_INT` until the target altitude is reached before returning control to the calling script.

Waypoint files are expected in **QGC WPL 110** format (the standard Mission Planner / QGroundControl export format), parsed into `[command, lat, lon, alt]` tuples before being uploaded over MAVLink as `MISSION_ITEM_INT` messages.

## Getting Started (Simulation)

### Prerequisites

- Ubuntu 24.04 (or WSL2 equivalent)
- Gazebo Harmonic (via OSRF apt repo — the snap version won't have the required `-dev` packages)
- ArduPilot SITL built from source
- The `ardupilot_gazebo` plugin built and configured (`GZ_SIM_SYSTEM_PLUGIN_PATH`, `GZ_SIM_RESOURCE_PATH`)

### Running the simulation

**1. Start Gazebo** with the Iris quadcopter on the runway world:

```bash
gz sim -v4 -r iris_runway.sdf
```

**2. In a separate terminal, launch ArduPilot SITL + MAVProxy:**

```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
```

This launches ArduCopter SITL and MAVProxy (with console + map), and connects to the running Gazebo instance from step 1.

**Alternative ground control station:** MAVProxy's console/map are used for lightweight monitoring above, but [QGroundControl](http://qgroundcontrol.com/) is a more full-featured native Linux GCS if needed — download the AppImage, `chmod +x` it, and run directly. It can connect to the same SITL instance (default UDP port 14550) alongside or instead of MAVProxy.

**Common first-run dependency gaps** (all fixed with `pip install --break-system-packages`):
- `empy==3.3.4` — required for the SITL build itself
- `MAVProxy` — the ground control station
- `future` — required by MAVProxy's console module
- `matplotlib` — required for MAVProxy's console GUI
- `opencv-python` — required for MAVProxy's map module

### Running a mission

```bash
python3 drone.py
```

Update the `tcp` connection string and mission file `path` in `drone.py` to match your setup. By default it connects to `tcp:127.0.0.1:5763` (SITL's default output port) and expects a QGC WPL-format waypoint file.

## Roadmap

- [ ] Physical build: Holybro X650 frame, Pixhawk 6C, 6S power system
- [ ] Raspberry Pi 5 companion computer (headless Ubuntu Server) bridging to the Pixhawk over UART
- [ ] Battery failsafe handling via `SYS_STATUS.voltage_battery`
- [ ] Real-world flight testing (CAA Flyer ID / Operator ID obtained)
- [ ] Onboard video feed + image recognition for hand-signal control
- [ ] Migration to Jetson Orin Nano + ROS2/MAVROS for onboard compute
- [ ] Drone swarm — Jetson Orin Nano mothership directing multiple vehicles

## Notes

This project started as a way to build hands-on experience with autonomous systems ahead of a career in defence/autonomy engineering. Simulation-first development was a deliberate choice — proving out arming, mission logic, and failure handling in Gazebo before any of it touches a real airframe.
