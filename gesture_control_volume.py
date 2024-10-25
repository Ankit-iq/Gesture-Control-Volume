from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import pyautogui
import os

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils

# Initial volume level
current_volume = 50  # Initialize volume at 50%

def set_volume(volume):
    global current_volume
    current_volume = volume

def get_volume():
    return current_volume

def gen_frames():
    webcam = cv2.VideoCapture(0)
    global current_volume
    while True:
        success, frame = webcam.read()
        if not success:
            break

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect hands
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the coordinates for volume control
                landmarks = hand_landmarks.landmark
                x1 = int(landmarks[8].x * frame.shape[1])
                y1 = int(landmarks[8].y * frame.shape[0])
                x2 = int(landmarks[4].x * frame.shape[1])
                y2 = int(landmarks[4].y * frame.shape[0])
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 4

                # Control volume based on hand gestures
                if dist > 15:
                    set_volume(current_volume + 5)  # Increase volume
                    pyautogui.press("volumeup")
                elif dist == 0:
                    set_volume(0)  # Mute volume
                    pyautogui.press("volumemute")
                else:
                    set_volume(current_volume - 5)  # Decrease volume
                    pyautogui.press("volumedown")

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Return the encoded frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/volume')
def volume():
    return jsonify(volume=get_volume())

if __name__ == '__main__':
    # Get the port from the environment variable, default to 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")  # Debug statement
    app.run(host='0.0.0.0', port=port)
