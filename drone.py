from pymavlink import mavutil
import time, math

# GIT PULL BEFORE STARTING

# SAVE, then:
# git add .
# git commit -m "describe what changed"
# git push

# self.vehicle     -> pymavlink connection object, high level helper functions
#                     eg. arducopter_arm(), set_mode_apm()
# self.vehicle.mav -> pymavlink raw MAVLink message senders
#                     eg. mission_count_send(), mission_item_int_send()
# self.method_name -> my own methods


class Drone():
    def __init__(self, connection_string, baud = None):
        self.connection = connection_string
        self.baud = baud
        self.vehicle = mavutil.mavlink_connection(self.connection, baud = self.baud) # Sending connection string to MavLink
        self.vehicle.wait_heartbeat() # waiting for connection confirmation before continuing
        print(f"Heartbeat from system {self.vehicle.target_system}, component {self.vehicle.target_component}")

        # Requesting data from FC
        self.vehicle.mav.request_data_stream_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10, # 10 Hz
            1   # start streaming
        )


    # Closes the connection
    def close(self):
        self.vehicle.close()


    def guided_arm_takeoff(self, target_altitude = 10):
        self.mode_guided()
        self.drone_arm()
        time.sleep(1)
        self.drone_takeoff(target_altitude) 


    def mode_guided(self):
        self.vehicle.set_mode_apm("GUIDED")


    def mode_loiter(self):
        self.vehicle.set_mode_apm("LOITER")


    # Auto mode starts to execute loaded mission
    def mode_auto(self):
        print("Switching to auto...")
        self.vehicle.set_mode_apm("AUTO")
        print("Mission started!")

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


    def mode_land(self):
        self.vehicle.set_mode_apm("LAND")


    def mode_rtl(self):
        self.vehicle.set_mode_apm("RTL")


    def drone_arm(self):
        self.vehicle.arducopter_arm()
        print("Arming...")
        self.vehicle.motors_armed_wait()
        print("Armed!")


    def drone_disarm(self):
        while self.is_armed() is not False:
            altitude = self.get_altitude()

            if altitude < 0.3:
                self.vehicle.arducopter_disarm()
                print("Disarming...")
                self.vehicle.motors_disarmed_wait()
                print("Disarmed!")
                break


    def drone_takeoff(self, target_altitude):

        self.vehicle.mav.command_long_send( # pymavlink function for sending action commands
            self.vehicle.target_system, # which drone to send it to, important for swarms
            self.vehicle.target_component, # which component on the drone, usually autopilot
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, # MAVLink command ID
            0, 0, 0, 0, 0, 0, 0, # First 0 means no confirmation needed, next 6 not used for takeoff
            target_altitude
        )

        last_print = 0

        while True:
            altitude = self.get_altitude()
            
            now = time.time()

            if now - last_print >= 1:
                print(f"Altitude: {altitude:.1f}m")
                last_print = now
            
            if altitude >= target_altitude * 0.95:
                print("Target altitude reached.")
                break


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
    def upload_mission(self, waypoints):
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
                command,            # the command type
                0,                  # current (0 = not current)
                1,                  # autocontinue to next waypoint
                0, 0, 0, 0,         # mission specific params
                int(lat * 1e7),     # lat in degrees * 10mill, converts decimal to precise int
                int(lon * 1e7),     # 50.8219060 becomes 508219060
                alt,                # altitude
                0                   # mission type
            )


    # Function to clear loaded waypoints
    def clear_mission(self):
        self.vehicle.mav.mission_clear_all_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            0
        )


    def get_position_gps(self):
        pos_msg = self.vehicle.recv_match(type = "GLOBAL_POSITION_INT", blocking = True)

        if pos_msg is None:
            print("No position message received.")
            return None, None, None

        lat = pos_msg.lat / 1e7
        lon = pos_msg.lon / 1e7
        alt = pos_msg.relative_alt / 1000

        return lat, lon, alt


    # Function to get local NED coordinates from drone, home is (0,0,0)
    def get_position_ned(self):
        while True:
            current_pos = self.vehicle.recv_match(type = "LOCAL_POSITION_NED", blocking = True, timeout = 2)

            if current_pos is None:
                print("No position message received.")
                continue

            return current_pos.x, current_pos.y, current_pos.z  

     
    # Function that returns drone altitude in meters
    def get_altitude(self):
            alt_msg = self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking = True)
            return alt_msg.relative_alt / 1000

    
    # Function to move the drone to specific GPS coordinates
    def send_coords_gps(self, lat, lon, alt):
        self.mode_guided()

        if not self.is_armed():
            print("Drone is not armed. Cannot go to coordinates.")
            return

        self.vehicle.mav.set_position_target_global_int_send(
            0,
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b0000110111111000, # type mask (only positions enabled)
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0,0,0, # XYZ velocity
            0,0,0, # XYZ Accel force
            0,0    # Yaw, Yaw Rate
        )

        print(f"Moving to - Lat: {lat}, Lon: {lon}, Alt: {alt}m")


    # Function to send local NED coordinates to the drone, this is TRUE NORTH
    # These are relevant to home position (0,0,0) in meters.
    def send_coords_ned(self, north, east, down):
        self.vehicle.mav.set_position_target_local_ned_send(
            0,
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111111000, # position_target_typemask (bitmask)
            north, # X
            east,  # Y
            down,  # Z (Negative is up!)
            0,0,0, # XYZ velocity
            0,0,0, # XYZ Accel force
            0,0    # Yaw, Yaw Rate
        )


    def distance_to_home(self):
        pass


    # Returns True if armed, False if not, and None if no message
    def is_armed(self):

        while True:
            heartbeat_msg = self.vehicle.recv_match(type = "HEARTBEAT", blocking = True, timeout = 2)

            if heartbeat_msg is None:
                print("No heartbeat message received.")
                return None

            if heartbeat_msg.get_srcSystem() == 1 and heartbeat_msg.get_srcComponent() == 1:
                # base_mode is a bitmask, 128 = armed, 0 = disarmed. Many commands in the same byte, bit 7 is 
                # specifically armed/disarmed. Using bitwise AND to check if bit 7 is set.
                return bool(heartbeat_msg.base_mode & 128)
        

    # Jittery, drones starts and stops at every point....
    def move_circle(self, radius = 10):
        start_x, start_y, start_z = self.get_position_ned()
        degrees = 0

        if not self.is_armed():
            print("Drone is not armed. Cannot move in a circle.")
            return

        else:
            coords = []
            # Plotting points around a circle
            while degrees <= 360:
                angle_radian = math.radians(degrees)
                x = start_x + radius * math.cos(angle_radian)
                y = start_y + radius * math.sin(angle_radian)
                z = start_z + 0
                coords.append((x, y, z))
                degrees += 10

            self.send_and_monitor_position_ned(coords)


    # Function that constantly sends velocity commands resulting in a circle
    def move_circle_velocity(self, radius = 20, duration = 100, meters_sec = 5):
        start_time = time.time()

        # math.sin and cos expects radian input
        angle_radian = 0.0
        angular_velocity = meters_sec / radius

        while time.time() - start_time <= duration:

            # x = r * cos(radian) and y = r * sin(radian) gives me a point on the circle from that angle
            # Swapping cos/sin rotates that by 90 degrees and gives me a direction vector
            # a line just touching the circle perpendicular to the line from the centre
            # sin and cos provide the direction, meters_sec is the speed
            vel_x = meters_sec * math.sin(angle_radian)
            vel_y = -meters_sec * math.cos(angle_radian)
            vel_z = 0.0 # Maintain altitude
            # Inverting x or y here dictates CW or CCW motion around the circle

            self.vehicle.mav.set_position_target_local_ned_send(
                0,
                self.vehicle.target_system,
                self.vehicle.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                0b0000011111000111, # Bitmask, only velocity is read
                0, 0, 0, # XYZ Position
                vel_x,
                vel_y,
                vel_z,
                0, 0, 0, # XYZ Acceleration
                0, 0 # Yaw and Yaw Rate
            )

            time.sleep(0.1)

            angle_radian += angular_velocity * 0.1

            # Wrap around radian back to 0.0
            if angle_radian > 2 * math.pi:
                angle_radian = 0.0


    # Function to move the drone in a square.
    # Relative to current position
    def move_square(self, size = 10):
        start_x, start_y, start_z = self.get_position_ned()

        moves = [(size, 0, 0),(0, size, 0),(-size, 0, 0),(0, -size, 0)]

        full_coords = []

        # List unpacking
        for tar_x, tar_y, tar_z in moves:
            start_x += tar_x
            start_y += tar_y
            start_z += tar_z
            full_coords.append((start_x, start_y, start_z))

        self.send_and_monitor_position_ned(full_coords, yaw = 90)

    
    def send_and_monitor_position_ned(self, coords, timeout = None, yaw = None):
        initial_yaw = yaw

        for i, (tar_x, tar_y, tar_z) in enumerate(coords):

            self.send_coords_ned(tar_x, tar_y, tar_z)

            if initial_yaw is not None:
                self.set_yaw(initial_yaw)
                initial_yaw += yaw

            start_time = time.time()

            while True:
                if timeout is not None:
                    if time.time() - start_time > timeout:
                        break

                curr_x, curr_y, curr_z = self.get_position_ned()

                # curr_pos - target = 0 if positions match

                if abs(curr_x - tar_x) <= 0.2 and abs(curr_y - tar_y) <= 0.2 and abs(curr_z - tar_z) <= 0.2:
                    print(f"point {i + 1} reached")
                    break

                time.sleep(0.1) # Relax cpu spam


    def set_yaw(self, yaw):
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,       # No confirmation needed
            yaw % 360,     # Desired angle
            20,      # Angle turn per second
            0,       # Direction: -1 CCW, 0 shortest, 1 CW 
            0,       # Relative offset (0 or 1) 
            0, 0, 0  # Not used
        )


    # Function to check battery voltage and RTL if below threshold
    def check_battery(self, threshold = 14000): # 3.5v/Cell = 14v, need to land, 13.2v damages battery
        voltage = self.get_battery_voltage()

        if voltage is None:
            print("Unable to retrieve battery voltage.")
            return

        elif voltage <= threshold: # 14V is ~3.5V/ cell (4S LiPo)
            self.mode_rtl()
            print(f"LOW BATTERY!{voltage}mV, Returning home...")
    

    # Function to get battery voltage
    def get_battery_voltage(self):
        batt_msg = self.vehicle.recv_match(type = "BATTERY_STATUS", blocking = True, timeout = 2)

        if batt_msg is None:
            return None
        
        return sum(batt_msg.voltages[:4]) # My drone uses a 4 cell lipo (4S)


    # Function to monitor the drone until it is disarmed
    def monitor_until_disarmed(self):
        disarmed_count = 0 # Intermitten failures due to stale messages

        while True:
            armed = self.is_armed()

            if armed == True:
                disarmed_count = 0

            elif armed == False:
                disarmed_count += 1

            if disarmed_count >= 3:
                print("Vehicle Disarmed.")
                break