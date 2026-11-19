#!/usr/bin/env python3
"""Render the 19 November 2026 world-news image (1024x1024 PNG).

Front-page layout: masthead naming the day, three hero stories, then a
two-column bulletin of 32 more verified stories, plus a footer ticker.
Every story below was checked against a news report published on
19 November 2026 (see the README for the source of each one).
The drawing is original code-drawn artwork: flat shapes, rules and
type only -- no photograph or copied artwork.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (180, 35, 24)
MUTED = (96, 92, 82)
WHITE = (255, 255, 255)
HAIR = (198, 192, 178)

CAT = {
    "WORLD": (180, 35, 24),
    "US": (29, 78, 137),
    "BUSINESS": (14, 107, 92),
    "TECH": (91, 58, 142),
    "ASIA": (176, 106, 0),
    "HEALTH": (46, 125, 50),
    "CLIMATE": (70, 110, 130),
}

HEROES = [
    {
        "kicker": "SHENZHEN SUMMIT",
        "color": (180, 35, 24),
        "head": ["Trump, Xi & Putin meet", "for the first time"],
        "sub": ["First-ever trilateral at APEC;", "nuclear arms on the table"],
        "motif": "flags",
    },
    {
        "kicker": "MARKETS",
        "color": (14, 107, 92),
        "head": ["Anthropic's $1.4tn", "Nasdaq debut"],
        "sub": ["Claude-maker starts trading", "as ANT, priced at $83"],
        "motif": "chart",
    },
    {
        "kicker": "GAMING",
        "color": (176, 106, 0),
        "head": ["GTA VI goes on sale", "worldwide"],
        "sub": ["Rockstar's epic lands after", "13 years; record pre-orders"],
        "motif": "vicecity",
    },
]

# (category, headline, subline) -- 32 stories, 16 per column.
ITEMS = [
    ("WORLD", "World court rules on Rohingya genocide",
     "ICJ delivers its verdict on Myanmar today"),
    ("WORLD", "Kerch Bridge hit a third time",
     "Traffic halted again as the key link crumbles"),
    ("WORLD", "Gulf war widens",
     "Iran drones hit US bases in Kuwait and Bahrain"),
    ("WORLD", "Israel's Gaza ground push",
     "Tanks cross Yellow Line; first move since truce"),
    ("WORLD", "Gaza floods wreck shelters",
     "6,000 tents destroyed; 150,000 stuck at border"),
    ("WORLD", "Drone war grinds on",
     "Russia and Ukraine trade strikes amid Abu Dhabi talks"),
    ("WORLD", "Estonia to shut Russia border",
     "Crossings close from December after security scare"),
    ("WORLD", "Takaichi meets Putin",
     "Japan PM raises detained journalist at APEC"),
    ("WORLD", "US-Venezuela rebuild ties",
     "Military cooperation restored, Hegseth says"),
    ("WORLD", "N. Korea enriches more uranium",
     "IAEA flags expansion of nuclear programme"),
    ("WORLD", "Canada sanctions settlers",
     "Measures target West Bank expansion"),
    ("WORLD", "Prague protests media law",
     "Hundreds of thousands defend press freedom"),
    ("WORLD", "Spain's general strike",
     "Ports and factories halted nationwide"),
    ("WORLD", "Trump: Russian diesel imports",
     "US to buy diesel after Putin call"),
    ("WORLD", "Hamas commander killed",
     "Senior figure dies in Israeli strike on Gaza"),
    ("US", "Liu Yunping makes history",
     "First Taiwanese American to chair House Dem caucus"),
    ("US", "Trump vs Vance rift",
     "President 'unhappy' VP did not back Iran war"),
    ("US", "Senators warn on AI cyber threat",
     "Attacks outpacing US defences, White House told"),
    ("BUSINESS", "Fed: more hikes likely",
     "Minutes point to rises; Waller floats 50bp in Dec"),
    ("BUSINESS", "Markets slide on hike fears",
     "Gold at 1-year low; bitcoin nears $62,000"),
    ("BUSINESS", "Oil falls 3%",
     "WTI closes at $83.26 as Gulf fears ease"),
    ("BUSINESS", "IMF lifts Germany forecast",
     "Growth now seen at 1.3% this year"),
    ("BUSINESS", "EU backs Indonesia trade pact",
     "Deal to blunt impact of US tariffs"),
    ("BUSINESS", "Microsoft eyes ByteDance deal",
     "Talks to sell AI services; House seeks briefing"),
    ("TECH", "Nvidia halts China chip sales",
     "H-series shipments stop; Kress promises early raises"),
    ("TECH", "NSA outage hits intel links",
     "Middle East feeds disrupted amid Iran war"),
    ("TECH", "Voyager 1 a light-day away",
     "NASA briefs world on farthest spacecraft today"),
    ("ASIA", "India-Japan defence talks",
     "2+2 dialogue opens in Tokyo"),
    ("ASIA", "Cyclone Akvan nears India",
     "Odisha braces as storm approaches east coast"),
    ("ASIA", "Delhi schools reopen",
     "Pollution curbs eased after GRAP III lifted"),
    ("HEALTH", "Kenya's second Ebola case",
     "Linked to first patient, officials confirm"),
    ("CLIMATE", "Istanbul floods kill three",
     "City hit by unprecedented deluge"),
]

TICKER = ("ALSO: Van Gogh's $190.4m record \u00b7 Stacy Keach dies at 85 \u00b7 "
          "Sindhu back in top five \u00b7 76ers beat Magic 121-116")
SOURCES = ("Stories first reported 19 November 2026 \u00b7 Sources: Reuters \u00b7 BBC \u00b7 "
           "AP \u00b7 AFP \u00b7 NASA \u00b7 Federal Reserve \u00b7 Sotheby's")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, fnt, max_w):
    """Truncate text with an ellipsis so it fits max_w pixels."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > max_w:
        text = text[:-1]
    return text + "\u2026"


