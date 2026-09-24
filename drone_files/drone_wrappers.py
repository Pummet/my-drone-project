import time, settings



''' MULTI STEP SEQUENCES '''


class Drone_Wrappers():

    def guided_arm_takeoff(self, target_altitude = 1.5):
        if self.change_flight_mode("guided"):
            return False
        
        self.drone_arm()
        time.sleep(1)
        
        if not self.drone_takeoff(target_altitude):
            self.drone_disarm()
            return False

        return True


    def land_disarm(self):
        for attempt in range(3):
            if self.change_flight_mode("land"):
                self.drone_disarm()
                self.close()
                return True
            
        print("LAND failed after 3 attempts, TAKE MANUAL CONTROL!\n" * 5)
        return False


    def rtl_disarm(self):
        for attempt in range(3):
            if self.change_flight_mode("rtl"):
                self.drone_disarm()
                self.close()
                return True

        # RTL can fail due to no GPS lock
        print("RTL failed, falling back to LAND.")
        self.land_disarm()


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
