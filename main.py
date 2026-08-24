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


# This function checks if Pi or desktop is running the code
# Don't need to manually change everytime!!!
def pi_or_sim():
    if len(sys.argv) > 1 and sys.argv[1] == "pi":
        connection = "/dev/ttyAMA0"
        baud = 57600
        drone = create_drone(connection, baud)

    else:
        connection = "tcp:127.0.0.1:5763"
        drone = create_drone(connection)

    return drone



drone_1 = pi_or_sim()
path = "/home/pummet/Documents/Projects/my-drone-project/missions/airfield.txt"

drone_arm_mission(drone_1, path)
drone_1.clear_mission()