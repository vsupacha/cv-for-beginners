"""Lab 6: make the A4 test sheets (A, B, C) and the instructor answer key.

Usage: python scripts/make_sheets_02.py
Output: data/test_sheets_02.pdf (print in color at 100% / Actual size)
        data/test_sheets_02_key.pdf (instructor only, not committed)
"""
import math
import random
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT_DIR = Path(__file__).resolve().parent.parent / "data"
PAGE_W, PAGE_H = 297, 210          # landscape A4 (mm)
MARGIN = 15                         # keep clear of the printer's unprintable edge

# reportlab does not position Thai marks (no GPOS), so use a font with the
# Windows Thai PUA glyphs and pick the shifted forms ourselves (thai_pua)
FONT_DIR = Path.home() / "AppData/Local/Microsoft/Windows/Fonts"
pdfmetrics.registerFont(TTFont("Sarabun", str(FONT_DIR / "THSarabunNew.ttf")))
pdfmetrics.registerFont(TTFont("SarabunB", str(FONT_DIR / "THSarabunNew Bold.ttf")))
FONT_SCALE = 1.45                   # TH Sarabun is small for its point size

TALL = set("ปฝฟฬ")
UPPER = set("ัิีึื็ํ")
TONE = "่้๊๋์"
UPPER_LEFT = dict(zip("ิีึืัํ็",
                      ""))


def thai_pua(text):
    """Replace Thai marks by the Windows PUA glyphs that are already shifted."""
    out, base = [], ""
    for ch in text:
        prev = out[-1] if out else ""
        if ch in TONE:
            i = TONE.index(ch)
            if prev in UPPER or prev in UPPER_LEFT.values():
                ch = chr(0xF713 + i) if base in TALL else ch         # high (above vowel)
            else:
                ch = chr(0xF705 + i) if base in TALL else chr(0xF70A + i)   # low
        elif ch in UPPER and base in TALL:
            ch = UPPER_LEFT[ch]
        elif ch in "ฺุู" and base in "ฎฏ":
            ch = chr(0xF718 + "ฺุู".index(ch))
        elif "ก" <= ch <= "ฮ":
            base = ch
        out.append(ch)
    return "".join(out)


class Canvas(canvas.Canvas):
    """Canvas that maps Thai/ThaiB to TH Sarabun and fixes the Thai marks."""

    def setFont(self, name, size, leading=None):
        name = {"Thai": "Sarabun", "ThaiB": "SarabunB"}.get(name, name)
        super().setFont(name, size * FONT_SCALE, leading)

    def drawString(self, x, y, text, *args, **kw):
        super().drawString(x, y, thai_pua(text), *args, **kw)

    def drawCentredString(self, x, y, text, *args, **kw):
        super().drawCentredString(x, y, thai_pua(text), *args, **kw)

# saturated colors that survive CMYK printing; H (OpenCV 0-179) ~ 178, 72, 109
COLOR_RGB = {
    "red":   (0.86, 0.08, 0.12),
    "green": (0.00, 0.60, 0.26),
    "blue":  (0.05, 0.30, 0.76),
}
COLOR_TH = {"red": "แดง", "green": "เขียว", "blue": "น้ำเงิน"}
SHAPE_TH = {"circle": "วงกลม", "square": "สี่เหลี่ยม", "triangle": "สามเหลี่ยม"}


# ---------------------------------------------------------------- geometry
def polygon(shape, cx, cy, size, angle=0.0):
    """Vertices (mm) of a square (side = size) or equilateral triangle (side = size)."""
    if shape == "square":
        r, n, a0 = size / math.sqrt(2), 4, math.pi / 4
    else:
        r, n, a0 = size / math.sqrt(3), 3, math.pi / 2
    a0 += math.radians(angle)
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n),
             cy + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def radius(shape, size):
    """Circumscribed radius (mm), used for spacing."""
    return {"circle": size / 2, "square": size / math.sqrt(2),
            "triangle": size / math.sqrt(3)}[shape]


