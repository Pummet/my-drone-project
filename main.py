from drone_files.drone import Drone
import video.pi_video

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
        9: drone.land_disarm,
        }


    ######## !!!!! MESSY AND NEEDS WORK !!!!! ########

    try: # Due to running on the Pi, I'll be cancelling the execution with CTRL C
        while True:
            gesture = video.pi_video.finger_counter()

            if gesture in missions:
                
                try: # Try/Except block here catches bad mission calls, prints an error and keeps looking for gestures
                    if gesture == 1: # launch command
                        missions[gesture]()
                    else: # check that drone is armed and airborne
                        altitude = drone.get_altitude()
                        if not (drone.armed() and altitude is not None and altitude > 0.5):
                            print("Gesture failed. Drone not armed or airborne.")
                            continue # skip the mission and the return to 1.5m

                        # goes up to 10 meters and executes
                        drone.send_coords_ned(0, 0, -10)
                        drone.target_altitude_checker(10)
                        missions[gesture]()

                    if gesture != 9: # drone has landed on mission 9
                        drone.send_coords_ned(0,0,-1.5) # Drone returns to 1.5m above launch for next command

                except Exception as e:
                    print(f"Mission for gesture {gesture} failed: {e}")

            elif gesture == 10:
                break
            else:
                print("No mission mapped to that gesture")

    except KeyboardInterrupt: # Keyboard trigger
        print("Interrupted by user")
        
    finally: # This always runs before the program closes
        video.pi_video.release_camera()
        drone.change_flight_mode("land")
        drone.drone_disarm()
        drone.close()
        print("Drone disconnecting...")