#!/usr/bin/env python3
"""Generate an NCC Education Level 4 Diploma certificate PDF."""

from __future__ import annotations

import math
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "Thiha_Kyaw_Zaww_NCC_Level4_Diploma_Certificate.pdf"

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
pdfmetrics.registerFont(TTFont("LSerif", str(FONT_DIR / "LiberationSerif-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LSerif-Bold", str(FONT_DIR / "LiberationSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("LSerif-Italic", str(FONT_DIR / "LiberationSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("LSans", str(FONT_DIR / "LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("LSans-Bold", str(FONT_DIR / "LiberationSans-Bold.ttf")))


def ensure_assets() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    _make_ofqual_logo(ASSETS / "ofqual_logo.png")
    _make_qw_logo(ASSETS / "qw_logo.png")
    _make_signature(ASSETS / "signature.png")
    _make_hologram(ASSETS / "hologram.png")
    _make_qr(ASSETS / "qr.png")


def _make_ofqual_logo(path: Path) -> None:
    w, h = 560, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    purple = (128, 45, 145, 255)

    # Twin stylized marks (approximate Ofqual symbol)
    def mark(ox: int, oy: int, scale: float = 1.0) -> None:
        pts = [
            (ox, oy + int(36 * scale)),
            (ox - int(34 * scale), oy + int(10 * scale)),
            (ox - int(22 * scale), oy - int(8 * scale)),
            (ox - int(8 * scale), oy + int(10 * scale)),
            (ox + int(4 * scale), oy - int(28 * scale)),
            (ox + int(18 * scale), oy + int(6 * scale)),
            (ox + int(34 * scale), oy - int(16 * scale)),
            (ox + int(34 * scale), oy + int(36 * scale)),
        ]
        draw.polygon(pts, fill=purple)
        draw.ellipse(
            [
                ox - int(14 * scale),
                oy + int(28 * scale),
                ox + int(14 * scale),
                oy + int(56 * scale),
            ],
            fill=purple,
        )

    mark(55, 70, 0.95)
    mark(95, 78, 0.78)

    try:
        font_big = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 58)
        font_reg = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 30)
        font_url = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Regular.ttf"), 24)
    except OSError:
        font_big = font_reg = font_url = ImageFont.load_default()

    draw.text((145, 48), "ofqual", fill=(20, 20, 20, 255), font=font_big)
    draw.text((147, 112), "REGULATED", fill=(20, 20, 20, 255), font=font_reg)
    draw.text((18, 195), "register.ofqual.gov.uk", fill=(35, 35, 35, 255), font=font_url)
    img.save(path)


def _make_qw_logo(path: Path) -> None:
    size = 400
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, size - 5, size - 5], outline=(25, 25, 25, 255), width=5)

    try:
        font_cy = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 24)
        font_en = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 22)
        font_small = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Regular.ttf"), 17)
    except OSError:
        font_cy = font_en = font_small = ImageFont.load_default()

    cx = cy = size // 2
    r = 62
    draw.ellipse([cx - r, cy - r - 8, cx + r, cy + r - 8], fill=(0, 90, 168, 255))
    draw.ellipse(
        [cx - r + 12, cy - r + 4, cx + r - 12, cy + r - 20],
        outline=(255, 255, 255, 255),
        width=3,
    )
    # Simplified Welsh dragon silhouette
    draw.polygon(
        [
            (cx - 22, cy + 10),
            (cx - 10, cy - 30),
            (cx + 4, cy - 8),
            (cx + 24, cy - 34),
            (cx + 14, cy + 16),
            (cx - 4, cy + 2),
        ],
        fill=(255, 255, 255, 255),
    )

    def centered(text: str, y: int, font) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((size - tw) / 2, y), text, fill=(20, 20, 20, 255), font=font)

    centered("CYMWYSTERAU", 30, font_cy)
    centered("CYMRU", 56, font_cy)
    centered("QUALIFICATIONS", 275, font_en)
    centered("WALES", 300, font_en)
    centered("Recognised awarding body", 335, font_small)
    img.save(path)


