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
    has_pi_camera = True
except ImportError:
    has_pi_camera = False

camera_size = (640, 480)

if has_pi_camera:
    cap = Picamera2()
    cap.configure(cap.create_preview_configuration(main = {"size": camera_size, "format": "RGB888"}))
    cap.start()
else:
    # DirectShow opens way faster than the default MSMF backend on Windows
    cap = cv.VideoCapture(0, cv.CAP_DSHOW if sys.platform == "win32" else cv.CAP_ANY) # Camera index

if has_pi_camera:
    video_config = cap.create_video_configuration()
    cap.configure(video_config)

    cap.start()
    video_path = "/home/pummet/my-drone-project/video_recordings/video.mp4"
    cap.start_recording(video_path)

    time.sleep(60)

    cap.stop_recording()