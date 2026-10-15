"""Generate printable test sheets and synthetic images for the worksheets.

Outputs (in data/):
  tray_sheet.pdf / .png     worksheet 4: 4 ArUco markers + 4 x 5 circles for parts
  checkerboard.pdf / .png   worksheet 5: 10 x 7 squares of 25 mm (9 x 6 inner corners)
  motion_strip.pdf          worksheet 3: 10 mm black dots every 50 mm, cut into strips
  04_tray/ok, 04_tray/ng    worksheet 4: 15 + 15 synthetic camera images of the tray

Print the PDFs at 100 % (Actual size), never "Fit to page".

    python scripts/make_sheets.py
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

DPI = 300
PX_PER_MM = DPI / 25.4
A4_LANDSCAPE = (297, 210)           # mm (width, height)

# ---- worksheet 4 tray layout (mm, from the top-left corner of the page) ----
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_MM = 30
MARKER_CENTERS = {0: (30, 30), 1: (267, 30), 2: (267, 180), 3: (30, 180)}   # TL, TR, BR, BL
ROWS, COLS = 4, 5
PITCH_MM = 40
CIRCLE_MM = 25
GRID_CENTER = (148.5, 105)


def cell_centers_mm():
    """Centers of the 4 x 5 circles, row by row."""
    cx0, cy0 = GRID_CENTER
    return [(cx0 + (c - (COLS - 1) / 2) * PITCH_MM, cy0 + (r - (ROWS - 1) / 2) * PITCH_MM)
            for r in range(ROWS) for c in range(COLS)]


def mm(v):
    return int(round(v * PX_PER_MM))


def blank_page():
    w, h = A4_LANDSCAPE
    return np.full((mm(h), mm(w)), 255, np.uint8)


def save(page, name, out):
    cv2.imwrite(str(out / f"{name}.png"), page)
    Image.fromarray(page).save(out / f"{name}.pdf", resolution=DPI)


def label(page, text, xy_mm, size=0.9):
    cv2.putText(page, text, (mm(xy_mm[0]), mm(xy_mm[1])), cv2.FONT_HERSHEY_SIMPLEX,
                size * PX_PER_MM / 4, 0, max(1, mm(0.4)), cv2.LINE_AA)


def tray_sheet():
    page = blank_page()
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    for mid, (cx, cy) in MARKER_CENTERS.items():
        side = mm(MARKER_MM)
        marker = cv2.aruco.generateImageMarker(dictionary, mid, side)
        x0, y0 = mm(cx) - side // 2, mm(cy) - side // 2
        page[y0:y0 + side, x0:x0 + side] = marker
    for i, (cx, cy) in enumerate(cell_centers_mm()):
        cv2.circle(page, (mm(cx), mm(cy)), mm(CIRCLE_MM / 2), 0, max(1, mm(0.3)), cv2.LINE_AA)
        label(page, str(i), (cx - CIRCLE_MM / 2, cy - CIRCLE_MM / 2), 0.6)
    label(page, "CV for Beginners - worksheet 4 tray (print at 100%)", (60, 202))
    return page


def checkerboard(cols=10, rows=7, square_mm=25):
    page = blank_page()
    w, h = A4_LANDSCAPE
    x0, y0 = (w - cols * square_mm) / 2, (h - rows * square_mm) / 2
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                cv2.rectangle(page, (mm(x0 + c * square_mm), mm(y0 + r * square_mm)),
                              (mm(x0 + (c + 1) * square_mm) - 1, mm(y0 + (r + 1) * square_mm) - 1),
                              0, -1)
    label(page, f"checkerboard {cols}x{rows} squares, {square_mm} mm (print at 100%)", (60, 205))
    return page


def motion_strip(dot_mm=10, spacing_mm=50):
    page = blank_page()
    w, h = A4_LANDSCAPE
    for y in (35, 105, 175):                  # three strips per page, cut along the lines
        for x in np.arange(25, w - 10, spacing_mm):
            cv2.circle(page, (mm(x), mm(y)), mm(dot_mm / 2), 0, -1, cv2.LINE_AA)
        cv2.line(page, (0, mm(y + 35)), (mm(w), mm(y + 35)), 160, 1)
    return page


def synthetic_tray(page, missing, stains, rng, scale=0.25):
    """Render the tray as a camera would see it: parts, perspective, blur, noise."""
    img = cv2.cvtColor(page, cv2.COLOR_GRAY2BGR)
    for i, (cx, cy) in enumerate(cell_centers_mm()):
        if i in missing:
            continue
        jitter = rng.normal(0, 1.0, 2)
        center = (mm(cx + jitter[0]), mm(cy + jitter[1]))
        cv2.circle(img, center, mm(11), (60, 70, 80), -1, cv2.LINE_AA)        # a part, 22 mm
        cv2.circle(img, center, mm(4), (120, 130, 140), -1, cv2.LINE_AA)
    for i in stains:                                   # a stain on the tray next to cell i
        cx, cy = cell_centers_mm()[i]
        size, level = rng.uniform(2.0, 5.0), int(rng.uniform(40, 200))
        cv2.ellipse(img, (mm(cx + 15), mm(cy - 9)), (mm(size), mm(size / 2)), 30, 0, 360,
                    (level, level, level), -1, cv2.LINE_AA)
    for _ in range(int(rng.integers(0, 3))):           # harmless dust, on good trays too
        x, y = rng.uniform(50, 250), rng.uniform(40, 175)
        level = int(rng.uniform(185, 225))
        cv2.circle(img, (mm(x), mm(y)), mm(rng.uniform(0.4, 1.0)), (level, level, level), -1)

    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = small.shape[:2]
    out_w, out_h = 960, 720
    margin = rng.uniform(40, 90, (4, 2))
    dst = np.float32([[margin[0, 0], margin[0, 1]],
                      [out_w - margin[1, 0], margin[1, 1]],
                      [out_w - margin[2, 0], out_h - margin[2, 1]],
                      [margin[3, 0], out_h - margin[3, 1]]])
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src, dst)
    view = cv2.warpPerspective(small, M, (out_w, out_h), borderValue=(90, 90, 90))
    gain = rng.uniform(0.85, 1.05)
    view = cv2.GaussianBlur(view, (3, 3), 0).astype(np.float32) * gain
    view += rng.normal(0, 4, view.shape)
    return np.clip(view, 0, 255).astype(np.uint8)


def tray_dataset(page, out, n_ok=15, n_ng=15, seed=4):
    rng = np.random.default_rng(seed)
    n_cells = ROWS * COLS
    for sub in ("ok", "ng"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    for k in range(n_ok):
        cv2.imwrite(str(out / "ok" / f"ok_{k:02d}.jpg"), synthetic_tray(page, set(), set(), rng))
    for k in range(n_ng):
        if k % 3 == 2:          # one part has a stain
            missing, stains = set(), {int(rng.integers(n_cells))}
        else:                   # one or two parts missing
            missing, stains = set(rng.choice(n_cells, int(rng.integers(1, 3)), replace=False).tolist()), set()
        cv2.imwrite(str(out / "ng" / f"ng_{k:02d}.jpg"), synthetic_tray(page, missing, stains, rng))


def main():
    out = Path(__file__).resolve().parent.parent / "data"
    out.mkdir(exist_ok=True)
    tray = tray_sheet()
    save(tray, "tray_sheet", out)
    save(checkerboard(), "checkerboard", out)
    Image.fromarray(motion_strip()).save(out / "motion_strip.pdf", resolution=DPI)
    tray_dataset(tray, out / "04_tray")
    print("written to", out)


if __name__ == "__main__":
    main()
