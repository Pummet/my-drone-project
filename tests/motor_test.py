'''
EXECUTES A BRIEF MOTOR TEST, MOTORS 1 - 4
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import settings



throttle_percent = 10       # 0-100
test_duration_sec = 2       # how long each motor spins


def connect():
    # Setting up drone connection
    print(f"Connecting to {settings.connection_string} at {settings.baud_rate} baud...")
    vehicle = mavutil.mavlink_connection(settings.connection_string, settings.baud_rate)

    vehicle.wait_heartbeat()
    print(f"Heartbeat received from system {vehicle.target_system}.")

    return vehicle



def main():
    print("=" * 50)
    print("MOTOR TEST — CONFIRM PROPS ARE OFF")
    print("=" * 50)

    confirm = input("Type 'yes' to confirm props are removed and area is clear: ")

    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return

    vehicle = connect()

    for motor in range(1, settings.num_motors + 1):
        test_motor(vehicle, motor, throttle_percent, test_duration_sec)

    vehicle.close()



def test_motor(vehicle, motor_number, throttle_percent, duration_sec):
    print(f"Testing motor {motor_number}, for {duration_sec} seconds at {throttle_percent}% power.")

    vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,
        motor_number,
        0,
        throttle_percent,
        duration_sec,
        0,0,0
    )

    ack = vehicle.recv_match(type = 'COMMAND_ACK', blocking = True, timeout = 5)

    if ack is None:
        print(f"  No ACK received for motor {motor_number} — check connection.")

    elif ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"  Motor {motor_number} test accepted.")

    else:
        print(f"  Motor {motor_number} test FAILED — result code: {ack.result}")

    time.sleep(2)
    


if __name__ == '__main__':
    main()