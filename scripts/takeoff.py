'''
LAUNCH DRONE TO A SET ALTITUDE, HOVER, THEN LAND
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

drone_1 = main.pi_or_sim()


# Catches parameters from command line, ie. python3 move_square.py 10
if len(sys.argv) > 1:
    target_altitude = (int(sys.argv[1]))
else:
    target_altitude = 10


if target_altitude <= 0 or target_altitude > 20:
    print("Altitude must be within 20 meters")

else:
    drone_1.guided_arm_takeoff(target_altitude)
    time.sleep(8)
    drone_1.rtl_disarm()