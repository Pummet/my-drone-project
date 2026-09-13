'''
MOVE THE DRONE IN A CIRCLE PATTERN
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main, settings


drone_1 = main.create_drone(settings.connection_string, settings.baud_rate)


drone_1.guided_arm_takeoff()

start_time = time.time()
duration = 60
angle_radian = 0.0
radius = 3
meters_sec = drone_1.calculate_meters_sec(radius)

while time.time() - start_time <= duration:
    angle_radian = drone_1.move_circle(3, angle_radian, meters_sec)
    time.sleep(0.1)

drone_1.change_flight_mode("rtl")
drone_1.drone_disarm()
drone_1.close()