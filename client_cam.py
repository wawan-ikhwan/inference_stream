import cv2
import socket

HOST = '10.1.15.10'
PORT = 39876


def send_frame(server_ip, port, frame: bytes, payload_size=65507):
  # Create a UDP socket
  udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  # Set the socket timeout to 1 second (optional)
  udp_socket.settimeout(1)

  # Calculate the number of packets needed to send the frame
  packet_count = (len(frame) // payload_size) + 1

  # Iterate over the packets and send them
  for i in range(packet_count):
    # Calculate the start and end indices for the current packet
    start_index = i * payload_size
    end_index = min((i + 1) * payload_size, len(frame))

    # Get the current packet data
    packet_data = frame[start_index:end_index]

    # Send the packet to the server
    udp_socket.sendto(packet_data, (server_ip, port))

  # Close the UDP socket
  udp_socket.close()


# Open the default webcam
cap = cv2.VideoCapture(0)

while 1:

  # Capture frame-by-frame
  ret, frame = cap.read()

  # Convert the frame to MJPEG format
  _, mjpeg = cv2.imencode('.jpg', frame)

  # Convert the MJPEG image to bytes
  frame_bytes = mjpeg.tobytes()

  # Send frame bytes via UDP socket with specified UDP server IP:PORT
  send_frame(HOST, port=PORT, frame=frame_bytes)

  # Check if the user pressed the 'q' key to exit
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Release the capture and close the window
cap.release()
cv2.destroyAllWindows()
