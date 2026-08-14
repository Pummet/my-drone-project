
from drone import Drone


def create_drone(tcp):
    return Drone(tcp)

def drone_arm_mission(drone, path):
    drone.mode_guided()
    drone.drone_arm()
    drone.drone_takeoff(10)
    drone.upload_mission(drone.load_waypoint(path))
    drone.mode_auto()
    drone.monitor_until_disarmed()


tcp = "tcp:127.0.0.1:5763"
path = "/home/pummet/Documents/Projects/my-drone-project/missions/short.txt"

drone_1 = create_drone(tcp)
drone_arm_mission(drone_1, path)
drone_1.clear_mission()