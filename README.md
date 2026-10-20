# CV for Beginners

Computer vision สำหรับงานตรวจสอบในอุตสาหกรรม ด้วย Python และ OpenCV ใน 5 ใบงาน ตั้งแต่นับวัตถุด้วย AI จนถึงสถานีตรวจที่วัดขนาดชิ้นงานแล้วสั่งไฟ OK/NG บนบอร์ด Arduino

**เอกสารเรียน (HTML):** <https://vsupacha.github.io/cv-for-beginners/>

| ใบงาน | เรื่อง |
| --- | --- |
| 1 | นับวัตถุด้วย AI (YOLO, เส้นนับ, error) |
| 2 | กล้องในฐานะเซนเซอร์ (HSV, contour, pixel → mm) |
| 3 | แสง เวลา และการรับภาพ (การจัดแสง, Otsu, fps, latency, motion blur) |
| 4 | ตรวจสอบชิ้นงาน OK/NG (ArUco, homography, FRR/FAR) |
| 5 | วัดขนาดและสถานีตรวจ (สอบเทียบกล้อง, %GRR, Serial → UNO R4) |

| โฟลเดอร์ | เนื้อหา |
| --- | --- |
| `index.qmd`, `content/`, `_quarto.yml` | ต้นฉบับเอกสาร (Quarto) |
| `data/` | แผ่นทดสอบสำหรับพิมพ์ และภาพจำลองของใบงาน 4 |
| `code/` | โค้ดตั้งต้นของแต่ละใบงาน |
| `worksheets/` | ใบบันทึกผล PDF สำหรับเขียนบน tablet (สร้างด้วย `scripts/make_worksheets.py`) |
| `scripts/` | สคริปต์สร้างแผ่นทดสอบและใบบันทึกผล (ผู้สอน) |

## สร้างเอกสาร

ต้องมี [Quarto](https://quarto.org)

```bash
quarto preview
```

สร้างแผ่นทดสอบใหม่ (ต้องมี `opencv-contrib-python numpy pillow reportlab`)

```bash
python scripts/make_sheets.py
python scripts/make_sheets_02.py
```

## เผยแพร่

push เข้า `main` แล้ว GitHub Actions (`.github/workflows/publish.yml`) จะ render และ deploy ขึ้น GitHub Pages ให้อัตโนมัติ (ตั้งค่า Settings → Pages → Source เป็น GitHub Actions)
