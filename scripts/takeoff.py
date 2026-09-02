'''
LAUNCH DRONE TO A SET ALTITUDE, LOITER, THEN LAND
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import drone, settings



drone_1 = drone.Drone(settings.connection_string, settings.baud)

# Determines if run from CLI or Sim
if len(sys.argv) > 1:
    # This catches the arguement when running from command line,
    # ie. python3 takeoff.py 10
    target_altitude = (int(sys.argv[1]))
else:
    target_altitude = 10


if target_altitude <= 0 or target_altitude > 20:
    print("Altitude must be within 20 meters")

else:
    drone_1.mode_guided()
    drone_1.drone_arm()
    drone_1.drone_takeoff(target_altitude)
    time.sleep(8)
    drone_1.mode_land()
    drone_1.drone_disarm()
    drone_1.close()