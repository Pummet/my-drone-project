#!/usr/bin/env python3
"""
Quick motor test — spins each motor (1-4) briefly at low throttle
using MAV_CMD_DO_MOTOR_TEST over MAVLink.
"""

from pymavlink import mavutil
import time

# --- Connection settings ---
#   USB on Pi:        '/dev/ttyACM0'
#   TELEM3 UART:      '/dev/ttyAMA0'
#   On Desktop:       'COM8'


connection_string = 'COM8'
baud = 57600

throttle_percent = 10       # 0-100
test_duration_sec = 2       # how long each motor spins
num_motors = 4



def connect():
    # Setting up drone connection
    print(f"Connecting to {connection_string} at {baud} baud...")
    conn = mavutil.mavlink_connection(connection_string, baud = baud)

    conn.wait_heartbeat()
    print(f"Heartbeat received from system {conn.target_system}.")

    return conn



def test_motor(conn, motor_number, throttle_percent, duration_sec):
    print(f"Testing motor {motor_number}, for {duration_sec} seconds at {throttle_percent}% power.")

    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,
        motor_number,
        0,
        throttle_percent,
        duration_sec,
        0,
        0,
        0
    )

    ack = conn.recv_match(type = 'COMMAND_ACK', blocking = True, timeout = 5)

    if ack is None:
        print(f"  No ACK received for motor {motor_number} — check connection.")

    elif ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"  Motor {motor_number} test accepted.")

    else:
        print(f"  Motor {motor_number} test FAILED — result code: {ack.result}")

    time.sleep(2)



def main():
    print("=" * 50)
    print("MOTOR TEST — CONFIRM PROPS ARE OFF")
    print("=" * 50)
    confirm = input("Type 'yes' to confirm props are removed and area is clear: ")

    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return

    conn = connect()

    for motor in range(1, num_motors + 1):
        test_motor(conn, motor, throttle_percent, test_duration_sec)
    


if __name__ == '__main__':
    main()