def draw_piece(c, p, s=1.0, ox=0.0, oy=0.0):
    """Draw one piece; s/ox/oy scale and shift it (for the thumbnails in the key)."""
    c.setFillColorRGB(*COLOR_RGB[p["color"]])
    c.setStrokeColorRGB(*COLOR_RGB[p["color"]])
    if p["shape"] == "circle":
        c.circle((ox + s * p["x"]) * mm, (oy + s * p["y"]) * mm,
                 s * p["size"] / 2 * mm, stroke=0, fill=1)
        return
    pts = polygon(p["shape"], p["x"], p["y"], p["size"], p.get("angle", 0))
    path = c.beginPath()
    path.moveTo((ox + s * pts[0][0]) * mm, (oy + s * pts[0][1]) * mm)
    for x, y in pts[1:]:
        path.lineTo((ox + s * x) * mm, (oy + s * y) * mm)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def piece(pid, color, shape, x, y, size, angle=0.0):
    return dict(id=pid, color=color, shape=shape, x=x, y=y, size=size, angle=angle)


# ---------------------------------------------------------------- sheets
def sheet_a():
    """3 colors x 3 shapes in a grid, one size per row (for HSV, shape and size)."""
    sizes = {"red": 30, "green": 35, "blue": 40}
    rows_y = {"red": 162, "green": 116, "blue": 66}
    cols_x = {"circle": 55, "square": 125, "triangle": 195}
    pieces, n = [], 1
    for color in COLOR_RGB:
        for shape in cols_x:
            y = rows_y[color]
            if shape == "triangle":    # put the bounding box, not the centroid, on the row
                y -= sizes[color] * (math.sqrt(3) / 2) / 2 - sizes[color] / math.sqrt(3) + \
                     sizes[color] * (math.sqrt(3) / 2) / 2 - sizes[color] * math.sqrt(3) / 6
            pieces.append(piece(f"A{n}", color, shape, cols_x[shape], y, sizes[color]))
            n += 1
    return pieces


def sheet_b(seed=6):
    """18 pieces (2 per color-shape), random size, position and angle (for counting)."""
    rng = random.Random(seed)
    specs = [(c, s) for c in COLOR_RGB for s in ("circle", "square", "triangle")] * 2
    rng.shuffle(specs)
    x0, x1, y0, y1, gap = MARGIN, PAGE_W - MARGIN, MARGIN, PAGE_H - MARGIN - 14, 8
    while True:                       # restart if one piece cannot be placed
        pieces = []
        for i, (color, shape) in enumerate(specs, 1):
            size = rng.choice([25, 28, 30])
            r = radius(shape, size)
            for _ in range(4000):
                x, y = rng.uniform(x0 + r, x1 - r), rng.uniform(y0 + r, y1 - r)
                if all(math.hypot(x - q["x"], y - q["y"]) > r + q["r"] + gap for q in pieces):
                    p = piece(f"B{i}", color, shape, x, y, size, rng.uniform(0, 90))
                    p["r"] = r
                    pieces.append(p)
                    break
            else:
                break
        if len(pieces) == len(specs):
            return pieces


def sheet_c():
    """Touching and overlapping pieces (later items are drawn on top)."""
    s3 = math.sqrt(3)
    return [
        # 1: two red circles touching -> same mask, one contour
        piece("C1", "red", "circle", 40, 150, 30), piece("C2", "red", "circle", 66, 150, 30),
        # 2: two blue squares sharing one edge -> looks like one rectangle
        piece("C3", "blue", "square", 125, 150, 30), piece("C4", "blue", "square", 155, 150, 30),
        # 3: two green triangles overlapping -> one merged polygon
        piece("C5", "green", "triangle", 210, 145, 34), piece("C6", "green", "triangle", 224, 152, 34, 180),
        # 4: green triangle on top of a red square -> square loses a corner
        piece("C7", "red", "square", 45, 85, 32), piece("C8", "green", "triangle", 62, 75, 28, 15),
        # 5: blue circle on top of a green circle -> green becomes a crescent
        piece("C9", "green", "circle", 125, 85, 34), piece("C10", "blue", "circle", 145, 85, 28),
        # 6: red triangle touching a blue square (different colors, no overlap)
        piece("C11", "blue", "square", 205, 85, 30),
        piece("C12", "red", "triangle", 220 + 30 * s3 / 6, 85, 30, -90),
        # 7: isolated pieces as a control
        piece("C13", "red", "circle", 255, 40, 28), piece("C14", "green", "square", 150, 35, 28),
        piece("C15", "blue", "triangle", 45, 32, 30),
    ]


