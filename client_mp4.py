import cv2
from client import send_frame

filename = 'sample.mp4'
# Create a list to store the image bytes
frames = []

# Open the video file
cap = cv2.VideoCapture(filename)

# Check if the video file opened successfully
if not cap.isOpened():
  print("Error opening video file")
  exit()

# Read frames from the video file
while True:
  # Read the next frame
  ret, frame = cap.read()

  # If no frame is read, break the loop
  if not ret:
    break

  # Implement inference frame here...

  # Convert the frame to MJPEG format
  _, mjpeg = cv2.imencode('.jpg', frame)

  # Convert the MJPEG image to bytes
  frame_bytes = mjpeg.tobytes()

  # Send frame bytes via UDP socket with specified UDP server IP:PORT
  send_frame('127.0.0.1', port=39876, frame=frame_bytes)

# Release the video file
cap.release()