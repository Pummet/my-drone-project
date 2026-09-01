import sys, os, time
# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drone import Drone
import settings

connection_string = settings.connection_string
baud = settings.baud_rate
drone = Drone(connection_string, baud)

target_altitude = (int(sys.argv[1]))

if target_altitude <= 0 or target_altitude > 20:
    print("Altitude must be within 20 meters")
else:
    drone.mode_guided()
    drone.drone_arm()
    drone.drone_takeoff(target_altitude)
    drone.mode_loiter()
    time.sleep(5)
    drone.mode_land()
    drone.drone_disarm()