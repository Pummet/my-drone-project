'''
MOVE THE DRONE IN A CIRCLE PATTERN
'''

import sys, os

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


drone_1 = main.pi_or_sim()


drone_1.guided_arm_takeoff()
drone_1.fly_circle_terrible(10)
drone_1.change_flight_mode("rtl")
drone_1.drone_disarm()
drone_1.close()