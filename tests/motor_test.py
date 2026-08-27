# Motor Test, spins each motor for 2 seconds.
# Uses MAV_CMD_DO_MOTOR_TEST

from pymavlink import mavutil
import time

connection_string = "/dev/ttyAMA0"
baud_rate = 57600 # Set in QGroundControl parameters

throttle_percent = 10
test_duration_secs = 2
num_motors = 4



def connect():
    connection = mavutil.mavlink_connection(connection_string, baud = baud_rate)
    connection.wait_heartbeat()
    print(f"Heartbeat from system {connection.target_system}")

    return connection



def test_motor(connection, motor_number, throttle_percent, test_duration_secs):
    print(f"Testing motor {motor_number} at {throttle_percent}% throttle for {test_duration_secs} seconds...")

    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,  # Confirmation
        motor_number,  # Motor number (1-4)
        throttle_percent,  # Throttle percentage
        test_duration_secs,  # Test duration in seconds
        0, 0, 0, 0  # Unused parameters
    )

    ack = connection.recv_match(type='COMMAND_ACK', blocking = True, timeout = 5)

    if ack is None:
        print(f"No ACK recieved for motor {motor_number}. Check Connection")

    elif ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"Motor {motor_number} test command accepted.")

    else:
        print(f"Motor {motor_number} test command failed with result: {ack.result}")

    time.sleep(test_duration_secs + 1) # Pause between each motor



def __main__():
    print("=" * 50)
    print("MOTOR TEST - CONFIRM PROPS ARE OFF")
    print("=" * 50)
    start = input("Type 'yes' to confirm props are removed and area is clear: ")

    if start.strip().lower() != "yes":
        print("Test Cancelled")
        return

    connection = connect()

    for motor in range(1, num_motors + 1):
        test_motor(connection, motor, throttle_percent, test_duration_secs)

    print("Motor test complete.")



if __name__ == "__main__":
    __main__()