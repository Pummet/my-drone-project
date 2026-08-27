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

connection_string = '/dev/ttyAMA0'
baud = 57600

throttle_percent = 10       # 0-100
test_duration_sec = 2       # how long each motor spins
num_motors = 4



def connect():
    print(f"Connecting to {connection_string} at {baud} baud...")
    conn = mavutil.mavlink_connection(connection_string, baud = baud)

    conn.wait_heartbeat()
    print(f"Heartbeat received from system {conn.target_system}.")

    # MAV_COMP_ID_AUTOPILOT1 = 1 -- force this explicitly rather than trusting
    # whatever component the heartbeat auto-detection picked, in case something
    # else on the link (GCS, etc.) is being picked up instead of the FC itself.
    if conn.target_component != 1:
        print(f"  WARNING: target_component was {conn.target_component}, forcing to 1 (autopilot)")
        conn.target_component = 1

    return conn



def test_motor(conn, motor_number, throttle_percent, duration_sec):
    print(f"Testing motor {motor_number} at {throttle_percent}% for {duration_sec}s...")

    conn.mav.command_long_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,                      # confirmation
        motor_number,           # param1: motor instance
        0,                      # param2: throttle type (0 = percent)
        throttle_percent,       # param3: throttle value
        duration_sec,           # param4: timeout (s)
        0,                      # param5: motor count (0 = single motor)
        0,                      # param6: test order
        0                       # param7: empty
    )

    ack = conn.recv_match(type = 'COMMAND_ACK', blocking = True, timeout = 5)

    if ack is None:
        print(f"  No ACK received for motor {motor_number} — check connection.")

    elif ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"  Motor {motor_number} test accepted.")

    else:
        print(f"  Motor {motor_number} test FAILED — result code: {ack.result}")

    time.sleep(4)



def main():
    print("=" * 50)
    print("MOTOR TEST — CONFIRM PROPS ARE OFF")
    print("=" * 50)
    confirm = input("Type 'yes' to confirm props are removed and area is clear: ")

    if confirm.strip().lower() != 'yes':
        print("Aborted.")
        return

    conn = connect()

    for motor in range(1, num_motors + 1):
        test_motor(conn, motor, throttle_percent, test_duration_sec)

    print("Motor test complete.")


if __name__ == '__main__':
    main()