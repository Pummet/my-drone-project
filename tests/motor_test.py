#!/usr/bin/env python3
"""
Quick motor test — spins each motor (1-4) briefly at low throttle
using MAV_CMD_DO_MOTOR_TEST over MAVLink.

!!! SAFETY !!!
- PROPS MUST BE OFF before running this.
- Keep clear of the frame while it's running.
- Have the battery connected (motors need battery power, not just USB).
"""

from pymavlink import mavutil
import time

# --- Connection settings ---
# Update this to match your setup:
#   USB on Pi:        '/dev/ttyACM0'
#   TELEM3 UART:       '/dev/serial0' (or '/dev/ttyAMA0')
#   Baud must match SERIAL5_BAUD if using TELEM3
CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

THROTTLE_PERCENT = 10       # 0-100
TEST_DURATION_SEC = 2       # how long each motor spins
NUM_MOTORS = 4

# MAV_CMD_DO_MOTOR_TEST param meanings:
#   param1: motor instance number (1-based)
#   param2: throttle type (0 = PERCENT)
#   param3: throttle value (0-100 for PERCENT type)
#   param4: timeout in seconds
#   param5: motor count (0 = just this one motor)
#   param6: test order (0 = default/board order)

def connect():
    print(f"Connecting to {CONNECTION_STRING} at {BAUD_RATE} baud...")
    conn = mavutil.mavlink_connection(CONNECTION_STRING, baud=BAUD_RATE)
    conn.wait_heartbeat()
    print(f"Heartbeat received from system {conn.target_system}, component {conn.target_component}")

    # MAV_COMP_ID_AUTOPILOT1 = 1 -- force this explicitly rather than trusting
    # whatever component the heartbeat auto-detection picked, in case something
    # else on the link (GCS, etc.) is being picked up instead of the FC itself.
    if conn.target_component != 1:
        print(f"  WARNING: target_component was {conn.target_component}, forcing to 1 (autopilot)")
        conn.target_component = 1

    # Ask the FC to actually stream SERVO_OUTPUT_RAW to us -- without this
    # request, some setups won't send it at all and get_servo_output() would
    # just time out every time, which looks identical to "PWM isn't moving".
    conn.mav.request_data_stream_send(
        conn.target_system,
        conn.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS,
        10,  # Hz
        1    # start
    )

    return conn


def get_servo_output(conn, timeout=1):
    """Grab the latest SERVO_OUTPUT_RAW message and return servo1-4 raw values."""
    msg = conn.recv_match(type='SERVO_OUTPUT_RAW', blocking=True, timeout=timeout)
    if msg is None:
        return None
    return {
        1: msg.servo1_raw,
        2: msg.servo2_raw,
        3: msg.servo3_raw,
        4: msg.servo4_raw,
    }


def test_motor(conn, motor_number, throttle_percent, duration_sec):
    print(f"Testing motor {motor_number} at {throttle_percent}% for {duration_sec}s...")

    before = get_servo_output(conn)
    print(f"  PWM before: {before}")

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

    ack = conn.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print(f"  No ACK received for motor {motor_number} — check connection.")
    elif ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"  Motor {motor_number} test accepted.")
    else:
        print(f"  Motor {motor_number} test FAILED — result code: {ack.result}")

    # Check PWM output partway through the test window, while it should be spinning
    time.sleep(duration_sec / 2)
    during = get_servo_output(conn)
    print(f"  PWM during: {during}")

    time.sleep(duration_sec / 2 + 0.5)


def main():
    print("=" * 50)
    print("MOTOR TEST — CONFIRM PROPS ARE OFF")
    print("=" * 50)
    confirm = input("Type 'yes' to confirm props are removed and area is clear: ")
    if confirm.strip().lower() != 'yes':
        print("Aborted.")
        return

    conn = connect()

    for motor in range(1, NUM_MOTORS + 1):
        test_motor(conn, motor, THROTTLE_PERCENT, TEST_DURATION_SEC)

    print("Motor test complete.")


if __name__ == '__main__':
    main()