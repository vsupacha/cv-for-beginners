"""Worksheet 5 starter: show the camera and find the checkerboard corners live.

Run: python 05_start.py      (s = save frame, q = quit)
"""
import sys

import cv2

SOURCE = 0                      # 0 = USB webcam, or "http://192.168.1.50:8080/video"
PATTERN = (9, 6)                # inner corners of data/checkerboard.pdf (columns, rows)
SQUARE = 25.0                   # mm

if isinstance(SOURCE, int) and sys.platform == "win32":
    cap = cv2.VideoCapture(SOURCE, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(SOURCE)

saved = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame: check SOURCE")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, PATTERN)

    view = frame.copy()
    if found:
        cv2.drawChessboardCorners(view, PATTERN, corners, found)
    cv2.putText(view, "board found" if found else "board not found", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0) if found else (0, 0, 255), 2)

    cv2.imshow("Worksheet 5", view)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        cv2.imwrite(f"board_{saved:02d}.png", frame)
        print("saved", f"board_{saved:02d}.png")
        saved += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
