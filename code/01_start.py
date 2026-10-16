"""Worksheet 1 starter: detect objects in every frame of a video with YOLO.

Run: python 01_start.py      (press q in the image window to quit)
"""
import cv2
from ultralytics import YOLO

SOURCE = "road_03.mp4"          # a video file, or 0 for a webcam
SCALE = 4                       # shrink each frame by this factor

model = YOLO("yolo26n.pt")      # downloaded automatically on first run
cap = cv2.VideoCapture(SOURCE)

while True:
    ret, frame = cap.read()
    if not ret:                 # end of the video, or no camera
        break
    frame = cv2.resize(frame, (frame.shape[1] // SCALE, frame.shape[0] // SCALE))

    results = model(frame, verbose=False)
    view = results[0].plot()    # frame with boxes drawn

    cv2.imshow("Worksheet 1", view)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
