# The World in One Day - Thursday 19 November 2026.
# Draws a one-page newspaper of that day's world news as a 1024x1024 PNG
# and writes it to /output/entry.png (MAKEFUN_OUTPUT_DIR stands in for
# /output outside the grader). Pure Python standard library, fully
# deterministic: the same bytes come out of every run.
import os, struct, zlib

W = H = 1024
PAPER = (247, 243, 234)
INK = (20, 33, 61)
RED = (193, 39, 45)
TEAL = (14, 124, 123)
OCHRE = (176, 106, 12)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
LINEC = (206, 198, 178)

# 5x7 bitmap font: each glyph is 7 rows, bit 4 is the leftmost pixel.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x01, 0x01, 0x01, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x1F),
    'F': (0x1F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x01),
    'G': (0x0E, 0x11, 0x01, 0x17, 0x11, 0x11, 0x0E),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x09, 0x05, 0x03, 0x05, 0x09, 0x11),
    'L': (0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x01, 0x01, 0x01),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x05, 0x09, 0x11),
    'S': (0x0E, 0x11, 0x01, 0x0E, 0x10, 0x11, 0x0E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    'Y': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x10, 0x08, 0x04, 0x02, 0x01, 0x1F),
    '0': (0x0E, 0x11, 0x19, 0x15, 0x13, 0x11, 0x0E),
    '1': (0x04, 0x06, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x10, 0x08, 0x04, 0x02, 0x1F),
    '3': (0x0E, 0x11, 0x10, 0x06, 0x10, 0x11, 0x0E),
    '4': (0x08, 0x0C, 0x0A, 0x09, 0x1F, 0x08, 0x08),
    '5': (0x1F, 0x01, 0x0F, 0x10, 0x10, 0x11, 0x0E),
    '6': (0x0E, 0x11, 0x01, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x10, 0x08, 0x04, 0x02, 0x02, 0x02),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x10, 0x11, 0x0E),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x06, 0x06),
    ',': (0, 0, 0, 0, 0x0C, 0x08, 0x10),
    "'": (0x0C, 0x08, 0x10, 0, 0, 0, 0),
    ':': (0, 0x06, 0x06, 0, 0x06, 0x06, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '$': (0x04, 0x0F, 0x15, 0x0E, 0x15, 0x0F, 0x04),
    '&': (0x0E, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x0D),
    '/': (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    '(': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    ')': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x10, 0x08, 0x04, 0, 0x04),
    '·': (0, 0, 0, 0x06, 0x06, 0, 0),
}

CV = bytearray(bytes(PAPER) * (W * H))


def rect(x, y, w, h, c):
    row = bytes(c) * w
    for yy in range(y, y + h):
        o = (yy * W + x) * 3
        CV[o:o + 3 * w] = row


def textw(s, sc):
    return len(s) * 6 * sc - sc


def text(x, y, s, sc, c, center=False):
    if center:
        x = x - textw(s, sc) // 2
    for ch in s.upper():
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            bits = g[r]
            if not bits:
                continue
            for b in range(5):
                if bits >> (4 - b) & 1:
                    rect(x + b * sc, y + r * sc, sc, sc, c)
        x += 6 * sc
    return x


