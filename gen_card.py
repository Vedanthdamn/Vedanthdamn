import json
import os
import html as htmllib
import requests

USERNAME = "Vedanthdamn"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# used only if no token is available (local testing without network/auth)
FALLBACK_STATS = {"repos": 20, "stars": 16, "commits": 531, "followers": 3}


def fetch_stats():
    """Pulls live repo/star/commit/follower counts from GitHub's GraphQL API."""
    if not TOKEN:
        return FALLBACK_STATS

    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        followers { totalCount }
        repositories(first: 100, after: $cursor, ownerAffiliations: [OWNER]) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes { stargazerCount }
        }
        contributionsCollection {
          contributionCalendar { totalContributions }
        }
      }
    }
    """
    cursor = None
    stars = 0
    repos_total = 0
    followers = 0
    commits = 0
    while True:
        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"login": USERNAME, "cursor": cursor}},
            headers={"Authorization": f"bearer {TOKEN}"},
        )
        resp.raise_for_status()
        payload = resp.json()
        if "errors" in payload:
            raise RuntimeError(payload["errors"])
        u = payload["data"]["user"]
        followers = u["followers"]["totalCount"]
        commits = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        repos_total = u["repositories"]["totalCount"]
        stars += sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
        page = u["repositories"]["pageInfo"]
        if page["hasNextPage"]:
            cursor = page["endCursor"]
        else:
            break
    return {"repos": repos_total, "stars": stars, "commits": commits, "followers": followers}


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

# a field renders on one line if it fits under this budget, otherwise
# label goes on its own line and the value wraps to an indented line below
WRAP_THRESHOLD = 34

GAP = "GAP"  # marker for a half-height spacer row between sections


def build_info(pal, stats):
    def field(key, value, number=False):
        label = key + ":"
        vcolor = pal["NUMBER"] if number else pal["VALUE"]
        if len(label) + 1 + len(value) <= WRAP_THRESHOLD:
            return [[(pal["LABEL"], label), (pal["DOTS"], "  "), (vcolor, value)]]
        return [
            [(pal["LABEL"], label)],
            [(pal["DOTS"], "  "), (vcolor, value)],
        ]

    info = []
    info.append([(pal["HEADER"], "vedanth@github")])
    info.append([(pal["RULE"], "-" * len("vedanth@github"))])
    info += field("OS", "macOS (MacBook Air M4), iPadOS, iOS")
    info += field("Host", "SRM Institute of Science & Tech")
    info += field("Kernel", "B.Tech CSE (AI & ML), Batch 2028")
    info += field("IDE", "VS Code, Claude Code, Xcode")
    info.append(GAP)
    info += field("Languages.Programming", "Python, TypeScript, JavaScript, C++, Swift")
    info += field("Languages.Frameworks", "React, Next.js, FastAPI, PyTorch")
    info += field("Languages.Real", "English")
    info.append(GAP)
    info += field("Hobbies", "Travel, creative writing, motorcycles")
    info.append(GAP)
    contact_hdr = "- Contact "
    info.append([(pal["SECTION"], contact_hdr + "-" * max(20 - len(contact_hdr), 3))])
    info += field("Email", "damavedanth@gmail.com")
    info += field("LinkedIn", "linkedin.com/in/vedanth-dama")
    info += field("GitHub", "Vedanthdamn")
    info.append(GAP)
    stats_hdr = "- GitHub Stats "
    info.append([(pal["SECTION"], stats_hdr + "-" * max(20 - len(stats_hdr), 3))])
    info += field("Repos", str(stats["repos"]), number=True)
    info += field("Stars", str(stats["stars"]), number=True)
    info += field("Commits", str(stats["commits"]), number=True)
    info += field("Followers", str(stats["followers"]), number=True)
    return info


# ---- SVG geometry ----
ART_FONT_SIZE = 15
ART_CHAR_W = ART_FONT_SIZE * 0.6
ART_LINE_H = ART_FONT_SIZE * 1.35
ART_WIDTH_PX = ART_COLS * ART_CHAR_W
ART_HEIGHT_PX = ART_ROWS * ART_LINE_H

PAD = 20
GAP_PX = 46
LINE_H_MULT = 1.28
GAP_ROW_MULT = 0.45  # spacer rows between sections are shorter than a text row

STATS = fetch_stats()
_sample_info = build_info(PALETTES["dark"], STATS)


def info_row_heights(info, font_size):
    line_h = font_size * LINE_H_MULT
    return [line_h * GAP_ROW_MULT if row == GAP else line_h for row in info]


def fit_info_font_size(info, target_height_px, start=24, min_size=14):
    """Shrinks the info font until its total rendered height fits within target_height_px."""
    for size in range(start, min_size - 1, -1):
        total = sum(info_row_heights(info, size))
        if total <= target_height_px:
            return size
    return min_size


INFO_FONT_SIZE = fit_info_font_size(_sample_info, ART_HEIGHT_PX)
INFO_CHAR_W = INFO_FONT_SIZE * 0.6
_row_heights = info_row_heights(_sample_info, INFO_FONT_SIZE)
INFO_HEIGHT_PX = sum(_row_heights)
info_col_w_px = max((sum(len(t) for _, t in line) for line in _sample_info if line != GAP), default=0) * INFO_CHAR_W

WIDTH = PAD * 2 + ART_WIDTH_PX + GAP_PX + info_col_w_px
HEIGHT = PAD * 2 + max(ART_HEIGHT_PX, INFO_HEIGHT_PX)


def esc(s):
    return htmllib.escape(s, quote=False).replace(" ", "&#160;")


def build_svg(mode):
    pal = PALETTES[mode]
    art_runs = art_for_mode(mode)
    info = build_info(pal, STATS)

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH:.0f}" height="{HEIGHT:.0f}" viewBox="0 0 {WIDTH:.0f} {HEIGHT:.0f}">')
    parts.append(f'<rect width="100%" height="100%" fill="{pal["BG"]}" rx="10"/>')

    parts.append(f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{ART_FONT_SIZE}px" xml:space="preserve">')
    for r in range(ART_ROWS):
        y = PAD + (r + 1) * ART_LINE_H - ART_LINE_H * 0.28
        parts.append(f'<text x="{PAD:.1f}" y="{y:.1f}">')
        for color, text in art_runs[r]:
            if text:
                parts.append(f'<tspan fill="{color}">{esc(text)}</tspan>')
        parts.append('</text>')
    parts.append('</g>')

    info_x = PAD + ART_WIDTH_PX + GAP_PX
    parts.append(f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{INFO_FONT_SIZE}px" font-weight="600" xml:space="preserve">')
    row_heights = info_row_heights(info, INFO_FONT_SIZE)
    cursor_y = PAD
    for row, h in zip(info, row_heights):
        cursor_y += h
        if row != GAP:
            y = cursor_y - h * 0.28
            parts.append(f'<text x="{info_x:.1f}" y="{y:.1f}">')
            for color, text in row:
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

print("stats", STATS)
print("WIDTH", WIDTH, "HEIGHT", HEIGHT, "ART_HEIGHT_PX", round(ART_HEIGHT_PX), "INFO_HEIGHT_PX", round(INFO_HEIGHT_PX), "INFO_FONT_SIZE", INFO_FONT_SIZE)
