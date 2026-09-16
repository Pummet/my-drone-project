import time, settings



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


    def waypoint_mission(self):
        waypoints = self.load_waypoint(settings.path)
        self.upload_waypoints(waypoints)
        if self.is_armed():
            self.change_flight_mode("auto")
        else:
            print("Drone is not armed")


    def fly_circle(self):
        print("Beginning circle pattern...")
        start_time = time.time()
        duration = 60
        angle_radian = 0.0
        radius = 3
        meters_sec = self.calculate_meters_sec(radius)

        while time.time() - start_time <= duration:
            angle_radian = self.circle_steps(radius, angle_radian, meters_sec)
            time.sleep(0.1)
