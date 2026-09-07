'''
DUMPING GROUND FOR SMALL TESTS!
'''
import math

def move_circle(radius = 10):
    current_x, current_y, current_z = 70,90,0,
    degrees = 0

    #if not self.is_armed():
    #    print("Drone is not armed. Cannot move in a circle.")
    #    return

    #else:
    coords = []
    # Plotting points around a circle
    while degrees <= 360:
        angle_radian = math.radians(degrees)
        current_x += radius * math.cos(angle_radian)
        current_y += radius * math.sin(angle_radian)
        current_z += 0
        coords.append((current_x, current_y, current_z))
        degrees += 10

    print(coords)
            
            
move_circle()