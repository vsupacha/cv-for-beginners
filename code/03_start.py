"""Worksheet 3 starter: camera with locked settings, grayscale image and live histogram.

Run: python 03_start.py      (p = camera settings, s = save frame, q = quit)
"""
import sys

import cv2
import numpy as np

SOURCE = 0                      # 0 = USB webcam, or "http://192.168.1.50:8080/video"

if isinstance(SOURCE, int) and sys.platform == "win32":
    cap = cv2.VideoCapture(SOURCE, cv2.CAP_DSHOW)   # DirectShow can open the settings dialog
else:
    cap = cv2.VideoCapture(SOURCE)


def histogram_image(gray, height=200):
    """Draw the 256-bin histogram of a grayscale image."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    canvas = np.full((height, 256), 255, np.uint8)
    for v in range(256):
        h = int((height - 10) * hist[v] / hist.max())
        cv2.line(canvas, (v, height - 1), (v, height - 1 - h), 0)
    return canvas


saved = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame: check SOURCE")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Worksheet 3", gray)
    cv2.imshow("Histogram", histogram_image(gray))
    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        cap.set(cv2.CAP_PROP_SETTINGS, 1)           # turn off auto exposure / white balance here
    elif key == ord('s'):
        cv2.imwrite(f"light_{saved:02d}.png", frame)
        print("saved", f"light_{saved:02d}.png")
        saved += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
