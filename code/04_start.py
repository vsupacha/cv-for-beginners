"""Worksheet 4 starter: find the tray by its 4 ArUco markers and show the top view.

Run: python 04_start.py      (s = save top view, q = quit)
"""
import cv2
import numpy as np

SOURCE = "data/04_tray/ok/ok_00.jpg"     # an image file, or 0 for a webcam

S = 2                                    # pixel per mm in the top view
MARKER_MM = {0: (30, 30), 1: (267, 30), 2: (267, 180), 3: (30, 180)}   # marker centers (mm)
W, H = (267 - 30) * S, (180 - 30) * S    # top view size (pixel)
CELLS_MM = [(148.5 + (c - 2) * 40, 105 + (r - 1.5) * 40) for r in range(4) for c in range(5)]
CELLS = [(int((x - 30) * S), int((y - 30) * S)) for x, y in CELLS_MM]

detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50))


def top_view(img):
    """Warp the tray to a top view, or return None if a marker is missing."""
    corners, ids, _ = detector.detectMarkers(img)
    if ids is None:
        return None
    found = {int(i): c[0].mean(axis=0) for i, c in zip(ids.ravel(), corners)}
    if not all(k in found for k in MARKER_MM):
        return None
    src = np.float32([found[k] for k in range(4)])
    dst = np.float32([((x - 30) * S, (y - 30) * S) for x, y in (MARKER_MM[k] for k in range(4))])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (W, H))


is_image = isinstance(SOURCE, str) and SOURCE.lower().endswith((".jpg", ".png"))
cap = None if is_image else cv2.VideoCapture(SOURCE)

while True:
    if is_image:
        frame = cv2.imread(SOURCE)
    else:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame: check SOURCE")
            break

    top = top_view(frame)
    if top is None:
        view = frame.copy()
        cv2.putText(view, "need all 4 markers", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        view = top.copy()
        for i, (cx, cy) in enumerate(CELLS):
            cv2.circle(view, (cx, cy), 9 * S, (0, 0, 255), 2)
            cv2.putText(view, str(i), (cx - 8, cy + 6), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 0, 255), 2)

    cv2.imshow("Worksheet 4", view)
    key = cv2.waitKey(30) & 0xFF
    if key == ord('s') and top is not None:
        cv2.imwrite("top_view.png", top)
        print("saved top_view.png")
    elif key == ord('q'):
        break

if cap is not None:
    cap.release()
cv2.destroyAllWindows()
