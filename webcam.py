import cv2
import time


def main():
  # Open the default webcam
  cap = cv2.VideoCapture(0)

  # Check if the webcam is opened correctly
  if not cap.isOpened():
    print("Cannot open webcam")
    return

  # Get the initial time
  start_time = time.time()
  frame_count = 0

  while True:
    # Read the current frame from the webcam
    ret, frame = cap.read()

    if not ret:
      print("Cannot receive frame. Exiting ...")
      break

    # Display the frame
    cv2.imshow('Webcam', frame)

    # Calculate FPS
    frame_count += 1
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time

    # Display the FPS in the console
    print(f"FPS: {fps:.2f}", end='\r')

    # Press 'q' to exit
    if cv2.waitKey(1) == ord('q'):
      break

  # Release the webcam and close the window
  cap.release()
  cv2.destroyAllWindows()


if __name__ == '__main__':
  main()
