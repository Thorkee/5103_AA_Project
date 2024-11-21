import cv2
from roboflow import Roboflow
import os
import time

# Initialize Roboflow
rf = Roboflow(api_key="mAG26LjDPqjrqmJOBrRs")
project = rf.workspace().project("aae5103-ea3xk")  # Ensure project ID is correct
model = project.version("2").model  # Ensure version number is correct

# Set the custom save directory
save_directory = r"C:\Users\urjr\OneDrive\Document\WeChat Files\wxid_ndawx836w6db11\FileStorage\File\2024-11"
os.makedirs(save_directory, exist_ok=True)

# Open the video file
video_path = r"C:\Users\urjr\Downloads\Screen-2024-11-03-181347(1).mp4"
cap = cv2.VideoCapture(video_path)

# Check if the video file was opened successfully
if not cap.isOpened():
    print(f"Error: Unable to open video file {video_path}")
    exit(1)

# Set the original video FPS and target processing FPS
original_fps = cap.get(cv2.CAP_PROP_FPS)
target_fps = 3  # We want to process at 3 FPS
frame_interval = int(original_fps / target_fps)  # How many frames to skip to achieve 3 FPS

# Define the confidence threshold (sensitivity adjustment)
confidence_threshold = 0.7  # Set to a value between 0 and 1 (e.g., 0.7 for 70%)

frame_count = 0
skip_frames = 0  # Counter to skip the next 10 frames after detection
save_delay = 0  # Counter for delayed saving

# Loop through the video frames
while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("End of video file or failed to grab frame.")
        break

    # Skip frames if needed to process the video at the target FPS
    if frame_count % frame_interval != 0:
        frame_count += 1
        continue

    # If we're waiting to save the frame after detection, decrement the save_delay counter
    if save_delay > 0:
        save_delay -= 1
        if save_delay == 0:
            # Save the frame after 5 frames
            frame_filename = os.path.join(save_directory, f'frame_{frame_count}.jpg')
            cv2.imwrite(frame_filename, frame)
            print(f'Saved frame {frame_count}.jpg after 5-frame delay.')
            
            # After saving, skip the next 10 frames (or pause detection)
            skip_frames = 10  # Skip 10 frames after saving
            print("Pausing detection for 10 frames after saving.")
        frame_count += 1
        continue

    # Skip the next 10 frames after saving
    if skip_frames > 0:
        skip_frames -= 1
        print(f"Skipping frame {frame_count}.")
        frame_count += 1
        continue

    # Use Roboflow model to obtain predictions
    try:
        predictions = model.predict(frame).json()
    except Exception as e:
        print(f"Error during model prediction: {e}")
        break

    people_detected = False
    goods_detected = False

    # Detect people or goods with confidence threshold
    for prediction in predictions.get('predictions', []):
        if prediction['confidence'] >= confidence_threshold:  # Apply confidence threshold
            if prediction['class'] == 'people':
                people_detected = True
            elif prediction['class'] == 'goods':
                goods_detected = True

    # Initiate a 5-frame delay before saving the frame if both people and goods are detected
    if people_detected and goods_detected:
        print(f"Detection at frame {frame_count}: both 'people' and 'goods' detected.")
        
        # Start the countdown to save the frame 5 frames later
        save_delay = 5

    frame_count += 1

    # Optional: Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
print("Video processing completed.")
