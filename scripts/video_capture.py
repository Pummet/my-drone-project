'''
MOVE THE DRONE IN A CIRCLE PATTERN
'''

import sys, os, time, cv2 as cv

# This is to help import from working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This is a guarded import. PiCamera2 only exists on the Pi, so this
# will stop the program crashing when run on desktop with webcam
try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264encoder
    from picamera2.outputs import FfmpegOutput
    has_pi_camera = True

    encoder = H264Encoder(bitrate = 10000000)
    output = FfmpegOutput("/home/pummet/my-drone-project/video_recordings/video.mp4")

    camera_size = (640, 480)

    if has_pi_camera:
        cap = Picamera2()
    else:
        # DirectShow opens way faster than the default MSMF backend on Windows
        cap = cv.VideoCapture(0, cv.CAP_DSHOW if sys.platform == "win32" else cv.CAP_ANY) # Camera index

    if has_pi_camera:
        video_config = cap.create_video_configuration()
        cap.configure(video_config)

        cap.start()
        cap.start_recording(encoder, output)

        time.sleep(60)

        cap.stop_recording()
        
except ImportError:
    has_pi_camera = False