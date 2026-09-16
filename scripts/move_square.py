'''
MOVE THE DRONE IN A SQUARE PATTERN
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main, settings


drone_1 = main.pi_or_sim()


drone_1.guided_arm_takeoff()
drone_1.fly_square()
time.sleep(1)
drone_1.change_flight_mode("rtl")
drone_1.drone_disarm()
drone_1.close()