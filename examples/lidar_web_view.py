"""
Stream lidar data to a web page as a 2D top-down view.

0 degrees = front of the robot (pointing up on screen).

Usage:
    python examples/lidar_web_view.py

Then open http://<robot-ip>:5001 in a browser.
"""

import logging
import math
import threading
import cv2
import numpy as np
from flask import Flask, render_template_string, Response

from rosmaster_lib import Lidar

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

SIZE = 500
CENTER = SIZE // 2
MAX_RANGE = 12000  # mm (12m max)

frame_lock = threading.Lock()
latest_frame = None
current_max_range = 4000  # default visible range, adjustable via slider


def lidar_loop():
    """Continuously read lidar scans and render them."""
    global latest_frame, current_max_range

    lidar = Lidar()
    lidar.connect()

    for scan in lidar.iter_scans():
        max_r = current_max_range
        canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

        # Range rings
        for r_pct in [0.25, 0.5, 0.75, 1.0]:
            r = int(CENTER * r_pct)
            cv2.circle(canvas, (CENTER, CENTER), r, (50, 50, 50), 1)

        # Distance labels
        for r_pct in [0.25, 0.5, 0.75, 1.0]:
            r = int(CENTER * r_pct)
            label = f"{max_r * r_pct / 1000:.1f}m"
            cv2.putText(canvas, label, (CENTER + 3, CENTER - r + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)

        # Front indicator (0 degrees = up)
        cv2.line(canvas, (CENTER, 5), (CENTER, 25), (0, 200, 0), 2)
        cv2.putText(canvas, "FRONT", (CENTER - 22, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 0), 1)

        # Robot center marker
        cv2.circle(canvas, (CENTER, CENTER), 4, (200, 200, 200), -1)

        # Plot points
        for _, angle, dist in scan:
            if dist <= 0 or dist > max_r:
                continue
            rad = math.radians(angle)
            r = int((dist / max_r) * (CENTER - 10))
            x = CENTER + int(r * math.sin(rad))
            y = CENTER - int(r * math.cos(rad))
            # Near = red/orange, far = blue
            ratio = dist / max_r
            red = int(255 * (1 - ratio))
            blue = int(255 * ratio)
            cv2.circle(canvas, (x, y), 2, (blue, 0, red), -1)

        # Info text
        cv2.putText(canvas, f"Points: {len(scan)}  Range: {max_r/1000:.1f}m", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        _, buffer = cv2.imencode(".jpg", canvas, [cv2.IMWRITE_JPEG_QUALITY, 70])
        with frame_lock:
            latest_frame = buffer.tobytes()


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/video")
def video():
    def generate():
        while True:
            with frame_lock:
                frame = latest_frame
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/set_range/<int:range_mm>")
def set_range(range_mm):
    global current_max_range
    current_max_range = max(100, min(range_mm, MAX_RANGE))
    return ("", 204)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Lidar View</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #111; color: #fff; }
        img { width: 500px; height: 500px; border-radius: 6px; margin-top: 10px; }
        .controls { margin: 10px 0; }
        input[type=range] { width: 300px; cursor: pointer; }
        label { font-size: 16px; }
        #rangeLabel { color: #0c0; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Lidar 360&deg; View</h1>
    <p>Front of robot is <span style="color: #0c0">up</span>.</p>
    <div class="controls">
        <label>Range: <span id="rangeLabel">4.0</span>m</label>
        <input type="range" id="rangeSlider" min="1" max="12" value="4" step="0.5"
               oninput="updateRange(this.value)">
    </div>
    <img src="/video">
    <script>
        function updateRange(val) {
            document.getElementById('rangeLabel').textContent = val;
            fetch('/set_range/' + Math.round(val * 1000));
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting lidar stream...")
    threading.Thread(target=lidar_loop, daemon=True).start()

    print("Web server at http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, threaded=True)
