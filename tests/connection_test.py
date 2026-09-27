'''
RETURNS HEARTBEAT IF CONNECTED
'''


import main

def run():
    drone = main.pi_or_sim()

    if drone.wait_heartbeat(timeout = 5) is None:
        print("No heartbeat recieved")
    else:
        print(f"Heartbeat received from system {drone.target_system}")

    drone.close()


if __name__ == "__main__":
    run()