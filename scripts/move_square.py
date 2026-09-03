'''
MOVE THE DRONE IN A SQUARE PATTERN
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main, settings


drone_1 = main.create_drone(settings.connection_string, settings.baud_rate)


drone_1.guided_arm_takeoff(10)
drone_1.move_square()
time.sleep(3)
drone_1.mode_land()
drone_1.drone_disarm()
drone_1.close()