def wrap(s, maxch):
    lines, cur = [], ''
    for wd in s.split(' '):
        if cur and len(cur) + 1 + len(wd) > maxch:
            lines.append(cur)
            cur = wd
        else:
            cur = cur + ' ' + wd if cur else wd
    if cur:
        lines.append(cur)
    return lines


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        o = yy * W * 3
        raw += CV[o:o + W * 3]

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def flag_us(x, y, w, h):
    sh = h // 7
    for i in range(7):
        rect(x, y + i * sh, w, sh, (178, 34, 52) if i % 2 == 0 else WHITE)
    rect(x, y, w * 2 // 5, sh * 4, (60, 59, 110))
    for r in range(4):
        for cnum in range(5):
            rect(x + 6 + cnum * (w * 2 // 5 - 8) // 4, y + 5 + r * (sh * 4 - 8) // 3, 4, 4, WHITE)


def flag_cn(x, y, w, h):
    rect(x, y, w, h, (222, 41, 16))
    for dx, dy, s in ((10, 8, 10), (30, 4, 5), (36, 14, 5), (36, 26, 5), (30, 36, 5)):
        rect(x + dx, y + dy, s, s, (255, 222, 0))


def flag_ru(x, y, w, h):
    sh = h // 3
    rect(x, y, w, sh, WHITE)
    rect(x, y + sh, w, sh, (0, 57, 166))
    rect(x, y + 2 * sh, w, h - 2 * sh, (213, 43, 30))


STORIES = [
    ('LAW', RED, 'WORLD COURT RULES ON ROHINGYA',
     'THE ICJ DECIDES GAMBIA V. MYANMAR GENOCIDE CASE'),
    ('CLIMATE', TEAL, 'COP31 RACE TO SAVE TALKS',
     'MINISTERS IN ANTALYA, TURKIYE FIGHT FOR A FINAL TEXT'),
    ('ENERGY', OCHRE, 'TANKERS HIT MINES NEAR HORMUZ',
     'THREE TANKERS HIT. IEA WARNS ON ENERGY SECURITY'),
    ('WAR', RED, 'UKRAINE STRIKES CRIMEAN BRIDGE',
     'TRAFFIC HALTED. EU PROPOSES A 45BN EURO LOAN'),
    ('ASIA', TEAL, 'BANGLADESH: YUNUS HOME BURNED',
     'VIOLENCE IN 28 DISTRICTS. TROOPS ON THE STREETS'),
    ('MARKETS', OCHRE, 'STOCKS SLIDE, COPPER -5 PCT',
     'HANG SENG -1.9 PCT, S&P 500 -0.2 PCT, BRENT $89.59'),
]

BRIEFS = [
    ('ARTS', "VAN GOGH SETS $190.4M RECORD AT SOTHEBY'S"),
    ('SCIENCE', 'VOYAGER 1 NOW ONE LIGHT-DAY FROM EARTH'),
    ('BUSINESS', 'ANTHROPIC SETS $81.3BN IPO RECORD'),
    ('AMERICAS', 'DEMOCRATS PICK JEFFRIES FOR SPEAKER'),
]


def draw():
    rect(0, 0, W, 8, RED)
    text(W // 2, 22, 'THE WORLD IN ONE DAY', 5, INK, center=True)
    text(W // 2, 78, 'THURSDAY 19 NOVEMBER 2026', 6, RED, center=True)
    rect(24, 132, W - 48, 3, INK)
    # Hero: the first US-China-Russia trilateral summit, Shenzhen.
    text(24, 148, 'SHENZHEN · APEC SUMMIT', 3, RED)
    fw, fh, fx = 96, 64, 640
    flag_us(fx, 146, fw, fh)
    flag_cn(fx + 112, 146, fw, fh)
    flag_ru(fx + 224, 146, fw, fh)
    text(fx + 48, 216, 'USA', 2, GREY, center=True)
    text(fx + 160, 216, 'CHINA', 2, GREY, center=True)
    text(fx + 272, 216, 'RUSSIA', 2, GREY, center=True)
    text(24, 196, 'TRUMP, XI AND PUTIN', 5, INK)
    text(24, 240, 'HOLD FIRST TRILATERAL SUMMIT', 5, INK)
    sub = ("THE FIRST-EVER THREE-WAY MEETING OF THE US, CHINESE AND "
           "RUSSIAN LEADERS. NUCLEAR ARMS AND IRAN TOP THE AGENDA. "
           "UKRAINE DISCUSSED SEPARATELY.")
    for i, ln in enumerate(wrap(sub, 54)):
        text(24, 292 + i * 29, ln, 3, GREY)
    rect(24, 386, W - 48, 3, INK)
    # Story rows.
    y = 404
    for cat, cc, head, summ in STORIES:
        rect(24, y + 2, 10, 58, cc)
        x = text(48, y, cat + ' · ', 4, cc)
        text(x, y, head, 4, INK)
        text(48, y + 38, summ, 3, GREY)
        y += 72
        rect(24, y - 8, W - 48, 1, LINEC)
    # Briefs band.
    rect(0, y + 2, W, H - y - 2, INK)
    text(24, y + 16, 'ALSO TODAY', 3, (255, 205, 90))
    by = y + 52
    for cat, line in BRIEFS:
        x = text(24, by, cat + ': ', 3, (255, 205, 90))
        text(x, by, line, 3, WHITE)
        by += 28
    text(24, H - 18, 'SOURCES: WIRE REPORTS OF 19 NOV 2026 · DRAWN BY AN AI AGENT', 2, (170, 178, 200))


def main():
    draw()
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'entry.png'), 'wb') as f:
        f.write(png_bytes())


if __name__ == '__main__':
    main()
