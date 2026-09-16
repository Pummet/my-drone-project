from pymavlink import mavutil
import time


''' SETTING UP CONNECTION, TELEMETRY READS, BATTERY CHECKS, AND ARM/DISARM READS '''


class Drone_Core():
    def __init__(self, connection_string, baud = None, motors = 4):
        self.connection = connection_string
        self.baud = baud
        self.motors = motors

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
        self.vehicle.mav.request_data_stream_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10,
            0 # stop streaming
        )

        # hasattr check only triggers on Pi, not through TCP on SITL
        if hasattr(self.vehicle, "port") and hasattr(self.vehicle.port, "flush"):
            try:
                self.vehicle.port.flush()
            except Exception as e:
                print(f"Error flushing port: {e}")

        self.vehicle.close()



    def drone_arm(self):
        self.vehicle.arducopter_arm()
        print("Arming...")
        self.vehicle.motors_armed_wait()
        print("Armed!")


    def drone_disarm(self):
        while self.is_armed() is not False:
            altitude = self.get_altitude()

            # Checking if drone is within 20cm of ground
            if altitude < 0.2:
                self.vehicle.arducopter_disarm()
                print("Disarming...")
                self.vehicle.motors_disarmed_wait()
                print("Disarmed!")
                break


    # Returns True if armed, False if not, and None if no message
    def is_armed(self):
        heartbeat_msg = self.vehicle.recv_match(type = "HEARTBEAT", blocking = True, timeout = 2)

        if heartbeat_msg is None:
            print("No heartbeat message received.")
            return None

        elif heartbeat_msg.get_srcSystem() == 1 and heartbeat_msg.get_srcComponent() == 1:
            # base_mode is a bitmask, 128 = armed. Many commands in the same byte, bit 7 is 
            # specifically armed/disarmed. Using bitwise AND to check if bit 7 is set.
            return bool(heartbeat_msg.base_mode & 128)
        

    def drone_takeoff(self, target_altitude):
        self.vehicle.mav.command_long_send( # pymavlink function for sending action commands
            self.vehicle.target_system, # which drone to send it to, important for swarms
            self.vehicle.target_component, # which component on the drone, usually autopilot
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, # MAVLink command ID
            0, 0, 0, 0, 0, 0, 0, # First 0 means send once, next 6 not used for takeoff
            target_altitude
        )

        ack = self.vehicle.recv_match(type = "COMMAND_ACK", blocking = True, timeout = 5)

        if ack is None or ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("Drone launch command not accepted.")
            return
        
        print("Takeoff started.")

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


    # Function to get local NED coordinates from drone, home is (0,0,0)
    def get_position_ned(self):
        while True:
            current_pos = self.vehicle.recv_match(type = "LOCAL_POSITION_NED", blocking = True, timeout = 2)

            if current_pos is None:
                print("No position message received.")
                continue

            return current_pos.x, current_pos.y, current_pos.z  


    def get_position_gps(self):
        pos_msg = self.vehicle.recv_match(type = "GLOBAL_POSITION_INT", blocking = True)

        if pos_msg is None:
            print("No position message received.")
            return None, None, None

        lat = pos_msg.lat / 1e7
        lon = pos_msg.lon / 1e7
        alt = pos_msg.relative_alt / 1000

        return lat, lon, alt   


    # Function that returns drone altitude in meters
    def get_altitude(self):
        alt_msg = self.vehicle.recv_match(type="GLOBAL_POSITION_INT", blocking = True)
        return alt_msg.relative_alt / 1000


    # Function to get battery voltage
    def get_battery_voltage(self):
        batt_msg = self.vehicle.recv_match(type = "BATTERY_STATUS", blocking = True, timeout = 2)

        if batt_msg is None:
            return None
        
        return sum(batt_msg.voltages[:self.motors]) # My drone uses a 4 cell lipo (4S) 


    # Function to check battery voltage and RTL if below threshold
    def check_battery(self, threshold_mv = 14000): # 3.5v/Cell = 14v, need to land, 13.2v damages battery
        voltage = self.get_battery_voltage()

        if voltage is None:
            print("Unable to retrieve battery voltage.")
            return

        elif voltage <= threshold_mv: # 14V is ~3.5V/ cell (4S LiPo)
            self.change_flight_mode("rtl")
            print(f"LOW BATTERY!{voltage}mV, Returning home...")


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

            time.sleep(0.1)


    def distance_to_home(self):
        pass