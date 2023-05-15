from multiprocessing import Pipe, Queue


def frame_store(qframe):
  from time import time_ns, sleep
  while 1:
    sleep(999999)
    open('./frames/' + str(time_ns()) + '.jpg', 'wb').write(qframe.get())


def frame_collector(clients, qframe):
  from time import time_ns
  from io import BytesIO
  from socket import socket, AF_INET, SOCK_DGRAM
  from collections import deque
  from inference_mtcnn import inference_mtcnn, bytes_to_mat, mat_to_bytes

  class Stats:

    def __init__(self, window=120):
      self._queue = deque(maxlen=window)
      self._prev_ma = None

    def push(self, value):
      self._queue.append(value)
      ma = sum(self._queue) / len(self._queue)
      diff = int(ma - self._prev_ma) if self._prev_ma is not None else None
      self._prev_ma = ma
      ma = int(ma)
      value = int(value)
      print(f"FPS: {value}, MA: {ma}, diff: {diff}")

  SERV_IPV4, SERV_PORT = ('127.0.0.1', 39876)
  PAYLOAD_SIZE = 65536
  udpSock = socket(AF_INET, SOCK_DGRAM)
  udpSock.bind((SERV_IPV4, SERV_PORT))
  isWriting = False
  LOCK_CLNT_ADDR = None
  frameCounted = 0
  t0 = time_ns()
  # LOCK_CLNT_ADDR = ('192.168.145.105',9999)
  try:
    while 1:
      dataRecv, CLNT_ADDR = udpSock.recvfrom(PAYLOAD_SIZE)

      if LOCK_CLNT_ADDR == CLNT_ADDR or True:
        if not isWriting:
          if dataRecv[:2] == b'\xff\xd8':  # Start of JPEG
            isWriting = True
            buf = BytesIO()

        if isWriting:
          buf.write(dataRecv)
          if dataRecv[-2:] == b'\xff\xd9':  # End of JPEG
            tNow = time_ns()
            isWriting = False
            frame = buf.getvalue()

            # inference process
            frame = mat_to_bytes(inference_mtcnn(bytes_to_mat(frame)))

            qframe.put(frame)
            d = dict(clients)  # Make copy into local dict
            if tNow - t0 > 1000000000:
              t0 = tNow
              print('FPS: ', frameCounted, '|', len(clients))
              frameCounted = 0
            else:
              frameCounted += 1
            for handle, sender in d.items():
              try:
                sender.send(frame)
              except:  # Client has gone away?
                del clients[handle]
      else:
        if dataRecv == b'SYN\n':
          udpSock.sendto(b'ACK\n', CLNT_ADDR)
          udpSock.sendto(b'$cam init\n', CLNT_ADDR)
          udpSock.sendto(b'$cam stream\n', CLNT_ADDR)
          LOCK_CLNT_ADDR = CLNT_ADDR
  except KeyboardInterrupt:  # ctrl-C
    pass


def flask_service(clients):
  from flask import Flask, Response
  from time import sleep

  app = Flask(__name__)

  def frame_consumer():
    receiver, sender = Pipe(False)
    clients[sender._handle] = sender
    while True:
      yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + receiver.recv(
      ) + b'\r\n'
      sleep(1 / 13)  # fps limiter

  @app.route('/mjpeg')
  def mjpeg():
    return Response(frame_consumer(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

  @app.route('/')
  def index():
    return """
please go to the <a href="/mjpeg">/mjpeg </a>
    """

  app.run(host='127.0.0.1', threaded=True)


if __name__ == '__main__':
  from multiprocessing import Process, Manager

  with Manager() as manager:
    clients = manager.dict()
    frame = Queue()

    p1 = Process(target=frame_collector, args=(
        clients,
        frame,
    ))
    p2 = Process(target=flask_service, args=(clients,))
    p3 = Process(target=frame_store, args=(frame,))
    p1.start()
    p2.start()
    p3.start()

    try:
      p2.join()  # block while flask_service is running
    except:  # ctrl-C
      p1.terminate()
      p2.terminate()
      p3.terminate()
    finally:
      print('\nEnding up.\n')
