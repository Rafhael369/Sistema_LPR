from flask import Flask, render_template, Response
import cv2
import os
import queue
import time
import threading

frames = queue.Queue()
app = Flask(__name__)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

def receive(rtsp_cam, id_camera):
    cap = cv2.VideoCapture(rtsp_cam, cv2.CAP_FFMPEG)
    while True:
        conectado = False
        ret, frame = cap.read()
        if ret:
            conectado = True
            try:
                frames.get_nowait()
            except queue.Empty:
                pass
            try:
                frames.put([frame, id_camera])
            except:
                pass

        if conectado == False:
            print("Falha na conexão com o RTSP: " + rtsp_cam)
            print("Tentativa de reconexão em 15 segundos ...")

            time.sleep(15)
            receive(rtsp_cam, id_camera)

def video_stream():
    threading.Thread(target=receive, args=("rtsp://192.168.15.12:8554/", "Camera 1",)).start()
    while True:
        frame = frames.get()
        
        if frame is None:
            break
        
        ret, buffer = cv2.imencode('.jpg', frame[0])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
