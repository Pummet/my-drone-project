from pymavlink import mavutil
import time


''' THIS IS DIRECT MAVLINK COMMANDS, ONE ACTION PER MESSAGE'''


class Drone_Commands():
    def change_flight_mode(self, mode):
        mode = mode.upper()

        # Flight modes and numbers are stored in a dictionary
        if mode not in self.vehicle.mode_mapping():
            print(f"Unknown mode: {mode}")
            return

        mode_id = self.vehicle.mode_mapping()[mode]

        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0, # 0 means send once, can spam here but mostly not needed
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, # enter customer ArduPilot modes in next field
            mode_id,
            0, 0, 0, 0, 0 # not used
        )

        ack = self.vehicle.recv_match(type = "COMMAND_ACK", blocking = True, timeout = 5)

        if ack is None or ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"Mode change to {mode} was not accepted")
        else:
            print(f"Flight mode changed to {mode}")


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


    # Function to move the drone to specific GPS coordinates
    def send_coords_gps(self, lat, lon, alt):
        self.change_flight_mode("guided")

        if not self.is_armed():
            print("Drone is not armed. Cannot go to coordinates.")
            return

        self.vehicle.mav.set_position_target_global_int_send(
            0, # send once
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
            0, # time boot ms, not used            
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


    # Function to send yaw controls
    def send_yaw(self, yaw, dir = 0):
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,         # send once
            yaw % 360, # Desired angle (wrap-around)
            200,       # Angle turn per second
            dir,       # Direction: -1 CCW, 0 shortest, 1 CW 
            0,         # Relative offset (0 or 1) 
            0, 0, 0    # Not used
        )


    # Function to send velocity commands
    def send_velocity(self, vel_x, vel_y, vel_z):
        self.vehicle.mav.set_position_target_local_ned_send(
            0, # time boot ms, not used
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