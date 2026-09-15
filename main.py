from drone import Drone

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
    drone_1 = pi_or_sim()
    drone_1.drone_takeoff(2)

