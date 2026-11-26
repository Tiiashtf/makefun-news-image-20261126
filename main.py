#!/usr/bin/env python3
"""Draws the front page of THE WORLD TODAY for Thursday 26 November 2026.

Pure Python 3.13 standard library only: a small pixel canvas, filled-shape
drawing, a hand-authored 5x7 dot-matrix face, and a PNG writer built on
zlib. The program needs no input files and no network: it draws the whole
front page from the story copy below and writes /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). It is deterministic: every run writes the
exact same bytes. It never removes the output directory itself; it clears
only files inside it, then writes the image.

Every story on the page was reported on 26 November 2026: the US tariff
proposal, the Cairo ring-road tanker fire, the Houthi strikes on Saudi
sites, Kim Jong Un's tactical-nuclear order, Ukraine's Savasleyka airbase
strike and the leaked Russian casualty data, plus the day's briefs.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 227)
INK = (18, 18, 18)
RED = (158, 27, 27)
NAVY = (18, 34, 66)
NAVY2 = (28, 52, 96)
GOLD = (214, 158, 46)
FLAME = (232, 110, 30)
EMBER = (244, 164, 42)
STEEL = (46, 94, 126)
SEA = (24, 62, 96)
GREY = (112, 107, 96)
LIGHT = (233, 227, 211)
SMOKE = (150, 146, 136)
WHITE = (250, 248, 242)
GREEN = (34, 110, 72)

# ---------------------------------------------------------------- font
# A 5x7 dot-matrix face, authored for this page. Every glyph is seven
# rows of five cells; '#' is ink, ' ' is blank. All copy on the page is
# set in capitals, in the manner of a classic broadsheet headline face.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = [[bg for _ in range(w)] for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            row = self.buf[yy]
            for xx in range(max(0, x), min(self.w, x + w)):
                row[xx] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x1, y1, x2, y2, x3, y3, c):
        # Filled triangle by scanline: sort vertices by y.
        vs = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = vs
        def interp(y, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(y, (ax, ay), (bx, by))
            else:
                xa = interp(y, (bx, by), (cx, cy))
            xb = interp(y, (ax, ay), (cx, cy))
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            for x in range(int(lo), int(hi) + 1):
                self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        """Draw uppercase text; returns the width in pixels."""
        cx = x
        for ch in s:
            if ch == " ":
                cx += 6 * scale
                continue
            g = GLYPHS.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for r, row in enumerate(g):
                for col, cell in enumerate(row):
                    if cell == "1":
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def center(self, y, s, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = self.text_w(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)

    def wrap(self, x, y, max_w, s, scale, c, lh=None):
        """Word-wrap text; returns the y just below the last line."""
        if lh is None:
            lh = 9 * scale
        words = s.split(" ")
        line = ""
        cy = y
        for wd in words:
            trial = (line + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w or not line:
                line = trial
            else:
                self.text(x, cy, line, scale, c)
                cy += lh
                line = wd
        if line:
            self.text(x, cy, line, scale, c)
            cy += lh
        return cy


def png_bytes(cv):
    raw = bytearray()
    for row in cv.buf:
        raw.append(0)
        for (r, g, b) in row:
            raw += bytes((r, g, b))
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ---------------------------------------------------------------- icons
def draw_flame(cv, x, y, s):
    """A stylised flame, s = overall height in pixels."""
    w = s * 3 // 4
    cv.tri(x + w // 2, y, x, y + s, x + w, y + s, FLAME)
    cv.tri(x + w // 2, y + s // 3, x + w // 6, y + s,
           x + w * 5 // 6, y + s, EMBER)
    cv.tri(x + w // 2, y + s // 2, x + w // 3, y + s,
           x + w * 2 // 3, y + s, GOLD)
    cv.rect(x - 2, y + s, w + 4, 4, INK)


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, STEEL)
    cv.ring(cx, cy, r, NAVY, 3)
    # latitude bands and a meridian, as a wire globe
    cv.hline(cx - r + 4, cy - r // 2, 2 * r - 8, WHITE, 2)
    cv.hline(cx - r + 4, cy + r // 2, 2 * r - 8, WHITE, 2)
    cv.vline(cx, cy - r + 2, 2 * r - 4, WHITE, 2)
    cv.circle(cx - r // 3, cy - r // 4, r // 5, GREEN)
    cv.circle(cx + r // 4, cy + r // 3, r // 4, GREEN)


def draw_bars(cv, x, y, w, h, vals, c):
    """Rising bar chart on a baseline; vals are 0..1 fractions."""
    n = len(vals)
    bw = w // (n * 2)
    for i, v in enumerate(vals):
        bh = max(4, int(v * h))
        cv.rect(x + i * 2 * bw + bw // 2, y + h - bh, bw, bh, c)
    cv.hline(x, y + h, w, INK, 3)


def draw_rocket(cv, x, y, s):
    """A small rocket climbing to the right, s = length."""
    h = s // 3
    cv.tri(x + s, y + h // 2, x + s * 3 // 4, y, x + s * 3 // 4, y + h, RED)
    cv.rect(x + s // 4, y, s // 2, h, WHITE)
    cv.circle(x + s // 2, y + h // 2, h // 4, STEEL)
    cv.tri(x + s // 4, y, x, y - h // 2, x, y + h // 4, RED)
    cv.tri(x + s // 4, y + h, x, y + h * 3 // 4, x, y + h * 3 // 2, RED)
    cv.tri(x, y + h // 2, x - s // 4, y + h // 4, x - s // 4,
           y + h * 3 // 4, EMBER)


def draw_jet(cv, x, y, s):
    """A small jet seen from above, s = length."""
    h = s // 4
    cv.tri(x + s, y + h // 2, x + s * 4 // 5, y, x + s * 4 // 5, y + h, INK)
    cv.rect(x + s // 5, y, s * 3 // 5, h, STEEL)
    cv.tri(x + s // 5, y, x, y - h, x + s // 5, y + h // 2, STEEL)
    cv.tri(x + s // 5, y + h, x, y + 2 * h, x + s // 5, y + h // 2, STEEL)
    cv.tri(x + s // 5, y + h // 4, x + s // 10, y + h // 2,
           x + s // 5, y + h * 3 // 4, WHITE)


def draw_star(cv, cx, cy, r, c):
    cv.tri(cx, cy - r, cx - r // 3, cy, cx + r // 3, cy, c)
    cv.tri(cx, cy + r, cx - r // 3, cy, cx + r // 3, cy, c)
    cv.tri(cx - r, cy, cx, cy - r // 3, cx, cy + r // 3, c)
    cv.tri(cx + r, cy, cx, cy - r // 3, cx, cy + r // 3, c)


def draw_derrick(cv, x, y, s):
    """An oil derrick / refinery tower, s = height."""
    w = s // 2
    cv.tri(x + w // 2, y, x, y + s, x + w, y + s, INK)
    cv.rect(x + w // 2 - 2, y + s // 3, 4, s * 2 // 3, PAPER)
    cv.rect(x - 4, y + s, w + 8, 4, INK)
    cv.circle(x + w // 2, y - 6, 5, RED)


# ---------------------------------------------------------------- layout
def rule(cv, x, y, w, c=INK, t=3):
    cv.hline(x, y, w, c, t)


def kicker(cv, x, y, s, c=RED):
    cv.text(x, y, s, 2, c)
    return y + 18


def headline(cv, x, y, lines, scale, c=INK):
    cy = y
    for ln in lines:
        cv.text(x, cy, ln, scale, c)
        cy += 9 * scale
    return cy

def draw_page(cv):
    cv.rect(0, 0, W, H, PAPER)
    cv.rect(0, 0, W, 10, RED)
    cv.rect(0, H - 10, W, 10, RED)

    # ---- masthead ------------------------------------------------
    cv.rect(24, 24, 976, 128, NAVY)
    cv.center(40, "THE WORLD TODAY", 7, WHITE)
    cv.center(104, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    cv.center(132, "ONE DAY - ONE PAGE - THE WORLD IN FULL", 2, WHITE)
    rule(cv, 24, 168, 976, RED, 4)

    # ---- lead story: US tariffs ----------------------------------
    y = 186
    kicker(cv, 24, y, "WASHINGTON - TRADE")
    y = headline(cv, 24, y + 22, ["US HITS 14 NATIONS", "WITH NEW TARIFFS"], 4)
    y = cv.wrap(24, y + 6, 600, "WASHINGTON PROPOSES COUNTRY TARIFFS ON "
                "CHINA, THE EU, JAPAN AND INDIA - UP TO 25% ON INDIA OVER "
                "EXCESS CAPACITY. MARKETS FALL AS AI SHARES SELL OFF.",
                2, INK)
    # illustration: globe + rising tariff bars
    draw_globe(cv, 780, 300, 62)
    draw_bars(cv, 700, 392, 220, 56, [0.3, 0.45, 0.6, 0.8, 1.0], RED)
    cv.text(700, 452, "TARIFFS UP TO 25%", 2, RED)
    rule(cv, 24, 486, 976, INK, 3)

    # ---- second row: Cairo fire / Houthi strikes -----------------
    y = 506
    kicker(cv, 24, y, "CAIRO - DISASTER")
    y2 = headline(cv, 24, y + 22, ["TANKER FIRE KILLS 31", "ON CAIRO RING ROAD"], 3)
    y2 = cv.wrap(24, y2 + 4, 430, "A FUEL TANKER OVERTURNED AND BURST INTO "
                 "FLAMES ON THE BUSY HIGHWAY AROUND CAIRO. AT LEAST 31 DEAD "
                 "AND ABOUT 21 HURT, EGYPT SAYS.", 2, INK)
    draw_flame(cv, 470, 540, 110)

    kicker(cv, 560, y, "RIYADH - CONFLICT")
    y3 = headline(cv, 560, y + 22, ["HOUTHIS STRIKE", "SAUDI REFINERY"], 3)
    y3 = cv.wrap(560, y3 + 4, 320, "YEMEN'S HOUTHIS CLAIM ATTACKS ON SAUDI "
                 "PORTS AND THE RAS TANURA REFINERY. BRENT OIL RISES ON "
                 "SUPPLY FEARS.", 2, INK)
    draw_derrick(cv, 900, 560, 110)
    rule(cv, 24, 716, 976, INK, 3)

    # ---- third row: Kim / Ukraine --------------------------------
    y = 736
    kicker(cv, 24, y, "PYONGYANG - NUCLEAR")
    y2 = headline(cv, 24, y + 22, ["KIM ORDERS MORE", "TACTICAL NUKES"], 3)
    y2 = cv.wrap(24, y2 + 4, 430, "KIM JONG UN SAYS NORTH KOREA MUST DEPLOY "
                 "TACTICAL NUCLEAR WEAPONS ACROSS MORE DOMAINS AND EXPAND "
                 "PRODUCTION, KCNA REPORTS.", 2, INK)
    draw_rocket(cv, 470, 800, 90)

    kicker(cv, 560, y, "KYIV - WAR")
    y3 = headline(cv, 560, y + 22, ["UKRAINE HITS AIRBASE", "5 JETS DAMAGED"], 3)
    y3 = cv.wrap(560, y3 + 4, 320, "UKRAINE SAYS IT STRUCK SAVASLEYKA "
                 "AIRFIELD IN RUSSIA. LEAKED DATA PUT RUSSIAN WAR DEAD AT "
                 "NEARLY 500,000.", 2, INK)
    draw_jet(cv, 890, 800, 100)
    rule(cv, 24, 920, 976, RED, 4)

    # ---- briefs strip --------------------------------------------
    cv.wrap(24, 934, 976, "ALSO TODAY: FIRST PAKISTANI ASTRONAUT REACHES "
            "CHINA'S TIANGONG STATION - HAMAS SECURITY CHIEF KILLED IN GAZA "
            "- THANKSGIVING STORM POSTPONES MACY'S PARADE - MISS UNIVERSE: "
            "JENNIFER BARRETO - LIVERPOOL 3-0 CLUB BRUGGE - FCC CLEARS "
            "SPACEX 1M SATELLITES",
            2, INK)
    cv.center(1000, "SUMMED UP FROM THE NEWS OF 26 NOVEMBER 2026", 1, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    # Clear only the contents of the output directory, never the dir itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            for sub in os.listdir(path):
                os.remove(os.path.join(path, sub))
            os.rmdir(path)
        else:
            os.remove(path)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    data = png_bytes(cv)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
