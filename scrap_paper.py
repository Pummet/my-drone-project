'''
DUMPING GROUND FOR SMALL TESTS!
'''

import math
import matplotlib.pyplot as plt

radius = 10
degrees_per_turn = 0

coords = []
while degrees_per_turn < 360:
    angle_radian = math.radians(degrees_per_turn)
    x = radius * math.cos(angle_radian)
    y = radius * math.sin(angle_radian)
    coords.append((x, y))
    degrees_per_turn += 10




xs = [c[0] for c in coords]
ys = [c[1] for c in coords]

plt.figure(figsize=(6, 6))
plt.plot(xs, ys, 'o-')
plt.gca().set_aspect('equal')
plt.grid(True)
plt.title("Points around a circle")
plt.show()