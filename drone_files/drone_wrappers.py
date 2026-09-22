import time, settings



''' MULTI STEP SEQUENCES '''


class Drone_Wrappers():

    def guided_arm_takeoff(self, target_altitude = 1.5):
        self.change_flight_mode("guided")
        self.drone_arm()
        time.sleep(1)
        self.drone_takeoff(target_altitude)


    def land_disarm(self):
        self.change_flight_mode("land")
        self.drone_disarm()
        self.close()


    def rtl_disarm(self):
        self.change_flight_mode("rtl")
        self.drone_disarm()
        self.close()


    def waypoint_mission(self):
        waypoints = self.load_waypoint(settings.path)
        self.upload_waypoints(waypoints)

        armed_state = self.armed()
        if armed_state is True:
            self.change_flight_mode("auto")
            self.waypoint_tracker()
        elif armed_state is False:
            print("Drone is not armed")
        else:
            print("Could not confirm arm state, no heartbeat recieved")