C_GROUPS = [   # result column: lab6_ref.py on a 640 px render of this sheet
    ("C1-C2", "วงกลมแดง 2 ชิ้นซ้อนกันเล็กน้อย", "รวมเป็น contour เดียว ได้ circle 1 ชิ้น (C = 0.64)"),
    ("C3-C4", "สี่เหลี่ยมน้ำเงิน 2 ชิ้นชิดขอบกัน", "รวมเป็นสี่เหลี่ยมผืนผ้า ได้ square 1 ชิ้น"),
    ("C5-C6", "สามเหลี่ยมเขียว 2 ชิ้นซ้อนกัน", "รวมเป็นสี่เหลี่ยมด้านขนาน ได้ square 1 ชิ้น (รูปทรงผิด)"),
    ("C7-C8", "สามเหลี่ยมเขียวทับสี่เหลี่ยมแดง", "สี่เหลี่ยมแหว่งมุมแต่ยังได้ n = 4 นับถูกทั้ง 2 ชิ้น"),
    ("C9-C10", "วงกลมน้ำเงินทับวงกลมเขียว", "วงกลมเขียวเหลือรูปเสี้ยว C ลดเหลือ 0.72 ยังได้ circle"),
    ("C11-C12", "สามเหลี่ยมแดงแตะสี่เหลี่ยมน้ำเงิน", "ต่างสี แยก mask กันได้ นับถูกทั้ง 2 ชิ้น"),
    ("C13-C15", "ชิ้นงานแยกเดี่ยว (control)", "นับและจำแนกถูกทั้ง 3 ชิ้น"),
]


# ---------------------------------------------------------------- drawing helpers
def ruler(c, x, y, length=100, vertical=False):
    """Ruler with 1 mm ticks; (x, y) is the 0 mark (mm)."""
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(0.2 * mm)
    c.setFont("Thai", 7)
    if vertical:
        c.line(x * mm, y * mm, x * mm, (y + length) * mm)
    else:
        c.line(x * mm, y * mm, (x + length) * mm, y * mm)
    for i in range(length + 1):
        t = 6 if i % 10 == 0 else 4 if i % 5 == 0 else 2.5
        c.setLineWidth((0.25 if i % 10 == 0 else 0.15) * mm)
        if vertical:
            c.line(x * mm, (y + i) * mm, (x + t) * mm, (y + i) * mm)
            if i % 10 == 0:
                c.drawString((x + 7.5) * mm, (y + i - 0.9) * mm, str(i))
        else:
            c.line((x + i) * mm, y * mm, (x + i) * mm, (y + t) * mm)
            if i % 10 == 0:
                c.drawCentredString((x + i) * mm, (y + 7.5) * mm, str(i))
    c.setFont("Thai", 8)
    if vertical:
        c.drawString((x + 3) * mm, (y + length + 4) * mm, "mm")
    else:
        c.drawString((x + length + 4) * mm, (y + 1) * mm, "mm")


def header(c, letter, title):
    c.setFillColorRGB(0, 0, 0)
    c.setFont("ThaiB", 26)
    c.drawString(MARGIN * mm, (PAGE_H - MARGIN - 6) * mm, letter)
    c.setFont("ThaiB", 11)
    c.drawString((MARGIN + 14) * mm, (PAGE_H - MARGIN - 1) * mm, f"ใบงาน 6 แผ่นทดสอบ {letter}: {title}")
    c.setFont("Thai", 8)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString((MARGIN + 14) * mm, (PAGE_H - MARGIN - 6) * mm,
                 "พิมพ์สีขนาดจริง 100% (Actual size) ห้ามเลือก Fit to page  |  LE382 ปฏิบัติการเครื่องมือวัดและระบบการวัด")


