from drone_core import Drone_Core
from drone_commands import Drone_Commands
from drone_missions import Drone_Missions
from drone_patterns import Drone_Patterns
from drone_wrappers import Drone_Wrappers

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


''' 
ORIGINAL FILE WAS GETTING LARGE
USING A TRICK I FOUND HERE CALLED MIXINS
SET UP CLASSES WITH GROUPED FUNCTIONS
THEN DRONE INHERITS FROM ALL OF THEM
MY CODE WILL WORK THE SAME AS BEFORE
NO NEED TO REWRITE
'''


class Drone(Drone_Core, Drone_Commands, Drone_Missions, Drone_Patterns, Drone_Wrappers):
    pass