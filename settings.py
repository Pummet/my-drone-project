################ BASH COMMANDS ################
# Gazebo   gz sim -v4 -r iris_runway.sdf
# SITL     sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -L Brockenhurst
# QGC      ~/Applications/QGroundControl.AppImage


############## Pi to FC settings ##############
#   TELEM3 UART:      '/dev/ttyAMA0'
#   On SITL           'tcp:127.0.0.1:5763'


############## Computer to Pi #################
#   Toggle field:      sudo wifi-toggle.sh ap
#   Toggle home:       sudo wifi-toggle.sh home

#   Home WiFi:         ssh pummet@drone-pi.local
#   In the field AP:   ssh pummet@192.168.4.1


#################### NOTES ####################
# GIT PULL BEFORE STARTING

# SAVE, then:
# git add .
# git commit -m "describe what changed"
# git push

# self.vehicle     -> pymavlink connection object, high level helper functions
#                     eg. arducopter_arm(), set_mode_apm()
# self.vehicle.mav -> pymavlink raw MAVLink message senders
#                     eg. mission_count_send(), mission_item_int_send()
# self.method_name -> my own methods


connection_string = '/dev/ttyAMA0'
baud_rate = 57600

# This will need to change, path is different on the Pi
path = "/home/pummet/Documents/Projects/my-drone-project/waypoints/daryl_coop.txt"