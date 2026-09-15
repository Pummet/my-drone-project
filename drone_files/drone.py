from drone_files.drone_core import Drone_Core
from drone_files.drone_commands import Drone_Commands
from drone_files.drone_missions import Drone_Missions
from drone_files.drone_patterns import Drone_Patterns
from drone_files.drone_wrappers import Drone_Wrappers

''' 
Originally I had all functions under class Drone(), but it was starting to get a bit unwieldy.
Searched around and found this, which is called a mixin. Can set up many classes and group functions together,
then create class Drone that inherits from all of them. I can use this class like drone_1 = Drone(etc etc), and it will
inherit all functions! Very cool!
'''


class Drone(Drone_Core, Drone_Commands, Drone_Missions, Drone_Patterns, Drone_Wrappers):
    pass