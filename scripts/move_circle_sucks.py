'''
MOVE THE DRONE IN A CIRCLE PATTERN
'''


import main

def run():
    drone_1 = main.pi_or_sim()
    drone_1.guided_arm_takeoff()
    drone_1.fly_circle_terrible(10)
    drone_1.rtl_disarm()


if __name__ == "__main__":
    run()