import cv2 as cv
import mediapipe as mp
import time

# This is a guarded import. PiCamera2 only exists on the Pi, so this
# will stop the program crashing when run on desktop with webcam
try:
    from picamera2 import Picamera2
    has_pi_camera = True
except ImportError:
    has_pi_camera = False


''' HEADLESS FOR DRONE/PI '''


camera_size = (640, 480)

if has_pi_camera:
    cap = Picamera2()
    cap.configure(cap.create_preview_configuration(main = {"size": camera_size, "format": "RGB888"}))
    cap.start()
else:
    cap = cv.VideoCapture(0)   # Camera index
    cap.set(3, camera_size[0]) # 3 = width
    cap.set(4, camera_size[1]) # 4 = height


# this is the whole Hands module, think of a toolbox, from that I use the tool .Hands
mp_hands = mp.solutions.hands

# Was in a WITH block before, but this rebuilds the module every call
# Better outside of the function where it can be built once, but I must manually close it
hands = mp_hands.Hands(max_num_hands = 2, min_detection_confidence = 0.7, min_tracking_confidence = 0.7)


# Wrapper function
def finger_counter():
    print("Waiting for next gesture...")
    last_count = 0
    streak_length = 0

    while True:
        rgb = frame_capture_success()

        if rgb is None:
            break

        # passing converted frame into count_fingers
        current_count = count_fingers(rgb)

        # checking if current frame is same as lost, 15 frames in a row confirmed = True
        last_count, streak_length, confirmed = continuous_capture(current_count, last_count, streak_length)
        
        if confirmed:
            return last_count


# Function to get a frame from either PiCamera or open CV
def get_frame():
    if has_pi_camera:
        try:
            frame = cap.capture_array()
            # returning bool and frame to match output for OpenCV, simplifies rest of code
            return frame is not None, frame
        except Exception:
            return False, None
    else:
        return cap.read() # Returns bool and frame from camera



# Function to confirm that success of a frame grab, converts frame to RGB for and returns for MediaPipe
def frame_capture_success():
    attempt = 0
    success, frame = get_frame() # returns bool and frame from camera

    # Loop to try again if first read fails, skips when success = True
    while not success and attempt < 5:
        time.sleep(0.1)
        success, frame = get_frame()
        attempt += 1

    # 5 fails triggers this
    if not success:
        print("Failed to read frame.")
        release_camera()
        return

    # Flipping frame to make it more intuitive
    frame = cv.flip(frame, 1)
    # OCV gives BGR, convert to RGB for MediaPipe
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    return rgb


# Function that returns the number of extended fingers
def count_fingers(rgb):
    # process() runs the hand detection model on the RGB converted frame
    # main thing it returns is multi_hand_landmarks
    # 21 landmark points on each hand
    results = hands.process(rgb)
    current_count = 0

    if not results.multi_hand_landmarks:
        return current_count
    
    for hand, hand_landmarks in enumerate(results.multi_hand_landmarks):

        # Label is Left or Right hand!
        which_hand = results.multi_handedness[hand].classification[0].label

        hand_orientation = front_back_hand(which_hand, hand_landmarks)

        for tip in range(4, 21, 4): # Just checking fingertips (4, 8, 12, 16, 20)
            if tip == 4:
                # Trying to catch thumbs[4] here, tricky!
                # Thumb is extended if tip is left/right of thumb knuckle depending on hand/orientation
                if which_hand == "Left":
                    if hand_orientation == "front":
                        if hand_landmarks.landmark[tip].x > hand_landmarks.landmark[tip - 1].x:
                            current_count += 1
                    elif hand_orientation == "back":
                        if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                            current_count += 1
                elif which_hand == "Right":
                    if hand_orientation == "front":
                        if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                            current_count += 1
                    elif hand_orientation == "back":
                        if hand_landmarks.landmark[tip].x > hand_landmarks.landmark[tip - 1].x:
                            current_count += 1
            else: # finger is extended if tip is above knuckle
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    current_count += 1

        print(f"Hand: {which_hand}, {hand_orientation}, fingers {current_count}")

    return current_count

    
# Function that checks 15 frames in a row with the same gesture
def continuous_capture(current_count, last_count, streak_length):
    if current_count == 0: # checking 0 to stop confirmation when no hands on frame (0 fingers)
        streak_length = 0
    elif last_count != current_count:
        last_count = current_count
        streak_length = 1
    else:
        streak_length += 1

    confirmed = streak_length >= 15000

    return last_count, streak_length, confirmed


# returns "front" or "back" of hand
def front_back_hand(which_hand, hand_landmarks):
    # Checking x position of thumb knuckle[2] vs pinky knuckle[17] to determine front or back of hand
    if which_hand == "Right":
        if hand_landmarks.landmark[2].x < hand_landmarks.landmark[17].x:
            return "front"
        else:
            return "back"
    else:
        if hand_landmarks.landmark[2].x > hand_landmarks.landmark[17].x:
            return "front"
        else:
            return "back"
    

def release_camera():
    hands.close()
    if has_pi_camera:
        cap.stop()
        cap.close()
    else:
        cap.release()


if __name__ == "__main__":
    finger_counter()