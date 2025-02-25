import cv2
import mediapipe as mp
import pyautogui
import time
import threading
import pygame

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Frame skipping to reduce lag
frame_count = 0
frame_skip = 3  # Process every 3rd frame
prev_action = None

# Run key presses in a separate thread to avoid delay
def press_key(key):
    pyautogui.press(key)

while cap.isOpened():
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for natural interaction
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if frame_count % frame_skip == 0:
        results = hands.process(rgb_frame)

    action = None  # Store detected action

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger positions
            landmarks = hand_landmarks.landmark
            fingers = []

            # Thumb (special case, check if tip is left of base)
            if landmarks[4].x < landmarks[3].x:
                fingers.append(1)  # Left Gesture
            else:
                fingers.append(0)

            # Other fingers (check if tip is above lower joint)
            for i, tip in zip([8, 12, 16, 20], range(1, 5)):
                fingers.append(1 if landmarks[i].y < landmarks[i - 2].y else 0)

            # Determine action based on finger states
            if fingers == [0, 0, 0, 0, 0]:
                action = "jump"  # Jump (SPACE)
                threading.Thread(target=press_key, args=("space",)).start()

            elif fingers == [1, 0, 0, 0, 0]:
                action = "left"  # Move Left (A)
                threading.Thread(target=press_key, args=("a",)).start()

            elif fingers == [0, 1, 0, 0, 0]:
                action = "right"  # Move Right (D)
                threading.Thread(target=press_key, args=("d",)).start()

            elif fingers == [0, 1, 1, 0, 0]:
                action = "roll"  # Roll (DOWN)
                threading.Thread(target=press_key, args=("down",)).start()

            # Display action on the screen
            cv2.putText(frame, f"Action: {action}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show FPS
    end_time = time.time()
    fps = int(1 / (end_time - start_time))
    cv2.putText(frame, f"FPS: {fps}", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Control for Subway Surfers", frame)
    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
