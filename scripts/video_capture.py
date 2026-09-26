'''
MOVE THE DRONE IN A CIRCLE PATTERN
'''

import sys, os, time

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    

    cap = Picamera2()
    encoder = H264Encoder(bitrate = 10000000)
    output = FfmpegOutput("/home/pummet/my-drone-project/video_recordings/video.mp4")

    camera_size = (640, 480)

    video_config = cap.create_video_configuration()
    cap.configure(video_config)
    print("start record")
    cap.start()
    cap.start_recording(encoder, output)

    time.sleep(60)

    cap.stop_recording()
    print("recording finished")