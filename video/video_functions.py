import cv2 as cv
import mediapipe as mp
import time


mp_hands = mp.solutions.hands # this is the whole Hands module, think of a toolbox, from that I use the tool .Hands

cap = cv.VideoCapture(0) # Camera index

# Was in a WITH block before, but this rebuilds the module every call
# Better outside of the function where it can be built once, but I must manually close it
hands = mp_hands.Hands(max_num_hands = 2, min_detection_confidence = 0.7, min_tracking_confidence = 0.7)

def finger_counter():
    last_count = 0
    streak_length = 0

    print("Waiting for next gesture...")

    while True:
        attempt = 0
        success, frame = cap.read() # returns bool and frame from camera
        current_count = 0

        # Loop to try again if first read fails, breaks when success = True
        while not success and attempt < 5:
            time.sleep(0.1)
            success, frame = cap.read()
            attempt += 1

        # 5 fails triggers this
        if not success:
            print("Failed to read frame")
            cap.release()
            break

        # OCV gives BGR, convert to RGB here for MediaPipe
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # process() runs the hand detection model on the RGB converted frame
        # main thing it returns is multi_hand_landmarks
        # 21 landmark points on each hand
        results = hands.process(rgb)

        # if its found hands, draw landmarks
        if results.multi_hand_landmarks:
            for hand, hand_landmarks in enumerate(results.multi_hand_landmarks):

                which_hand = results.multi_handedness[hand].classification[0].label

                for tip in range(4, 21, 4): # Just hitting tips (4, 8, 12, 16, 20)
                    if tip == 4:
                        # Trying to catch thumbs here, tricky!
                        if which_hand == "Left":
                            if hand_landmarks.landmark[tip].x > hand_landmarks.landmark[tip - 1].x:
                                current_count += 1
                        else:
                            if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                                current_count += 1
                    else:            
                        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                            current_count += 1

            # Checking for 10 frames with the same hand signal in a row, then returning it
            if last_count != current_count:
                last_count = current_count
                streak_length = 1
            else:
                streak_length += 1
            print(f"STREAK: {streak_length}")
            if streak_length > 10:
                return last_count


def release_camera():
    hands.close()
    cap.release()


if __name__ == "__main__":
    finger_counter()