import time



''' MULTI STEP SEQUENCES '''


class Drone_Wrappers():

    def guided_arm_takeoff(self, target_altitude = 2):
        self.change_flight_mode("guided")
        self.drone_arm()
        time.sleep(1)
        self.drone_takeoff(target_altitude)


    def land_disarm(self):
        self.change_flight_mode("land")
        self.drone_disarm()
