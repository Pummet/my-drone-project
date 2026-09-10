'''
DUMPING GROUND FOR SMALL TESTS!
'''
import sys, os, time, math

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main, settings


drone_1 = main.create_drone(settings.connection_string, settings.baud_rate)



start = (1,0,10)
target = (1, 0, 10)

start_pos = drone_1.get_position_ned()
print(type(start_pos))

print(start == target)

print(400 % 360)