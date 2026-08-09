from pymavlink import mavutil

# Gazebo   gz sim -v4 -r iris_runway.sdf
# SITL     sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console -L Brockenhurst
# QGC      ~/Applications/QGroundControl.AppImage

# FRAME_CLASS 1 = Quad
# FRAME_TYPE 1 = X


# testing testing testing
# testing again

class Drone():
    def __init__(self, tcp):
        self.tcp = tcp # TCP is passed in when drone is made
        self.vehicle = mavutil.mavlink_connection(tcp) # Sending TCP connection port to mavlink
        self.vehicle.wait_heartbeat() # waiting for connection confirmation before continuing
        # self.vehicle is for calling pymavlink methods
        # self.mode_guided is for calling my methods

        self.vehicle.mav.request_data_stream_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10, # 10 Hz
            1   # start streaming
        )


    def mode_guided(self):
        self.vehicle.set_mode_apm("GUIDED")


    def mode_auto(self):
        print("Switching to auto...")
        self.vehicle.set_mode_apm("AUTO")


    def mode_rtl(self):
        self.vehicle.set_mode_apm("RTL")


    def mode_stabilize(self):
        self.vehicle.set_mode_apm("STABILIZE")


    def mode_land(self):
        self.vehicle.set_mode_apm("LAND")


    def drone_arm(self):
        self.vehicle.arducopter_arm()
        print("Arming...")
        self.vehicle.motors_armed_wait()
        print("Armed!")


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

        while True:
            alt_msg = self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking = True)

            altitude = alt_msg.relative_alt / 1000
            print(f"Altitude: {altitude:.1f}m")
            
            if altitude >= target_altitude * 0.95:
                print("Target altitude reached")
                break


path = "/home/pummet/Documents/Projects/Drone/missions/daryl_coop.txt"
drone_1 = Drone("tcp:127.0.0.1:5763") # 127.0.0.1 is my pc (local), 5763 is the port opened by ArduPilot
drone_1.mode_guided()
drone_1.drone_arm()
drone_1.drone_takeoff(10)
drone_1.upload_mission(drone_1.load_waypoint(path))
drone_1.mode_auto()




disarmed_count = 0 # Intermitten failures due to stale messages

# Overseer loop to check mission progress, or to force RTL if battery low
while True:
    heartbeat_msg = drone_1.vehicle.recv_match(type = "HEARTBEAT", blocking = True)

    # Sys and Comp 1 is the drone. Filtering out other heartbeats
    if heartbeat_msg.get_srcSystem() == 1 and heartbeat_msg.get_srcComponent() == 1:
        armed = bool(heartbeat_msg.base_mode & 128)
        
    if not armed:
        disarmed_count += 1
    else:
        disarmed_count = 0

    if disarmed_count >= 3:
        print("Mission complete - Vehicle disarmed.")
        break

    batt_msg = drone_1.vehicle.recv_match(type = "SYS_STATUS", blocking = True)

    #if batt_msg.voltage_battery <= 19800:
    #    drone_1.mode_rtl()
    #    print("Battery Low. Emergency RTL")
    #    break

drone_1.clear_mission()