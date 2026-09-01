from pymavlink import mavutil
import time
import sys

# GIT PULL BEFORE STARTING

# SAVE, then:
# git add .
# git commit -m "describe what changed"
# git push

# Gazebo   gz sim -v4 -r iris_runway.sdf
# SITL     sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -L Brockenhurst
# QGC      ~/Applications/QGroundControl.AppImage

# FRAME_CLASS 1 = Quad
# FRAME_TYPE 1 = X


# self.vehicle     -> pymavlink connection object, high level helper functions
#                     eg. arducopter_arm(), set_mode_apm()
# self.vehicle.mav -> pymavlink raw MAVLink message senders
#                     eg. mission_count_send(), mission_item_int_send()
# self.method_name -> my own methods


class Drone():
    def __init__(self, connection_string, baud = None):
        self.connection = connection_string # TCP is passed in when drone is made
        self.baud = baud
        self.vehicle = mavutil.mavlink_connection(self.connection, baud = self.baud) # Sending TCP connection port to mavlink
        self.vehicle.wait_heartbeat() # waiting for connection confirmation before continuing
        print(f"Heartbeat from system {self.vehicle.target_system}, component {self.vehicle.target_component}")

        self.vehicle.mav.request_data_stream_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10, # 10 Hz
            1   # start streaming
        )



    def mode_guided(self):
        self.vehicle.set_mode_apm("GUIDED")



    def mode_loiter(self):
        self.vehicle.set_mode_apm("LOITER")



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

                if miss_prog.seq >= 2 and (now - last_print) >= 1:
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
        self.vehicle.arducopter_disarm()
        print("Disarming...")
        self.vehicle.motors_disarmed_wait()
        print("Disarmed!")



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



    def upload_mission(self, waypoints):
        self.vehicle.mav.mission_count_send( # need to tell drone how many waypoints first
            self.vehicle.target_system, # which drone
            self.vehicle.target_component, # which component, usually automatic
            len(waypoints),
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



    def get_position(self):
        pos_msg = self.vehicle.recv_match(type = "GLOBAL_POSITION_INT", blocking = True)

        if pos_msg is None:
            print("No position message received.")
            return None, None, None

        lat = pos_msg.lat / 1e7
        lon = pos_msg.lon / 1e7
        alt = pos_msg.relative_alt / 1000

        return lat, lon, alt



    # Function to move the drone to specific coordinates
    def goto_coords(self, lat, lon, alt):
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
            0, 0, 0, 0, 0, 0, 0, 0
        )

        print(f"Moving to - Lat: {lat}, Lon: {lon}, Alt: {alt}m")



    def distance_to_home(self):
        pass



    # Function to check if the drone is armed
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



    # Function to check battery voltage and return to home if below threshold
    def check_battery(self, threshold = 14000): # 3.5v/Cell = 14v, need to land, 13.2v damages battery
        voltage = self.get_battery_voltage()

        if voltage is None:
            print("Unable to retrieve battery voltage.")
            return False

        if voltage <= threshold: # 14V is ~3.5V/ cell (4S LiPo)
            self.mode_rtl()
            print(f"LOW BATTERY!{voltage}mV, Returning home...")
            return True
        
        return False
    


    # Function to get battery voltage
    def get_battery_voltage(self):
        batt_msg = self.vehicle.recv_match(type = "BATTERY_STATUS", blocking = True, timeout = 2)

        if batt_msg is None:
            print("No battery status message received.")
            return None
        
        return sum(batt_msg.voltages[:4]) # I'mDrone using a 4 cell lipo (4S)



    # Function to monitor the drone until it is disarmed
    def monitor_until_disarmed(self):
        disarmed_count = 0 # Intermitten failures due to stale messages

        # Overseer loop to check mission progress, or to force RTL if battery low
        while True:
            armed = self.is_armed()

            if armed == True:
                disarmed_count = 0

            elif armed == False:
                disarmed_count += 1

            if disarmed_count >= 3:
                print("Vehicle Disarmed.")
                break

            # self.check_battery() # Checking battery on each loop



    # Function to clear loaded waypoints
    def clear_mission(self):
        self.vehicle.mav.mission_clear_all_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            0
        )



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
            alt_msg = self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking = True)
            altitude = alt_msg.relative_alt / 1000
            
            now = time.time()

            if now - last_print >= 1:
                print(f"Altitude: {altitude:.1f}m")
                last_print = now
            
            if altitude >= target_altitude * 0.95:
                print("Target altitude reached.")
                break