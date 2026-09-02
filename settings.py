############# BASH COMMANDS #############
# Gazebo   gz sim -v4 -r iris_runway.sdf
# SITL     sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -L Brockenhurst
# QGC      ~/Applications/QGroundControl.AppImage


# --- Connection settings ---
#   TELEM3 UART:      '/dev/ttyAMA0'
#   On Radio:         'COM8'
#   On SITL           'tcp:127.0.0.1:5763'

connection_string = '/dev/ttyAMA0'
baud_rate = 57600
num_motors = 4

# This will need to change, path is different on the Pi
path = "/home/pummet/Documents/Projects/my-drone-project/missions/airfield.txt"