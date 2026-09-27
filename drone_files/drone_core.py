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
        print(f"Heartbeat recieved, connection successful!")

        # Requesting data from FC
        self.vehicle.mav.request_data_stream_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            6, # 6 Hz
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

        # hasattr check only triggers on Pi, not through TCP on SITL(Desktop)
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
        while self.armed() is not False:
            altitude = self.get_altitude()

            # Checking if drone is within 20cm of ground
            if altitude < 0.2:
                self.vehicle.arducopter_disarm()
                print("Disarming...")
                self.vehicle.motors_disarmed_wait()
                print("Disarmed!")
                break


    # Returns True if armed, False if not, and None if no message
    def armed(self):
        heartbeat_msg = self.get_latest_message("HEARTBEAT")

        if heartbeat_msg.get_srcSystem() == 1 and heartbeat_msg.get_srcComponent() == 1:
            # base_mode is a bitmask, 128 = armed. Many commands in the same byte, bit 7 is
            # specifically armed/disarmed. Using bitwise AND to check if bit 7 is set.
            return bool(heartbeat_msg.base_mode & 128)
        else:
            print("No heartbeat message received.")
            return None
        

    # struggling with the message buffer, too many messages building up and functions
    # not reading the most recent one. Found this solution, which reads everything in the buffer.
    # vehicle.messages holds the most recently read message of each message type, therefore it will
    # hold the most recent and i can query it directly (its a dictionary)
    # need to be careful as this drains ACKs as well.
    def drain_messages(self):
        while self.vehicle.recv_msg() is not None:
            pass


    # function that gets the most recent message of a specified type
    def get_latest_message(self, msg_type, max_age = 1.0, timeout = 5):
        self.drain_messages()
        msg = self.vehicle.messages.get(msg_type)

        # _timestamp is the device time that pymavlink recieved the message
        if msg is not None and time.time() - msg._timestamp < max_age:
            return msg

        # if nothing, wait 5 seconds for a new one
        return self.vehicle.recv_match(type = msg_type, blocking = True, timeout = timeout)



    # Function to get local NED coordinates from drone, home is (0,0,0)
    def get_position_ned(self):
        while True:
            ned_msg = self.get_latest_message("LOCAL_POSITION_NED")

            if ned_msg is None:
                print("No position message received.")
                continue

            return ned_msg.x, ned_msg.y, ned_msg.z  


    def get_position_gps(self):
        gps_msg = self.get_latest_message("GLOBAL_POSITION_INT")

        if gps_msg is None:
            print("No position message received.")
            return None, None, None

        lat = gps_msg.lat / 1e7
        lon = gps_msg.lon / 1e7
        alt = gps_msg.relative_alt / 1000

        return lat, lon, alt   


    # Function that returns drone altitude in meters
    def get_altitude(self):
        alt_msg = self.get_latest_message("GLOBAL_POSITION_INT")

        if alt_msg is None:
            print("No altitude message recieved. RTL")
            return None
        
        return alt_msg.relative_alt / 1000


    # Function to get battery voltage
    def get_battery_voltage(self):
        batt_msg = self.get_latest_message("BATTERY_STATUS")

        if batt_msg is None:
            return
        
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
            armed = self.armed()

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