from drone_files.drone import Drone
import video.video_functions

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

    missions = {
        1: drone.guided_arm_takeoff,
        2: drone.fly_square,
        3: drone.fly_circle,
        4: drone.fly_figure_eight,
        5: "",
        6: "",
        7: "",
        8: "",
        9: drone.land_disarm,
        }

    try: # Due to running on the Pi, I'll be cancelling the execution with CTRL C
        while True:
            gesture = video.video_functions.finger_counter()

            if gesture in missions:
                try: # Try/Except block here catches bad mission calls, prints an error and keeps looking for gestures
                    missions[gesture]()
                except Exception as e:
                    print(f"Missiong for gesture {gesture} failed: {e}")
            elif gesture == 10:
                break
            else:
                print("No mission mapped to that gesture")

    except KeyboardInterrupt: # Keyboard trigger
        print("Interrupted by user")
        
    finally: # This always runs before the program closes
        video.video_functions.release_camera()
        drone.drone_disarm()
        drone.close()
        print("Drone disarming and disconnecting...")