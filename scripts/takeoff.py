'''
LAUNCH DRONE TO A SET ALTITUDE, HOVER, THEN LAND
'''


import main, time

def run(target_altitude = 10):
    drone_1 = main.pi_or_sim()
    if target_altitude <= 0 or target_altitude > 20:
        print("Altitude must be within 20 meters")
    else:
        drone_1.guided_arm_takeoff(target_altitude)
        time.sleep(8)
        drone_1.rtl_disarm()


if __name__ == "__main__":
    run()