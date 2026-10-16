"""Worksheet 2 starter: show the camera and read BGR / HSV values by clicking.

Run: python 02_start.py      (click = print pixel values, s = save frame, q = quit)
"""
import cv2

SOURCE = 0                      # 0 = USB webcam, or "http://192.168.1.50:8080/video"

cap = cv2.VideoCapture(SOURCE)
frame, hsv = None, None


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and hsv is not None:
        print("x, y =", (x, y), "  BGR =", frame[y, x], "  HSV =", hsv[y, x])


cv2.namedWindow("Worksheet 2")
cv2.setMouseCallback("Worksheet 2", on_click)
saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame: check SOURCE")
        break
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    cv2.imshow("Worksheet 2", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        cv2.imwrite(f"frame_{saved:02d}.png", frame)
        print("saved", f"frame_{saved:02d}.png")
        saved += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