def label(c, text, x, y, size=8):
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.setFont("Thai", size)
    c.drawCentredString(x * mm, y * mm, text)


# ---------------------------------------------------------------- pages
def draw_sheet_a(c, pieces):
    header(c, "A", "สี รูปทรง และขนาด (ส่วนที่ 2.1, 2.2 และส่วนที่ 3)")
    for p in pieces:
        draw_piece(c, p)
        label(c, p["id"], p["x"] - radius(p["shape"], p["size"]) - 8, p["y"] - 1.2, 9)
    ruler(c, 40, 22)
    ruler(c, 262, 45, vertical=True)
    label(c, "ไม้บรรทัดอ้างอิงสำหรับสอบเทียบ (ส่วนที่ 3.1) ตรวจความยาว 100 mm ด้วยไม้บรรทัดจริงหลังพิมพ์",
          90, 14, 8)


def draw_sheet(c, letter, title, pieces):
    header(c, letter, title)
    for p in pieces:
        draw_piece(c, p)


def key_table(c, x, y, rows, widths, font=8, line=5.2):
    """Simple table; rows[0] is the header. (x, y) is the top-left (mm)."""
    c.setFillColorRGB(0, 0, 0)
    for r, row in enumerate(rows):
        c.setFont("ThaiB" if r == 0 else "Thai", font)
        cx = x
        for text, w in zip(row, widths):
            c.drawString((cx + 1.5) * mm, (y - (r + 1) * line + 1.5) * mm, str(text))
            cx += w
        c.setLineWidth(0.4 if r == 0 else 0.15)
        c.line(x * mm, (y - (r + 1) * line) * mm, (x + sum(widths)) * mm, (y - (r + 1) * line) * mm)
    c.setLineWidth(0.4)
    c.line(x * mm, y * mm, (x + sum(widths)) * mm, y * mm)
    return y - len(rows) * line


def thumbnail(c, pieces, ox, oy, s, ids=True):
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    c.rect(ox * mm, oy * mm, s * PAGE_W * mm, s * PAGE_H * mm, stroke=1, fill=0)
    for p in pieces:
        draw_piece(c, p, s, ox, oy)
    if ids:
        for p in pieces:
            c.setFillColorRGB(1, 1, 1)
            c.setFont("ThaiB", 6)
            c.drawCentredString((ox + s * p["x"]) * mm, (oy + s * p["y"] - 0.8) * mm, p["id"][1:])


def counts(pieces):
    rows = [["สี \\ รูปทรง", "วงกลม", "สี่เหลี่ยม", "สามเหลี่ยม", "รวม"]]
    for color in COLOR_RGB:
        n = [sum(p["color"] == color and p["shape"] == s for p in pieces)
             for s in ("circle", "square", "triangle")]
        rows.append([COLOR_TH[color], *n, sum(n)])
    rows.append(["รวม", *[sum(p["shape"] == s for p in pieces) for s in ("circle", "square", "triangle")],
                 len(pieces)])
    return rows


def size_text(p):
    if p["shape"] == "circle":
        return f"เส้นผ่านศูนย์กลาง {p['size']:.0f}"
    return f"ด้าน {p['size']:.0f}"


