import cv2 as cv
import mediapipe as mp
import time


''' FOR TESTING ON COMPUTER WITH WEBCAM - FULL GUI '''


mp_hands = mp.solutions.hands # this is the whole Hands module, think of a toolbox, from that I use the tool .Hands
mp_draw = mp.solutions.drawing_utils # for drawing the connections


cap = cv.VideoCapture(0) # Camera index


# Resolution
cap.set(3, 1200) # 3 = width
cap.set(4, 720)  # 4 = height


def main():
    # loading Hands detection module into memory, then passing each frame into it
    with mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7, # higher confidence is more accurate
    min_tracking_confidence = 0.7
    ) as hands:
        while True:
            attempt = 0
            success, frame = cap.read() # returns bool and frame from camera

            # Loop to try again if first read fails, breaks when success = True
            while not success and attempt < 5:
                time.sleep(0.1)
                success, frame = cap.read()
                attempt += 1

            # 5 fails triggers this
            if not success:
                print("Failed to read frame")
                break

            # Flipping image so more intuitive
            frame = cv.flip(frame, 1)
            h, w, _ = frame.shape
            
            # OCV gives BGR, convert to RGB here for MediaPipe
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            # process() runs the hand detection model on the RGB converted frame
            # main thing it returns is multi_hand_landmarks
            # 21 landmark points on each hand
            results = hands.process(rgb)

            fingers_up = 0
            # if its found hands, draw landmarks
            if results.multi_hand_landmarks:
                for hand, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                        )

                    # Draw labels
                    finger_tips = {
                        "Thumb": hand_landmarks.landmark[4],
                        "Index": hand_landmarks.landmark[8],
                        "Middle": hand_landmarks.landmark[12],
                        "Ring": hand_landmarks.landmark[16],
                        "Pinky": hand_landmarks.landmark[20]
                        }

                    for name, landmark in finger_tips.items():
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv.putText(
                            frame,
                            name,
                            (x, y - 20),
                            cv.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1
                            )

                    # This is for Left or Right hand
                    which_hand = results.multi_handedness[hand].classification[0].label

                    hand_orientation = front_back_hand(which_hand, hand_landmarks)

                    print(f"Hand: {which_hand}, {hand_orientation}")

                    # Counting extended fingers
                    for tip in range(4, 21, 4): # Just hitting fingertips (4, 8, 12, 16, 20)
                        if tip == 4:
                            # Trying to catch thumbs[4] here, tricky!
                            # Thumb is extended if tip is left/right of thumb knuckle depending on hand/orientation
                            if which_hand == "Left":
                                if hand_orientation == "front":
                                    if hand_landmarks.landmark[tip].x > hand_landmarks.landmark[tip - 1].x:
                                        fingers_up += 1
                                elif hand_orientation == "back":
                                    if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                                        fingers_up += 1
                            elif which_hand == "Right":
                                if hand_orientation == "front":
                                    if hand_landmarks.landmark[tip].x < hand_landmarks.landmark[tip - 1].x:
                                        fingers_up += 1
                                elif hand_orientation == "back":
                                    if hand_landmarks.landmark[tip].x > hand_landmarks.landmark[tip - 1].x:
                                        fingers_up += 1
                        else: # finger is extended if tip is above knuckle
                            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                                fingers_up += 1

                print(f"Fingers up: {fingers_up}")

            # Opens windows
            cv.imshow("Frame", frame)

            # Closes on Q press
            if cv.waitKey(1) == ord("q"):
                break

    cap.release()
    cv.destroyAllWindows()


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
        

if __name__ == "__main__":
    main()