from drone import Drone
import settings, sys



def create_drone(connection, baud = None):
    return Drone(connection, baud)



def drone_arm_mission(drone, path):
    drone.guided_arm_takeoff(10)
    drone.upload_mission(drone.load_waypoint(path))
    drone.mode_auto()
    drone.monitor_until_disarmed()



# This function checks if Pi or desktop is running the code
# Don't need to manually change everytime!!!
def pi_or_sim():
    if len(sys.argv) > 1 and sys.argv[1] == "pi":
        connection = settings.connection_string
        baud = settings.baud_rate
        drone = create_drone(connection, baud)

    else:
        connection = "tcp:127.0.0.1:5763"
        drone = create_drone(connection)

    return drone



if __name__ == "__main__":
    drone_1 = pi_or_sim()
    drone_arm_mission(drone_1, settings.path)
    drone_1.clear_mission()