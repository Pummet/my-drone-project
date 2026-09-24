import time, math



''' SHAPES AND CALCULATIONS, BUILT MY REPEATEDLY SENDING COMMANDS '''


class Drone_Patterns():
    # Jittery, drones starts and stops at every point....
    def fly_circle_terrible(self, radius = 10):
        start_x, start_y, start_z = self.get_position_ned()
        degrees = 0

        if not self.armed():
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


    # Smooth circular movement using vectors
    def circle_steps(self, radius, angle_radian, meters_sec, mirror = False, clockwise = True):
        # Drone faces the centre of the circle as it orbits
        # mirror = False --- centre is north of start
        # mirror = True ---- centre is south of start
        # the circles position is dictated by the velocity calculation
        if not mirror:
            target_yaw = angle_radian * (180 / math.pi)
        else:
            target_yaw = (angle_radian - math.pi) * (180 / math.pi)

        vel_x, vel_y, vel_z = self.calculate_velocity_circle(meters_sec, angle_radian)
        self.send_velocity(vel_x, vel_y, vel_z)
        self.send_yaw(target_yaw)

        angular_velocity = meters_sec / radius

        # movement direction is controlling which circle the drone is on
        # and which way it travels
        if clockwise:
            angle_radian += angular_velocity * 0.1
        else:
            angle_radian -= angular_velocity * 0.1

        # Wrap around radian back to 0.0 or 6.28
        if not mirror and angle_radian > 2 * math.pi:
            angle_radian = 0.0
            
        elif mirror and angle_radian < 0.0:
            angle_radian = 2 * math.pi

        return angle_radian


    def calculate_velocity_circle(self, meters_sec, angle_radian, vel_z = 0.0):
        # x = r * cos(radian) and y = r * sin(radian) gives me a point on the circle from that angle
        # Swapping cos/sin rotates that by 90 degrees and gives me a direction vector,
        # a line just touching the circle perpendicular to the line from the centre
        # sin and cos provide the direction, meters_sec is the speed

        vel_x = meters_sec * math.sin(angle_radian)
        vel_y = -meters_sec * math.cos(angle_radian)

        return vel_x, vel_y, vel_z


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


    def calculate_meters_sec(self, radius):
        # 5m/s over 15m radius circle worked well in sims, good reference point
        # Gives me a good speed per 1m, then multiply by radius
        ref_speed, ref_radius = 5, 15
        meters_sec = (ref_speed / ref_radius) * radius

        if meters_sec > 10: # Capping speed
            meters_sec = 10

        return meters_sec


    # Function for moving in a figure eight. (2 circles, cheat!)
    def fly_figure_eight(self, radius = 3, duration = 60):
        meters_sec = self.calculate_meters_sec(radius)

        start_time = time.time()
        angle_radian = 0.0
        mirror = False

        # Same angle_radian is being passed back and forth, whilst spamming vector commands at 0.1 secs
        # Tracking previous angle to catch the resets in move_circle()
        # when this happens, the drone has completed a full circle and switches to a mirrored circle
        while time.time() - start_time <= duration:
            prev_angle = angle_radian

            if not mirror:
                angle_radian = self.circle_steps(radius, angle_radian, meters_sec)

                if angle_radian < prev_angle:
                        angle_radian = 2 * math.pi # South circle decrements radian
                        mirror = True
            else:
                angle_radian = self.circle_steps(radius, angle_radian, meters_sec, mirror, clockwise = False)

                if angle_radian > prev_angle:
                        angle_radian = 0 # north circle increases radian
                        mirror = False

            time.sleep(0.1)


    # Function to move the drone in a square.
    # Relative to current position
    def fly_square(self, size = 5):
        start_pos = list(self.get_position_ned())

        moves = [(size, 0, 0),(0, size, 0),(-size, 0, 0),(0, -size, 0)]

        full_coords = []

        # List unpacking
        for tar_x, tar_y, tar_z in moves:
            start_pos[0] += tar_x
            start_pos[1] += tar_y
            start_pos[2] += tar_z
            full_coords.append((start_pos[0], start_pos[1], start_pos[2]))

        self.send_and_monitor_position_ned(full_coords, yaw = 90, reps = 5)


    def send_and_monitor_position_ned(self, coords, timeout = None, 
                                      yaw = None, reps = 1, 
                                      position_tolerance = 0.2):

        yaw_change = yaw

        for _ in range(reps):
            for i, (tar_x, tar_y, tar_z) in enumerate(coords):

                self.send_coords_ned(tar_x, tar_y, tar_z)

                if yaw_change is not None:
                    self.send_yaw(yaw_change)
                    yaw_change += yaw

                start_time = time.time()

                while True:
                    if timeout is not None:
                        if time.time() - start_time > timeout:
                            break

                    curr_pos = self.get_position_ned()

                    # curr_pos - target = 0 if positions match
                    # 0.2m tolerance
                    if abs(curr_pos[0] - tar_x) <= position_tolerance and abs(curr_pos[1] - tar_y) <= position_tolerance and abs(curr_pos[2] - tar_z) <= position_tolerance:
                        print(f"point {i + 1} reached")
                        break

                    time.sleep(0.1) # Relax cpu spam
                    

    def fly_spiral_up(self):
        pass