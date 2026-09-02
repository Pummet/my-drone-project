'''
RETURNS HEARTBEAT IF CONNECTED
'''

import sys, os

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import settings


vehicle = mavutil.mavlink_connection(settings.connection_string, settings.baud_rate)

if vehicle.wait_heartbeat(timeout = 5) is None:
    print("No heartbeat recieved")

else:
    print(f"Heartbeat received from system {vehicle.target_system}")