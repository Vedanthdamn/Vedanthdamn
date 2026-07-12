import json
import html as htmllib

with open("art_data.json") as f:
    ART_RUNS_ORIG = json.load(f)  # list of rows, each row = list of [color, text]

ART_ROWS = len(ART_RUNS_ORIG)
ART_COLS = max(sum(len(t) for _, t in row) for row in ART_RUNS_ORIG)

def darken_for_light(color, k=2.3):
    def ch(v):
        v = int(v, 16)
        return max(0, min(255, round(255 - (255 - v) * k)))
    r, g, b = ch(color[1:3]), ch(color[3:5]), ch(color[5:7])
    return f"#{r:02x}{g:02x}{b:02x}"

def art_for_mode(mode):
    if mode == "dark":
        return ART_RUNS_ORIG
    return [[(darken_for_light(c), t) for c, t in row] for row in ART_RUNS_ORIG]

PALETTES = {
    "dark": dict(LABEL="#e3b341", DOTS="#6e7681", VALUE="#c9d1d9", HEADER="#c9d1d9",
                 RULE="#6e7681", SECTION="#39c5cf", NUMBER="#e8c574", BG="#0d1117"),
    "light": dict(LABEL="#9a6700", DOTS="#8b949e", VALUE="#24292f", HEADER="#24292f",
                  RULE="#8b949e", SECTION="#0598a6", NUMBER="#9a6700", BG="#ffffff"),
}

def build_info(pal):
    def dotline(key, value, target=34, number=False):
        label = key + ":"
        dots_needed = max(target - len(label) - 1, 3)
        dots = "." * dots_needed
        vcolor = pal["NUMBER"] if number else pal["VALUE"]
        return [(pal["LABEL"], label), (pal["DOTS"], " " + dots + " "), (vcolor, value)]

    info = []
    info.append([(pal["HEADER"], "vedanth@github")])
    info.append([(pal["RULE"], "-" * len("vedanth@github"))])
    info.append(dotline("OS", "macOS (MacBook Air M4), iPadOS, iOS"))
    info.append(dotline("Host", "SRM Institute of Science & Tech"))
    info.append(dotline("Kernel", "B.Tech CSE (AI & ML), Batch 2028"))
    info.append(dotline("IDE", "VS Code, Claude Code, Xcode"))
    info.append([])
    info.append(dotline("Languages.Programming", "Python, TypeScript, JavaScript, C++, Swift"))
    info.append(dotline("Languages.Frameworks", "React, Next.js, FastAPI, PyTorch"))
    info.append(dotline("Languages.Real", "English"))
    info.append([])
    info.append(dotline("Hobbies", "Travel, creative writing, motorcycles"))
    info.append([])
    contact_hdr = "- Contact "
    info.append([(pal["SECTION"], contact_hdr + "-" * max(34 - len(contact_hdr), 3))])
    info.append(dotline("Email", "damavedanth@gmail.com"))
    info.append(dotline("LinkedIn", "linkedin.com/in/vedanth-dama"))
    info.append(dotline("GitHub", "Vedanthdamn"))
    info.append([])
    stats_hdr = "- GitHub Stats "
    info.append([(pal["SECTION"], stats_hdr + "-" * max(34 - len(stats_hdr), 3))])
    info.append(dotline("Repos", "20", number=True))
    info.append(dotline("Stars", "16", number=True))
    info.append(dotline("Commits", "403", number=True))
    info.append(dotline("Followers", "3", number=True))
    return info

# ---- SVG geometry (shared across modes) ----
FONT_SIZE = 15
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.35
PAD = 18
GAP_COLS = 3

_sample_info = build_info(PALETTES["dark"])
INFO_ROWS = len(_sample_info)
TOTAL_ROWS = max(ART_ROWS, INFO_ROWS)
info_col_w = max((sum(len(t) for _, t in line) for line in _sample_info), default=0)
TOTAL_COLS = ART_COLS + GAP_COLS + info_col_w

WIDTH = PAD * 2 + TOTAL_COLS * CHAR_W
HEIGHT = PAD * 2 + TOTAL_ROWS * LINE_H

def esc(s):
    return htmllib.escape(s, quote=False).replace(" ", "&#160;")

def build_svg(mode):
    pal = PALETTES[mode]
    art_runs = art_for_mode(mode)
    info = build_info(pal)

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH:.0f}" height="{HEIGHT:.0f}" viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}">')
    parts.append(f'<rect width="100%" height="100%" fill="{pal["BG"]}" rx="10"/>')
    parts.append(f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{FONT_SIZE}px" xml:space="preserve">')

    info_x = PAD + (ART_COLS + GAP_COLS) * CHAR_W
    for r in range(TOTAL_ROWS):
        y = PAD + (r + 1) * LINE_H - LINE_H * 0.28
        if r < ART_ROWS:
            parts.append(f'<text x="{PAD:.1f}" y="{y:.1f}">')
            for color, text in art_runs[r]:
                if text:
                    parts.append(f'<tspan fill="{color}">{esc(text)}</tspan>')
            parts.append('</text>')
        if r < INFO_ROWS and info[r]:
            parts.append(f'<text x="{info_x:.1f}" y="{y:.1f}">')
            for color, text in info[r]:
                if text:
                    parts.append(f'<tspan fill="{color}">{esc(text)}</tspan>')
            parts.append('</text>')

    parts.append('</g>')
    parts.append('</svg>')
    return "".join(parts)

with open("dark_mode.svg", "w") as f:
    f.write(build_svg("dark"))
with open("light_mode.svg", "w") as f:
    f.write(build_svg("light"))

print("WIDTH", WIDTH, "HEIGHT", HEIGHT, "ART_COLS", ART_COLS, "ART_ROWS", ART_ROWS, "INFO_ROWS", INFO_ROWS, "info_col_w", info_col_w)
