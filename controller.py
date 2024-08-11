import cv2
import mediapipe as mp
import pyfirmata
import time

# Initialize Arduino
board = pyfirmata.Arduino('COM6')
red_led = board.get_pin('d:2:o')  # Pin for red LED
green_led = board.get_pin('d:3:o')  # Pin for green LED

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to check if a point is inside a rectangle
def is_inside(x, y, rect):
    return rect[0] < x < rect[0] + rect[2] and rect[1] < y < rect[1] + rect[3]

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define the box dimensions and position
red_box = (50, 50, 150, 150)  # (x, y, width, height)
green_box = (300, 50, 150, 150)

# Start capturing and processing video
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        
        if not ret:
            break
        
        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        results = hands.process(image_rgb)
        
        # Draw the boxes on the frame
        cv2.rectangle(frame, red_box[:2], (red_box[0] + red_box[2], red_box[1] + red_box[3]), (0, 0, 255), 3)
        cv2.rectangle(frame, green_box[:2], (green_box[0] + green_box[2], green_box[1] + green_box[3]), (0, 255, 0), 3)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract landmark coordinates
                for point in hand_landmarks.landmark:
                    x = int(point.x * frame.shape[1])
                    y = int(point.y * frame.shape[0])
                    
                    # Check if the point is inside the red or green box
                    if is_inside(x, y, red_box):
                        red_led.write(1)  # Turn on the red LED
                        green_led.write(0)
                    elif is_inside(x, y, green_box):
                        green_led.write(1)  # Turn on the green LED
                        red_led.write(0)
                    else:
                        red_led.write(0)
                        green_led.write(0)
                
                # Draw hand landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Display the frame
        cv2.imshow('Hand Tracking', frame)
        
        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
board.exit()
