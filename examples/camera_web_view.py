"""
Stream RGB and depth to a web page with toggle controls.

RGB uses raw OpenCV for low latency.
Depth is toggled on/off from the web page (initialized on demand).

Usage:
    python examples/camera_web_view.py

Then open http://<robot-ip>:5000 in a browser.
"""

import logging
import threading
import cv2
from flask import Flask, render_template_string, Response, jsonify

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ── RGB (always on, raw OpenCV) ──
rgb_cap = cv2.VideoCapture(0)
rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_lock = threading.Lock()
latest_rgb = None
latest_depth = None

# ── Depth (lazy init, toggled from web) ──
depth_camera = None
depth_on = False
depth_lock = threading.Lock()


def rgb_loop():
    """Continuously read RGB frames."""
    global latest_rgb
    while True:
        ret, frame = rgb_cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        with frame_lock:
            latest_rgb = buffer.tobytes()


def depth_loop():
    """Depth frames, started/stopped by toggle."""
    global latest_depth, depth_camera, depth_on

    while True:
        with depth_lock:
            if not depth_on or depth_camera is None:
                continue
            try:
                depth = depth_camera.get_depth_frame()
            except Exception:
                continue

        if depth is not None:
            from rosmaster_lib import DepthCamera
            filtered = cv2.medianBlur(depth, 5)
            colored = DepthCamera.depth_to_colormap(filtered)
            _, buffer = cv2.imencode(".jpg", colored, [cv2.IMWRITE_JPEG_QUALITY, 60])
            with frame_lock:
                latest_depth = buffer.tobytes()


# ── Routes ───────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/video/rgb")
def video_rgb():
    def generate():
        while True:
            with frame_lock:
                frame = latest_rgb
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video/depth")
def video_depth():
    def generate():
        while True:
            with frame_lock:
                frame = latest_depth
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/toggle/depth")
def toggle_depth():
    global depth_camera, depth_on
    from rosmaster_lib import DepthCamera

    with depth_lock:
        depth_on = not depth_on
        if depth_on:
            try:
                if depth_camera is None:
                    depth_camera = DepthCamera()
                logging.info("Depth ON")
            except Exception as e:
                depth_on = False
                return jsonify({"ok": False, "error": str(e)})
        else:
            if depth_camera:
                try:
                    depth_camera.release()
                except Exception:
                    pass
                depth_camera = None
            with frame_lock:
                latest_depth = None
            logging.info("Depth OFF")

    return jsonify({"ok": True, "on": depth_on})


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Camera Stream</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #111; color: #fff; }
        .streams { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding: 20px; }
        .stream { background: #222; border-radius: 8px; padding: 10px; }
        .stream img { width: 640px; height: 480px; border-radius: 4px; display: block; }
        .stream label { display: block; margin-bottom: 8px; font-size: 18px; }
        .controls { margin: 10px 0; }
        button { padding: 10px 24px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; }
        .btn-off { background: #444; color: #aaa; }
        .btn-on { background: #2a6; color: #fff; }
    </style>
</head>
<body>
    <h1>Robot Camera Stream</h1>
    <div class="controls">
        <button id="depthBtn" class="btn-off" onclick="toggleDepth()">Depth: OFF</button>
    </div>
    <div class="streams">
        <div class="stream">
            <label>RGB</label>
            <img src="/video/rgb">
        </div>
        <div class="stream">
            <label>Depth</label>
            <img src="/video/depth" id="depthFeed">
        </div>
    </div>
    <script>
        function toggleDepth() {
            fetch('/toggle/depth')
                .then(r => r.json())
                .then(d => {
                    const btn = document.getElementById('depthBtn');
                    const feed = document.getElementById('depthFeed');
                    if (d.on) {
                        btn.className = 'btn-on';
                        btn.textContent = 'Depth: ON';
                    } else {
                        btn.className = 'btn-off';
                        btn.textContent = 'Depth: OFF';
                        feed.src = '/video/depth?' + Date.now();
                    }
                });
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting camera stream...")
    threading.Thread(target=rgb_loop, daemon=True).start()
    threading.Thread(target=depth_loop, daemon=True).start()

    print("Web server at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)
