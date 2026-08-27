from pymavlink import mavutil

vehicle = mavutil.mavlink_connection("/dev/ttyAMA0", baud = 57600)

vehicle.wait_heartbeat()

print(f"Heartbeat received from system {vehicle.target_system}")