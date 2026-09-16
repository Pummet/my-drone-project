from pymavlink import mavutil
import time



''' WAYPOINT FILE LOADING, AND THE MISSION UPLOAD/EXECUTE/CLEARS FUNCTIONS '''


class Drone_Waypoints():
    # Reads waypoints from a .txt file and returns them as a list of lists
    def load_waypoint(self, path):
        print(f"Loading from: {path}")

        with open(path) as f: # opening file
            next(f) # skips the first line

            waypoints = []

            for line in f: # iterating through line
                values = line.split() # values becomes a list of strings
                command = int(values[3])
                lat = float(values[8])
                lon = float(values[9])
                alt = float(values[10])
                waypoints.append([command, lat, lon, alt]) # waypoints is a list of lists

            print("Waypoints loaded!")

            return waypoints
        

    # Function to upload waypoints list to the drone
    def upload_waypoints(self, waypoints):
        # Drone needs to know how many waypoints
        self.vehicle.mav.mission_count_send(
            self.vehicle.target_system, # which drone
            self.vehicle.target_component, # which component, usually automatic
            len(waypoints), # How many waypoints
            0 # 0 means main mission
        )

        for i, value in enumerate(waypoints):
            command, lat, lon, alt = value # list unpacking

            self.vehicle.mav.mission_item_int_send( # this is the 12 banger .txt wp file
                self.vehicle.target_system,
                self.vehicle.target_component,
                i,                  # sequence number
                3,                  # frame (3 = relative altitude)
                command,            # the command type (rtl, waypoint etc)
                0,                  # current (0 = not current)
                1,                  # autocontinue to next waypoint
                0, 0, 0, 0,         # mission specific params
                int(lat * 1e7),     # lat in degrees * 10mill, converts decimal to precise int
                int(lon * 1e7),     # 50.8219060 becomes 508219060
                alt,                # altitude
                0                   # mission type
            )




    # Auto mode starts to execute loaded mission
    def waypoint_tracker(self):
        print("Mission Started!")
        last_print = 0

        while True:
            miss_prog = self.vehicle.recv_match(type = "MISSION_CURRENT", blocking = True)

            now = time.time()

            # self.check_battery() # Commented out as no battery

            if miss_prog.seq != 0: # Fault when seq and total = 0 as WPs first load

                if miss_prog.seq >= 2 and (now - last_print) >= 2:
                    print(f"Current waypoint: {miss_prog.seq - 1} of {miss_prog.total - 2}")
                    last_print = now

                if miss_prog.seq == miss_prog.total:
                    print("Mission complete! Returning home...")
                    break


    # Function to clear loaded waypoints
    def clear_waypoints(self):
        self.vehicle.mav.mission_clear_all_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            0
        )