def _make_signature(path: Path) -> None:
    w, h = 700, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ink = (8, 8, 8, 255)

    def curve(points, width=3):
        # densify with simple interpolation for smoother look
        dense = []
        for i in range(len(points) - 1):
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            steps = 12
            for s in range(steps):
                t = s / steps
                # slight sine for hand feel
                bend = math.sin(t * math.pi) * 2
                dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - bend))
        dense.append(points[-1])
        draw.line(dense, fill=ink, width=width, joint="curve")

    # Peter
    curve(
        [
            (30, 140),
            (50, 70),
            (70, 160),
            (95, 55),
            (120, 155),
            (145, 75),
            (170, 135),
            (200, 90),
            (230, 130),
        ],
        4,
    )
    curve([(40, 155), (100, 175), (180, 160), (240, 145)], 2)

    # Ford with capital F loop
    curve([(250, 55), (255, 40), (270, 70), (255, 130), (250, 150)], 3)
    curve(
        [
            (255, 95),
            (290, 85),
            (320, 140),
            (350, 70),
            (380, 145),
            (415, 85),
            (450, 135),
            (500, 95),
            (545, 130),
            (600, 100),
        ],
        4,
    )
    curve([(320, 160), (420, 180), (530, 155), (620, 170)], 2)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(path)


def _make_hologram(path: Path) -> None:
    size = 340
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            if not (14 < x < size - 14 and 14 < y < size - 14):
                continue
            dx, dy = x - size / 2, y - size / 2
            dist = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)
            wave = math.sin(dist / 7 + angle * 5) * 45
            base = 170 + int(wave)
            r = min(255, max(70, base + int(45 * math.sin(angle * 3))))
            g = min(255, max(70, base + int(35 * math.sin(angle * 3 + 2.1))))
            b = min(255, max(90, base + int(50 * math.cos(angle * 2.4))))
            pixels[x, y] = (r, g, b, 255)

    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 12, size - 13, size - 13], outline=(70, 70, 85, 255), width=3)
    for i in range(24, size - 24, 26):
        for j in range(24, size - 24, 26):
            draw.ellipse([i, j, i + 9, j + 9], outline=(255, 255, 255, 70), width=1)

    ox0, oy0, ox1, oy1 = 78, 100, 262, 235
    draw.ellipse([ox0, oy0, ox1, oy1], outline=(35, 35, 45, 230), width=3)
    try:
        font_n = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Bold.ttf"), 44)
        font_e = ImageFont.truetype(str(FONT_DIR / "LiberationSans-Regular.ttf"), 22)
    except OSError:
        font_n = font_e = ImageFont.load_default()
    draw.text((118, 125), "NCC", fill=(25, 25, 35, 240), font=font_n)
    draw.text((112, 175), "education", fill=(25, 25, 35, 240), font=font_e)
    img.save(path)


def _make_qr(path: Path) -> None:
    payload = "https://AuthentiQual.com/C7118405-8105-49A4-9F79-0A3C2AEB538D"
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img.save(path)


def draw_ncc_logo(c: canvas.Canvas, cx: float, cy: float, scale: float = 1.0) -> None:
    """Vector NCC Education oval logo centered at (cx, cy)."""
    rx, ry = 32 * mm * scale, 15.5 * mm * scale
    c.setStrokeColor(black)
    c.setLineWidth(1.7 * scale)
    c.setFillColor(white)
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=1)

    c.setFillColor(black)
    c.setFont("LSans-Bold", 28 * scale)
    c.drawCentredString(cx, cy + 1.2 * mm * scale, "NCC")
    # ®
    c.setFont("LSans", 7 * scale)
    ncc_w = c.stringWidth("NCC", "LSans-Bold", 28 * scale)
    c.drawString(cx + ncc_w / 2 - 1 * mm, cy + 8 * mm * scale, "®")

    c.setFont("LSans", 13 * scale)
    c.drawCentredString(cx, cy - 7.5 * mm * scale, "education")


def draw_wrapped_centered(
    c: canvas.Canvas,
    text: str,
    y: float,
    font: str,
    size: float,
    max_width: float,
    leading: float | None = None,
) -> float:
    c.setFont(font, size)
    leading = leading or size * 1.28
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    page_w, _ = A4
    for line in lines:
        c.drawCentredString(page_w / 2, y, line)
        y -= leading
    return y


