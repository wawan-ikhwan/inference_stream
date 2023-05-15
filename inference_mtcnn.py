from PIL import Image, ImageDraw
import cv2
import torch
from facenet_pytorch import MTCNN
import numpy as np

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))
mtcnn = MTCNN(keep_all=True, device=device)


def bytes_to_mat(frame_bytes):
  np_array = np.frombuffer(frame_bytes, np.uint8)
  img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
  return img


def mat_to_bytes(frame_mat, quality=95):
  # Encode the image as a JPEG
  _, encoded_img = cv2.imencode('.jpg', frame_mat,
                                [int(cv2.IMWRITE_JPEG_QUALITY), quality])

  # Convert the encoded image to bytes
  frame_bytes = np.array(encoded_img).tobytes()

  return frame_bytes


def inference_mtcnn(frame):
  # Inference frame here...
  frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

  # Detect faces
  boxes, probs = mtcnn.detect(frame)

  # Draw faces
  frame_draw = frame.copy()
  draw = ImageDraw.Draw(frame_draw)
  if boxes is not None:
    for box, prob in zip(boxes, probs):
      draw.rectangle(box.tolist(), outline=(255, 0, 0), width=6)
      text_position = (box[0], box[1] - 10
                      )  # Position of the text above the box
      draw.text(text_position, f'Prob: {prob:.2f}', fill=(255, 0, 0))

  # Add to frame list
  frame = frame_draw.resize((640, 360), Image.BILINEAR)
  frame = np.array(frame)
  frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

  return frame