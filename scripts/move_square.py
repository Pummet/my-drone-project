'''
MOVE THE DRONE IN A SQUARE PATTERN
'''


import main, time

def run():
    drone_1 = main.pi_or_sim()
    drone_1.guided_arm_takeoff(10)
    drone_1.fly_square()
    time.sleep(1)
    drone_1.rtl_disarm()


if __name__ == "__main__":
    run()