'''
RETURNS HEARTBEAT IF CONNECTED
'''

import sys, os

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


drone = main.pi_or_sim()

if drone.wait_heartbeat(timeout = 5) is None:
    print("No heartbeat recieved")

else:
    print(f"Heartbeat received from system {drone.target_system}")