def draw_flags(d, x, y, w, h):
    """Three small flags: USA, China, Russia."""
    fw, gap = 62, 14
    # USA: red/white stripes + blue canton
    fx = x
    for i in range(7):
        d.rectangle([fx, y + i * h // 7, fx + fw, y + (i + 1) * h // 7],
                    fill=(178, 34, 52) if i % 2 == 0 else WHITE)
    d.rectangle([fx, y, fx + fw * 0.45, y + h * 0.55], fill=(30, 50, 110))
    # China: red field, yellow stars
    fx += fw + gap
    d.rectangle([fx, y, fx + fw, y + h], fill=(222, 41, 16))
    d.ellipse([fx + 8, y + 7, fx + 18, y + 17], fill=(255, 222, 0))
    for sx, sy in ((34, 8), (44, 14), (44, 24), (34, 30)):
        d.ellipse([fx + sx, y + sy, fx + sx + 6, y + sy + 6], fill=(255, 222, 0))
    # Russia: white / blue / red horizontal stripes
    fx += fw + gap
    d.rectangle([fx, y, fx + fw, y + h // 3], fill=WHITE)
    d.rectangle([fx, y + h // 3, fx + fw, y + 2 * h // 3], fill=(0, 57, 166))
    d.rectangle([fx, y + 2 * h // 3, fx + fw, y + h], fill=(213, 0, 50))
    for fxx in (x, x + fw + gap, x + 2 * (fw + gap)):
        d.rectangle([fxx, y, fxx + fw, y + h], outline=(120, 116, 106))


def draw_chart(d, x, y, w, h):
    """A rising market line with an arrowhead."""
    d.line([(x, y + h - 6), (x, y + 4)], fill=HAIR, width=1)
    d.line([(x, y + h - 6), (x + w, y + h - 6)], fill=HAIR, width=1)
    pts = [(x + 4, y + h - 14), (x + 40, y + h - 26), (x + 70, y + h - 20),
           (x + 105, y + h - 38), (x + 140, y + h - 30), (x + 175, y + h - 52),
           (x + w - 8, y + 12)]
    d.line(pts, fill=(14, 107, 92), width=4, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 12, ey + 2), (ex - 4, ey + 12)], fill=(14, 107, 92))
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(14, 107, 92))


def draw_vicecity(d, x, y, w, h):
    """Sunset sun, skyline and a palm: a Vice City evening."""
    d.ellipse([x + w // 2 - 26, y + 2, x + w // 2 + 26, y + 54],
              fill=(232, 120, 40))
    # skyline
    base = y + h
    for bx, bw, bh in ((0, 34, 26), (40, 26, 40), (72, 30, 30), (108, 24, 46),
                       (138, 34, 24), (178, 26, 38), (212, 30, 28)):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(52, 44, 74))
    # palm trunk + fronds
    tx = x + w - 34
    d.line([(tx, base), (tx + 6, base - 46)], fill=(52, 44, 74), width=4)
    for dx, dy in ((-26, -12), (-20, -24), (-8, -30), (6, -28), (18, -18)):
        d.line([(tx + 6, base - 46), (tx + 6 + dx, base - 46 + dy)],
               fill=(52, 44, 74), width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    f_kick = font(BOLD, 15)
    f_title = font(BOLD, 44)
    f_strap = font(REG, 15)
    d.text((24, 18), "THE WORLD IN ONE IMAGE", font=f_kick, fill=RED)
    d.text((24, 40), "Thursday 19 November 2026", font=f_title, fill=INK)
    strap = ("Trump, Xi & Putin meet in Shenzhen  \u00b7  Anthropic's $1.4tn debut  "
             "\u00b7  GTA VI launches")
    d.text((24, 96), strap, font=f_strap, fill=MUTED)
    d.line([(24, 124), (1000, 124)], fill=INK, width=3)
    d.line([(24, 129), (1000, 129)], fill=INK, width=1)

    # ---- hero row: three stories ----
    f_hkick = font(BOLD, 12)
    f_hhead = font(BOLD, 19)
    f_hsub = font(REG, 13)
    hx, hy, hw, hh = 24, 140, 320, 170
    for i, hero in enumerate(HEROES):
        px = hx + i * (hw + 8)
        d.rectangle([px, hy, px + hw, hy + hh], fill=WHITE, outline=HAIR)
        d.rectangle([px, hy, px + hw, hy + 5], fill=hero["color"])
        d.text((px + 12, hy + 12), hero["kicker"], font=f_hkick,
               fill=hero["color"])
        mx, my, mw, mh = px + 12, hy + 32, hw - 24, 54
        if hero["motif"] == "flags":
            draw_flags(d, mx + 38, my + 4, mw, 42)
        elif hero["motif"] == "chart":
            draw_chart(d, mx + 18, my + 2, mw - 36, 50)
        else:
            draw_vicecity(d, mx + 18, my + 2, mw - 36, 50)
        yy = hy + 94
        for line in hero["head"]:
            d.text((px + 12, yy), line, font=f_hhead, fill=INK)
            yy += 23
        yy = hy + 140
        for line in hero["sub"]:
            d.text((px + 12, yy), line, font=f_hsub, fill=MUTED)
            yy += 16

    # ---- bulletin: two columns of 16 ----
    f_head = font(BOLD, 16)
    f_cat = font(BOLD, 12)
    f_sub = font(REG, 12)
    col_w, pitch = 476, 39
    y0 = 322
    for idx, (cat, head, sub) in enumerate(ITEMS):
        col = idx // 16
        row = idx % 16
        x = 24 + col * 500
        y = y0 + row * pitch
        color = CAT[cat]
        d.text((x, y), fit(d, head, f_head, col_w), font=f_head, fill=INK)
        d.text((x, y + 19), cat, font=f_cat, fill=color)
        cw = d.textlength(cat, font=f_cat)
        d.text((x + cw + 6, y + 19), fit(d, sub, f_sub, col_w - cw - 6),
               font=f_sub, fill=MUTED)

    # ---- footer ticker ----
    f_tick = font(BOLD, 14)
    f_src = font(REG, 11)
    d.line([(24, 954), (1000, 954)], fill=INK, width=2)
    d.text((24, 962), fit(d, TICKER, f_tick, 976), font=f_tick, fill=INK)
    d.text((24, 986), SOURCES, font=f_src, fill=MUTED)

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