def create_certificate(output: Path = OUTPUT) -> Path:
    ensure_assets()
    page_w, page_h = A4
    c = canvas.Canvas(str(output), pagesize=A4)

    c.setFillColor(white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setFillColor(black)

    # Header logo + tagline
    draw_ncc_logo(c, page_w / 2, page_h - 32 * mm, scale=1.05)
    c.setFont("LSans", 10.5)
    c.drawCentredString(
        page_w / 2, page_h - 52 * mm, "Awarding Great British Qualifications"
    )

    # Main body — generous vertical rhythm like the original
    y = page_h - 78 * mm
    title = "NCC Education Level 4 Diploma in Computing (with Business Management)"
    y = draw_wrapped_centered(
        c, title, y, "LSerif-Bold", 19.5, page_w - 34 * mm, leading=25
    )

    y -= 5 * mm
    c.setFont("LSerif-Bold", 12)
    c.drawCentredString(page_w / 2, y, "Qualification Number: 600/0406/X")

    y -= 16 * mm
    c.setFont("LSerif-Italic", 12.5)
    c.drawCentredString(page_w / 2, y, "This is to certify that")

    y -= 16 * mm
    c.setFont("LSerif-Bold", 28)
    c.drawCentredString(page_w / 2, y, "Thiha Kyaw Zaww")

    y -= 16 * mm
    achievement = (
        "has successfully achieved a Merit mark of 69% in the above qualification "
        "awarded by NCC Education and delivered by"
    )
    y = draw_wrapped_centered(
        c, achievement, y, "LSerif-Italic", 12, page_w - 50 * mm, leading=16
    )

    y -= 10 * mm
    c.setFont("LSerif-Bold", 16)
    c.drawCentredString(page_w / 2, y, "NMA University, Myanmar")

    y -= 11 * mm
    c.setFont("LSerif-Bold", 14)
    c.drawCentredString(page_w / 2, y, "17 January 2025")

    # ---- Footer band ----
    left = 16 * mm

    # IDs above Ofqual
    c.setFont("LSans", 7)
    c.drawString(
        left,
        48 * mm,
        "Candidate ID Number: 211644   Certificate Number: 35255",
    )

    # Ofqual
    c.drawImage(
        str(ASSETS / "ofqual_logo.png"),
        left,
        16 * mm,
        width=40 * mm,
        height=17 * mm,
        mask="auto",
        preserveAspectRatio=True,
    )

    # Qualifications Wales
    c.drawImage(
        str(ASSETS / "qw_logo.png"),
        62 * mm,
        12 * mm,
        width=26 * mm,
        height=26 * mm,
        mask="auto",
        preserveAspectRatio=True,
    )

    # Signature + titles
    sig_x = 98 * mm
    c.drawImage(
        str(ASSETS / "signature.png"),
        sig_x,
        28 * mm,
        width=40 * mm,
        height=13.5 * mm,
        mask="auto",
        preserveAspectRatio=True,
    )
    c.setFont("LSerif", 9)
    c.drawString(sig_x + 1 * mm, 23.5 * mm, "Professor Peter Ford")
    c.setFont("LSerif", 8)
    c.drawString(sig_x + 1 * mm, 19.5 * mm, "Chair of the Academic Board")

    # Hologram (between signature and QR)
    c.drawImage(
        str(ASSETS / "hologram.png"),
        142 * mm,
        28 * mm,
        width=20 * mm,
        height=20 * mm,
        mask="auto",
        preserveAspectRatio=True,
    )

    # QR block on the right
    qr_size = 24 * mm
    qr_x = page_w - 18 * mm - qr_size
    qr_y = 16 * mm
    c.setFont("LSans", 5.5)
    c.drawCentredString(qr_x + qr_size / 2, qr_y + qr_size + 3.5 * mm, "C7118405-8105-49A4")
    c.drawImage(
        str(ASSETS / "qr.png"),
        qr_x,
        qr_y,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
    )
    c.setFont("LSans", 5.2)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 3 * mm, "9F79-0A3C2AEB538D")
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 5.5 * mm, "AuthentiQual.com")

    # Thin blue line at bottom edge
    c.setStrokeColor(Color(0.12, 0.32, 0.68))
    c.setLineWidth(1.8)
    c.line(0, 3.5 * mm, page_w, 3.5 * mm)

    c.showPage()
    c.save()
    return output


if __name__ == "__main__":
    out = create_certificate()
    print(f"Wrote {out}")
