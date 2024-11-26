#All senstive info are masked
from ultralytics import YOLO
import cv2
import os
from collections import deque
import requests
import base64
from datetime import datetime

model_path = "MASKED"
if not os.path.exists(model_path):
    raise FileNotFoundError("Model file not found.")

model = YOLO(model_path)
print("Classes:", model.names)

video_path = "MASKED"
if not os.path.exists(video_path):
    raise FileNotFoundError("Video file not found.")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video.")
    exit()

video_output_dir = "MASKED"
frame_output_dir = "MASKED"
os.makedirs(video_output_dir, exist_ok=True)
os.makedirs(frame_output_dir, exist_ok=True)

API_KEY = "MASKED"
ENDPOINT = "MASKED"
headers = {"Content-Type": "application/json", "api-key": API_KEY}

TELEGRAM_BOT_TOKEN = "MASKED"
TELEGRAM_CHAT_ID = "MASKED"

def encode_image(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

def send_request(encoded_image, prompt_text):
    payload = {
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{encoded_image}'}},
                    {'type': 'text', 'text': prompt_text}
                ]
            }
        ],
        'temperature': 0.4,
        'top_p': 0.9,
        'max_tokens': 800,
        'stream': False
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def send_telegram_alert(image_path):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = f"⚠️ Alert: Dangerous operation detected at {current_time}."
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as f:
        try:
            response = requests.post(telegram_url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": alert_message}, files={"photo": f})
            response.raise_for_status()
            print("Alert sent.")
        except requests.RequestException as e:
            print(f"Telegram alert failed: {e}")

fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
buffer = deque(maxlen=fps * 5)
recording = False
frame_skip_counter = 0
frame_skip_threshold = 3
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video.")
        break

    buffer.append(frame.copy())
    results = model.predict(source=frame, save=False, show=False, stream=True, conf=0.70, iou=0.45)
    detected_classes = set()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            class_name = model.names[cls]
            if class_name in ["goods", "people"]:
                detected_classes.add(class_name)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0]
            label = f"{class_name} {confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if "people" in detected_classes and "goods" in detected_classes:
        if not recording:
            recording = True
            clip_name = os.path.join(video_output_dir, f"clip_{frame_count}.mp4")
            video_writer = cv2.VideoWriter(clip_name, fourcc, fps, (frame_width, frame_height))
            print(f"Started recording: {clip_name}")
        for buffered_frame in buffer:
            video_writer.write(buffered_frame)
        buffer.clear()
        frame_name = os.path.join(frame_output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_name, frame)
        print(f"Frame saved: {frame_name}")

        if frame_skip_counter == 0:
            encoded_image = encode_image(frame_name)
            prompt_text = "MASKED"  # Prompt text has been replaced with MASKED
            response_json = send_request(encoded_image, prompt_text)
            if response_json:
                api_response = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                print(f"API Response: {api_response}")
                if api_response == "1":
                    send_telegram_alert(frame_name)
                    print("Dangerous operation alert sent.")
            frame_skip_counter = frame_skip_threshold
        else:
            frame_skip_counter -= 1
    elif recording:
        recording = False
        video_writer.release()
        print("Stopped recording.")

    cv2.imshow("YOLO Video Inference", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    frame_count += 1

if recording:
    video_writer.release()
cap.release()
cv2.destroyAllWindows()
