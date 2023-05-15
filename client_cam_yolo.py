import cv2
from client import send_frame
from yolo import YOLO

yolo = YOLO("models/cross-hands-yolov4-tiny.cfg",
            "models/cross-hands-yolov4-tiny.weights", ["hand"])

# yolo = YOLO("models/cross-hands.cfg", "models/cross-hands.weights", ["hand"])

yolo.size = int(256)
yolo.confidence = float(0.5)

# Open the default webcam
cap = cv2.VideoCapture(0)

while True:
  # Capture frame-by-frame
  ret, frame = cap.read()

  # Inference frame here...
  width, height, inference_time, results = yolo.inference(frame)

  # display fps
  cv2.putText(frame, f'{round(1/inference_time,2)} FPS', (15, 15),
              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

  # sort by confidence
  results.sort(key=lambda x: x[2])

  # how many hands should be shown
  hand_count = len(results)
  if -1 != -1:
    hand_count = int(-1)

  # display hands
  for detection in results[:hand_count]:
    id, name, confidence, x, y, w, h = detection
    cx = x + (w / 2)
    cy = y + (h / 2)

    # draw a bounding box rectangle and label on the image
    color = (0, 255, 255)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    text = "%s (%s)" % (name, round(confidence, 2))
    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color,
                2)

  # Convert the frame to MJPEG format
  _, mjpeg = cv2.imencode('.jpg', frame)

  # Convert the MJPEG image to bytes
  frame_bytes = mjpeg.tobytes()

  # Send frame bytes via UDP socket with specified UDP server IP:PORT
  send_frame('127.0.0.1', port=39876, frame=frame_bytes)

  # Check if the user pressed the 'q' key to exit
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Release the capture and close the window
cap.release()
cv2.destroyAllWindows()
