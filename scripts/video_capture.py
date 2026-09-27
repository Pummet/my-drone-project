'''
MOVE THE DRONE IN A CIRCLE PATTERN AND RECORD 
'''

import sys, os, main
from datetime import datetime

# This is a guarded import. PiCamera2 only exists on the Pi, so this
# will stop the program crashing when run on desktop with webcam
try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FfmpegOutput
    has_pi_camera = True
except ImportError as e:
    has_pi_camera = False
    print(f"No PiCamera libraries found: {e}")


def run(has_pi_camera):
    if has_pi_camera:
        # creating path and save file name, names are unique so they don't overwrite
        project_root = os.path.dirname(os.path.dirnam(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        save_dir = os.path.join(project_root, "video_recordings")
        # building path string above, file name below
        filename = datetime.now().strftime("video_%Y%m%d_%H%M%S.mp4")
        path = os.path.join(save_dir, filename)

        camera_size=(640, 480)
            
        cam = Picamera2() # creating the camera object
        cam.configure(cam.create_video_configuration(main = {"size": camera_size})) # configuring the camera for video
        encoder = H264Encoder(bitrate = 10000000) # sets up H.264 encoding at 10Mbps

        cam.start_recording(encoder, FfmpegOutput(path)) # starts recording and writing to path, in mp4 format

        drone_1 = main.pi_or_sim()
        drone_1.guided_arm_takeoff(10)
        drone_1.fly_circle()
        drone_1.rtl_disarm()

        cam.stop_recording()
        cam.close()
    else:
        return


if __name__ == "__main__":
    run()