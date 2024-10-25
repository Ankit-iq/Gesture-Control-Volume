from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import pyautogui
import os
import threading
import speech_recognition as sr

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


def listen_for_voice_commands():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            print("Listening for commands...")  # Debug statement
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")  # Debug statement

            if "Computer increase volume" in command.lower():
                set_volume(current_volume + 5)
                pyautogui.press("volumeup")
            elif "Computer Decrease volume" in command.lower():
                set_volume(current_volume - 5)
                pyautogui.press("volumedown")
            elif "mute" in command.lower():
                set_volume(0)
                pyautogui.press("volumemute")
            elif "unmute" in command.lower():
                set_volume(50)  # Set to a default volume, or implement a more refined method
                pyautogui.press("volumeup")

        except sr.UnknownValueError:
            print("Could not understand audio")  # Debug statement
        except sr.RequestError as e:
            print(f"Could not request results; {e}")  # Debug statement


if __name__ == '__main__':
    # Start the voice command thread
    voice_thread = threading.Thread(target=listen_for_voice_commands, daemon=True)
    voice_thread.start()

    # Get the port from the environment variable, default to 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")  # Debug statement
    app.run(host='0.0.0.0', port=port)
