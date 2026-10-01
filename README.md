# Semi-Autonomous Drone System

First-year Data Science & AI student building a drone as a personal project. Don't expect anything polished, I'm documenting the journey as I go. This was my first time using Linux, connecting programs together, and using GitHub.

A flight control system built around **ArduPilot** and **pymavlink**, developed in **Gazebo Harmonic / SITL** simulation and now flown on a real **Holybro X500** quadcopter with a **Raspberry Pi 5** companion computer. The drone can be commanded by **hand signals**: a camera counts the fingers I hold up and each number triggers a different mission.

The core of the project is a custom Python `Drone` class that wraps pymavlink to handle mode switching, arming, takeoff, waypoint missions, and flight patterns.

The long-term goal is a drone swarm, with a mothership on an Nvidia Jetson Orin Nano directing the rest of the fleet.

## Features

- **Gesture control**: MediaPipe hand tracking counts fingers (1-10, using both hands). A gesture must be held for 15 frames in a row before it triggers
- **Flight patterns**: square, circle and figure-eight, flown using velocity vectors for smooth movement
- **Mode control**: switches ArduPilot flight modes by name and waits for the acknowledgement
- **Arming and takeoff**: blocks until the motors are armed and the target altitude is reached
- **Waypoint missions**: loads QGC WPL files, uploads them over MAVLink and runs them in AUTO mode
- **Position, velocity and yaw commands**: local NED, GPS and velocity targets
- **Failsafe sequences**: RTL falls back to LAND, LAND retries 3 times, and there is a low-battery RTL check
- **Same code in sim and on the drone**: `main.py` picks the right connection depending on how it is launched

## Hardware

- **Frame:** Holybro X500
- **Motors:** 4 x Holybro 2216 KV920
- **ESCs:** BLHeli S 20A, with XT30 power connectors
- **Props:** 4 x 10" propellors
- **Flight controller:** Pixhawk 6C running ArduCopter
- **Power:** 4S LiPo
- **Companion computer:** Raspberry Pi 5 (headless Ubuntu Server), connected to the flight controller over UART (TELEM3, `/dev/ttyAMA0`, 921600 baud)
- **5A Step Down Lead:** Safely provides power to the Raspberry Pi
- **Camera:** Raspberry Pi camera, read with `picamera2`
- **M10 GPS Receiver:** For Loitering and position tracking
- **Telemetry radio:** SiK radio link to the ground, used for live tracking in the field
- **ELRS Receiver:** For radio control via a RadioMaster Pocket
- 

## Software stack

| Where | What |
| --- | --- |
| **ArduPilot** | Flight controller firmware (SITL in simulation, on the Pixhawk in real life) |
| **pymavlink** | Talks to the flight controller directly. |
| **Gazebo Harmonic** | 3D physics simulation, using the `ardupilot_gazebo` plugin and the Iris quadcopter model |
| **MediaPipe** | Hand landmark detection for gesture control |
| **OpenCV** | Camera input and image conversion. On the desktop it reads a webcam, with a full GUI test tool |
| **picamera2** | Camera input on the Raspberry Pi (only installs on the Pi) |
| **Mission Planner** | Live tracking in the field over the SiK telemetry radio (Windows) |
| **QGroundControl** | Ground control for simulation, used alongside SITL and Gazebo (Ubuntu) |
| **MAVProxy** | Launched by `sim_vehicle.py` alongside SITL |

I develop across three machines:

- **Windows:** Mission Planner for tracking real flights over the SiK radio, and webcam gesture testing with OpenCV
- **Ubuntu 24.04 (dual boot):** Gazebo, SITL and QGroundControl for simulation
- **Raspberry Pi 5:** the real flights

## Architecture

`Drone` is built from several small classes (mixins), each in its own file, because one giant class got unwieldy. `Drone` inherits from all of them, so a script only ever needs one object.

`Drone_Core` wraps a `pymavlink.mavlink_connection`, waits for a heartbeat, and requests all data streams at 6 Hz. Reading telemetry works by draining the message buffer and using the latest message of each type, so functions never act on stale data.

Waypoint files are in the standard **QGC WPL 110** format (exported by QGroundControl and Mission Planner). They are parsed into `[command, lat, lon, alt]` lists and uploaded as `MISSION_ITEM_INT` messages.

### Gesture control

`main.py` loops forever, waiting for a confirmed gesture:

| Fingers | Action |
| --- | --- |
| 1 | Arm and take off to 1.5 m |
| 2 | Fly a square |
| 3 | Fly a circle |
| 4 | Fly a figure-eight |
| 9 | Land and disarm |
| 10 | Exit the program (lands and disarms) |

Gestures 2-4 only run if the drone is armed and above 0.5 m. It climbs to 10 m, flies the pattern, then drops back to 1.5 m ready for the next command. Pressing CTRL+C also lands and disarms.

### Flight patterns

- **Circle:** velocity vectors sent every 0.1 s, with the drone facing the centre. Speed scales with radius (based on 5 m/s at a 15 m radius, capped at 10 m/s). My first version (`fly_circle_terrible`) stopped at every point and was very jittery, so it is kept next to the good one for comparison
- **Figure-eight:** two mirrored circles
- **Square:** position targets in local NED, with a 90 degree yaw at each corner

## Getting started

### Simulation (Ubuntu 24.04)

Prerequisites:

- Gazebo Harmonic from the OSRF apt repo (the snap version doesn't have the required `-dev` packages)
- ArduPilot SITL built from source
- The `ardupilot_gazebo` plugin built and configured (`GZ_SIM_SYSTEM_PLUGIN_PATH`, `GZ_SIM_RESOURCE_PATH`)

**1. Start Gazebo** with the Iris quadcopter on the runway world:

```bash
gz sim -v4 -r iris_runway.sdf
```

**2. In a second terminal, start ArduPilot SITL:**

```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console
```

**3. Open QGroundControl** (download the AppImage, `chmod +x` it and run it). It connects to SITL on UDP 14550 and shows the simulated drone alongside Gazebo.

**4. Install dependencies and run:**

```bash
pip install -r requirements.txt
python3 main.py
```

In simulation, `main.py` connects to `tcp:127.0.0.1:5763` and uses the desktop webcam for gestures.

Common first-run dependency gaps (fixed with `pip install --break-system-packages`): `empy==3.3.4`, `MAVProxy`, `future`, `matplotlib`, `opencv-python`.

### On the drone (Raspberry Pi)

SSH into the Raspberry Pi first. (git pull if needed)

```bash
python3 main.py
```

### Small test flights

The `scripts/` folder has single-purpose flights (`takeoff.py`, `move_square.py`, `move_circle.py`, `move_figure_eight.py`, `video_capture.py`). Each one creates its own drone connection, so don't import them into other files. Example:

```bash
python3 scripts/takeoff.py
```

### Tests

- `tests/motor_test.py` spins each motor briefly.
- `tests/connection_test.py` checks for a heartbeat

## Roadmap

- [x] Physical build: Holybro X500, Pixhawk 6C, Raspberry Pi 5 companion computer
- [x] Pi bridged to the Pixhawk over UART
- [x] Real-world flight testing (CAA Flyer ID / Operator ID obtained)
- [x] Onboard video feed and hand-signal control
- [x] Low-battery RTL check (written, not currently switched on)
- [ ] Migration to Jetson Orin Nano with ROS2 / MAVROS
- [ ] Drone swarm, with a Jetson Orin Nano mothership directing multiple vehicles

## Notes

This project started as a way to build hands-on experience with autonomous systems ahead of a possible career in defence or automation. Simulation testing first is the way to go so as not to potentially damage a real drone.
