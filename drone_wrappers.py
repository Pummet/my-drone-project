import time



''' MULTI STEP SEQUENCES '''


class Drone_Wrappers():

    def guided_arm_takeoff(self, target_altitude = 10):
        self.change_flight_mode("guided")
        self.drone_arm()
        time.sleep(1)
        self.drone_takeoff(target_altitude)