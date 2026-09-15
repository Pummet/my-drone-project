from drone_files.drone import Drone
import vision.camera_functions

import settings, sys

# This function checks if Pi or desktop is running the code
# Don't need to manually change everytime!!!
def pi_or_sim():
    if len(sys.argv) > 1 and sys.argv[1] == "pi":
        connection = settings.connection_string
        baud = settings.baud_rate
        drone = Drone(connection, baud)

    else:
        connection = "tcp:127.0.0.1:5763"
        drone = Drone(connection)

    return drone



if __name__ == "__main__":
    drone = pi_or_sim()
    drone.drone_takeoff(2)

    missions = {
        1: drone.guided_arm_takeoff,
        2: drone.move_square,
        3: drone.fly_circle,
        4: drone.move_figure_eight,
        5: "",
        6: "",
        7: "",
        8: "",
        9: drone.land_disarm,
        }

    while True:
        gesture = vision.camera_functions.finger_counter()

        if gesture in missions:
            missions[gesture]()
        elif gesture == 10:
            vision.camera_functions.release_camera()
            drone.drone_disarm()
            drone.close()
            print("Drone disconnecting...")
            break
        else:
            print("No mission mapped to that gesture.")