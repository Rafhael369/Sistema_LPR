from flask import Flask, render_template, Response
import cv2
import os

app = Flask(__name__)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
camera = cv2.VideoCapture("rtsp://192.168.15.10:8554/", cv2.CAP_FFMPEG)


def video_stream():
    while True:
        success, frame = camera.read()
        if not success:
            continue
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
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