def draw_key(c, a, b, cc):
    # page 1: sheet A
    c.setFont("ThaiB", 14)
    c.drawString(MARGIN * mm, (PAGE_H - MARGIN) * mm, "เฉลยแผ่นทดสอบใบงาน 6 (สำหรับผู้สอน ไม่แจกนักศึกษา)")
    c.setFont("ThaiB", 11)
    c.drawString(MARGIN * mm, (PAGE_H - MARGIN - 10) * mm, "แผ่น A: ขนาดตามแบบ (mm) ค่าจริงหลังพิมพ์ให้วัดด้วยไม้บรรทัด")
    thumbnail(c, a, MARGIN, 95, 0.33)
    rows = [["ID", "สี", "รูปทรง", "ขนาดตามแบบ (mm)", "C ทางทฤษฎี"]]
    circ = {"circle": "1.000", "square": "0.785", "triangle": "0.605"}
    for p in a:
        rows.append([p["id"], COLOR_TH[p["color"]], SHAPE_TH[p["shape"]], size_text(p), circ[p["shape"]]])
    key_table(c, 125, PAGE_H - MARGIN - 15, rows, [12, 18, 22, 48, 22])
    key_table(c, MARGIN, 88, counts(a), [24, 18, 20, 22, 14])
    c.setFont("Thai", 8)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    notes = [
        "ใช้กับตาราง 3.2.1: วงกลม A1, A4, A7 (30, 35, 40 mm) และสี่เหลี่ยม A2, A5, A8 (30, 35, 40 mm)",
        "ไม้บรรทัดแนวนอนและแนวตั้งยาว 100 mm ถ้าพิมพ์คลาด (เช่น 98 mm) ขนาดชิ้นงานจะคลาดในสัดส่วนเดียวกัน",
        "จึงต้องให้นักศึกษาวัดขนาดอ้างอิงด้วยไม้บรรทัดจริง ไม่ใช้ค่าตามแบบ",
    ]
    for i, t in enumerate(notes):
        c.drawString(MARGIN * mm, (52 - 5 * i) * mm, t)
    c.showPage()

    # page 2: sheets B and C
    c.setFont("ThaiB", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(MARGIN * mm, (PAGE_H - MARGIN) * mm, "แผ่น B: นับวัตถุ 18 ชิ้น (สีละรูปทรงละ 2 ชิ้น ขนาด 25-30 mm วางเอียงแบบสุ่ม)")
    thumbnail(c, b, MARGIN, 108, 0.33)
    key_table(c, 125, PAGE_H - MARGIN - 4, counts(b), [24, 18, 20, 22, 14])
    c.setFont("ThaiB", 11)
    c.drawString(MARGIN * mm, 98 * mm, f"แผ่น C: ชิ้นงานแตะหรือซ้อนกัน N_reference = {len(cc)} ชิ้น")
    thumbnail(c, cc, MARGIN, 20, 0.33)
    rows = [["ชิ้น", "การจัดวาง", "ผลจากโปรแกรมเฉลย lab6_ref.py"]]
    rows += [list(g) for g in C_GROUPS]
    key_table(c, 125, 94, rows, [18, 52, 92], font=7.5)
    key_table(c, 125, 50, counts(cc), [24, 18, 20, 22, 14])
    c.setFont("Thai", 8)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    notes = [
        "ผลจาก lab6_ref.py กับภาพจำลองกว้าง 640 pixel (ยังไม่ผ่านกล้อง): แผ่น A นับได้ 9/9, แผ่น B 18/18,",
        "แผ่น C N_measured = 12 (e = -3, จำแนกถูก 9 ชิ้น) ผลจากกล้องจริงขึ้นกับแสง สีที่พิมพ์ และช่วง HSV ที่ตั้ง",
    ]
    for i, t in enumerate(notes):
        c.drawString(MARGIN * mm, (12 - 4.5 * i) * mm, t)
    c.showPage()


def main():
    a, b, cc = sheet_a(), sheet_b(), sheet_c()

    c = Canvas(str(OUT_DIR / "test_sheets_02.pdf"), pagesize=landscape(A4))
    c.setTitle("LE382 Lab 6 test sheets")
    draw_sheet_a(c, a)
    c.showPage()
    draw_sheet(c, "B", "นับวัตถุตามสีและรูปทรง (ส่วนที่ 2.3, 2.4)", b)
    c.showPage()
    draw_sheet(c, "C", "ชิ้นงานแตะหรือซ้อนกัน (ส่วนที่ 2.4 ครั้งที่ 3)", cc)
    c.showPage()
    c.save()

    k = Canvas(str(OUT_DIR / "test_sheets_02_key.pdf"), pagesize=landscape(A4))
    k.setTitle("LE382 Lab 6 test sheets - answer key")
    draw_key(k, a, b, cc)
    k.save()
    print("wrote", OUT_DIR / "test_sheets_02.pdf", "and", OUT_DIR / "test_sheets_02_key.pdf")


if __name__ == "__main__":
    main()
