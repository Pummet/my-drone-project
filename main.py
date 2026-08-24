from drone import *
import sys

def create_drone(connection):
    return Drone(connection)

def drone_arm_mission(drone, path):
    drone.mode_guided()
    drone.drone_arm()
    drone.drone_takeoff(10)
    drone.upload_mission(drone.load_waypoint(path))
    drone.mode_auto()
    drone.monitor_until_disarmed()


# This IF checks if Pi or desktop is running the code
# Don't need to manually change everytime!!!
if len(sys.argv) > 1 and sys.argv[1] == "pi":
    connection = "/dev/ttyAMA0"
    baud = 57600
else:
    connection = "tcp:127.0.0.1:5763"


path = "/home/pummet/Documents/Projects/my-drone-project/missions/short.txt"


drone_1 = create_drone(connection)
drone_arm_mission(drone_1, path)
drone_1.clear_mission()