"""Render self-contained, animated SVG cards for the profile README.

No third-party Python packages are required. The daily GitHub Action fetches the
public contribution calendar with GraphQL and commits the generated SVGs.
Use STATIC=1 to preview the final animation frame without waiting.
"""

from __future__ import annotations

import base64
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
USER = "ansaganakhat"
STATIC = os.getenv("STATIC") == "1"
INK = "#EAF4FF"
MUTED = "#A8B9CE"
TEAL = "#5CE5C4"
BLUE = "#80AFFF"
AMBER = "#FFC184"


def xml(text: object) -> str:
    return escape(str(text), {'"': '&quot;'})


def font_css() -> str:
    rules = []
    for weight, filename in ((400, "sans-regular.woff"), (700, "sans-bold.woff")):
        font = ROOT / "fonts" / filename
        if font.exists():
            payload = base64.b64encode(font.read_bytes()).decode("ascii")
            rules.append(
                "@font-face{font-family:ProfileSans;font-style:normal;"
                f"font-weight:{weight};src:url(data:font/woff;base64,{payload}) format('woff')}}"
            )
    return "\n".join(rules)


CSS = """
text{font-family:ProfileSans,DejaVu Sans,Arial,sans-serif;fill:#EAF4FF}
.label{font-size:16px;font-weight:700;letter-spacing:3px;fill:#A8B9CE}
.muted{fill:#A8B9CE}.bold{font-weight:700}
.rise{animation:rise .8s cubic-bezier(.2,.75,.2,1) both}
.pop{animation:pop .55s cubic-bezier(.17,.8,.25,1.3) both}
.bar{transform-box:fill-box;transform-origin:center bottom;animation:bar .75s ease-out both}
.pulse{animation:pulse 3s ease-in-out infinite}
.dash{stroke-dasharray:8 12;animation:dash 10s linear infinite}
@keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}
@keyframes bar{from{transform:scaleY(.03)}to{transform:scaleY(1)}}
@keyframes pulse{50%{opacity:.38;transform:scale(1.08)}}
@keyframes dash{to{stroke-dashoffset:-80}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(width: int, height: int, title: str, body: str, extra: str = "") -> str:
    style = font_css() + CSS + ("\n*{animation:none!important}" if STATIC else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{xml(title)}">
<title>{xml(title)}</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101B30"/><stop offset="1" stop-color="#0B1220"/></linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#5CE5C4"/><stop offset=".55" stop-color="#80AFFF"/><stop offset="1" stop-color="#C49CFF"/></linearGradient>
  <linearGradient id="soft" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#5CE5C4" stop-opacity=".22"/><stop offset="1" stop-color="#80AFFF" stop-opacity="0"/></linearGradient>
  {extra}
</defs>
<style><![CDATA[{style}]]></style>
<rect width="{width}" height="{height}" rx="26" fill="url(#bg)"/>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="25" fill="none" stroke="#2A3D57"/>
{body}
</svg>'''


def save(name: str, content: str) -> None:
    CARDS.mkdir(parents=True, exist_ok=True)
    (CARDS / name).write_text(content + "\n", encoding="utf-8")


def header(label: str, width: int) -> str:
    return f'''<circle cx="34" cy="34" r="5" fill="#5CE5C4"/><circle cx="52" cy="34" r="5" fill="#80AFFF"/>
<circle cx="70" cy="34" r="5" fill="#FFC184"/>
<path d="M28 59H{width-28}" stroke="#2A3D57"/>
<text x="30" y="87" class="label">{xml(label)}</text>'''


def hero() -> None:
    grid = "".join(f'<path d="M{x} 0V360" stroke="#253A51" opacity=".25"/>' for x in range(40, 1200, 54))
    dots = "".join(f'<circle cx="{948+i*30}" cy="{60+j*30}" r="2" fill="#80AFFF" opacity=".28"/>' for i in range(7) for j in range(6))
    body = f'''<g>{grid}</g><circle cx="1030" cy="175" r="190" fill="url(#soft)"/>
<path d="M24 66H1176" stroke="#324760"/>
<circle cx="45" cy="36" r="5" fill="#5CE5C4"/><circle cx="64" cy="36" r="5" fill="#80AFFF"/><circle cx="83" cy="36" r="5" fill="#FFC184"/>
<text x="108" y="42" font-size="14" fill="#A8B9CE">ansaganakhat / profile</text>
<text x="1136" y="42" text-anchor="end" font-size="13" fill="#5CE5C4">● BUILDING IN PUBLIC</text>
<g class="rise" style="animation-delay:.1s"><text x="56" y="150" class="label" fill="#5CE5C4">HELLO, I AM</text>
<text x="52" y="233" font-size="76" class="bold" letter-spacing="-3">ANSAGAN <tspan fill="url(#shine)">AKHAT</tspan></text></g>
<g class="rise" style="animation-delay:.35s"><text x="56" y="274" font-size="23">I build useful tools for learning and everyday life.</text>
<text x="56" y="310" font-size="16" class="muted">AI  /  COMPUTER VISION  /  INTERACTIVE WEB</text></g>
<g>{dots}</g>
<g transform="translate(1024 191)"><circle r="79" fill="none" stroke="#3F6881" stroke-width="2" class="dash"/>
<circle r="54" fill="#13283A" stroke="#5CE5C4" stroke-width="3"/>
<path d="M-37 0Q0-39 37 0Q0 39-37 0Z" fill="none" stroke="#80AFFF" stroke-width="5"/>
<circle r="13" fill="#5CE5C4" class="pulse"/></g>
<path d="M56 329H766" stroke="url(#shine)" stroke-width="3" opacity=".7"/>'''
    save("hero.svg", svg(1200, 360, "Ansagan Akhat — AI, vision and learning tools", body))


TILES = [
    ("vision", "01", "COMPUTER", "VISION", "Camera-based prototypes", TEAL, "eye"),
    ("learning", "02", "LEARNING", "TOOLS", "Practice that feels interactive", BLUE, "book"),
    ("web", "03", "CAMPUS", "SERVICES", "Digital university services", AMBER, "cube"),
]


def tile_icon(kind: str, color: str) -> str:
    if kind == "eye":
        path = '<path d="M-30 0Q0-30 30 0Q0 30-30 0Z"/><circle r="10"/>'
    elif kind == "book":
        path = '<path d="M0-21Q-18-30-29-22V21Q-13 14 0 24Q13 14 29 21V-22Q18-30 0-21Z"/><path d="M0-21V24"/>'
    else:
        path = '<path d="M0-27 25-14 25 14 0 27-25 14-25-14Z"/><path d="M-25-14 0 0 25-14M0 0V27"/>'
    return f'<g transform="translate(315 65)" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" class="pulse">{path}</g>'


def tiles() -> None:
    for index, (key, number, a, b, caption, color, icon) in enumerate(TILES):
        body = f'''<rect x="14" y="14" width="362" height="212" rx="20" fill="{color}" opacity=".035" stroke="{color}" stroke-opacity=".38"/>
<path d="M28 45H185" stroke="{color}" stroke-width="3"/>
<text x="30" y="86" class="label" fill="{color}">FIELD / {number}</text>
{tile_icon(icon, color)}
<g class="rise" style="animation-delay:{.8 + index*.16:.2f}s">
<text x="28" y="139" font-size="34" class="bold">{a}</text>
<text x="28" y="178" font-size="34" class="bold" fill="{color}">{b}</text>
<text x="29" y="210" font-size="15" class="muted">{xml(caption)}</text></g>
<path d="M345 193l12 0m-6-6 6 6-6 6" stroke="{color}" fill="none" stroke-width="2"/>'''
        save(f"tile-{key}.svg", svg(390, 240, f"{a} {b}: {caption}", body))


PROJECTS = [
    ("codequest", "CODEQUEST AI", "Learning platform", "Teachers, parents, classes and interactive quizzes", "React  /  Python  /  Firebase", TEAL, "01"),
    ("idsai", "IDSAI STUDENT SERVICES", "Campus services platform", "Forms, schedules and room bookings", "Web  /  Firebase  /  Vercel", BLUE, "02"),
    ("vision", "CLASS SLEEP MONITOR", "Computer vision prototype", "Eye tracking and closed-eye detection in class", "Python  /  OpenCV  /  MediaPipe", AMBER, "03"),
    ("algorithms", "ALGORITHM QUIZ LAB", "Practice and exam prep", "300 questions across algorithms and data structures", "Web  /  PWA  /  GitHub Pages", "#C49CFF", "04"),
]


def projects() -> None:
    for index, (key, title, subtitle, description, stack, color, number) in enumerate(PROJECTS):
        body = f'''{header("SELECTED WORK  /  " + number, 580)}
<rect x="30" y="105" width="6" height="116" rx="3" fill="{color}"/>
<g class="rise" style="animation-delay:{1.35 + index*.12:.2f}s">
<text x="56" y="151" font-size="27" class="bold">{xml(title)}</text>
<text x="56" y="184" font-size="19" fill="{color}">{xml(subtitle)}</text>
<text x="56" y="216" font-size="15" class="muted">{xml(description)}</text>
<text x="56" y="259" font-size="15" class="muted">{xml(stack)}</text></g>
<circle cx="515" cy="253" r="24" fill="none" stroke="{color}" opacity=".7"/>
<path d="M507 253h16m-7-7 7 7-7 7" stroke="{color}" fill="none" stroke-width="2"/>'''
        save(f"project-{key}.svg", svg(580, 286, f"{title}: {description}", body))


def fetch_contributions() -> dict | None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else None
    query = '''query($login:String!){user(login:$login){contributionsCollection{
      contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}
    }}}'''
    req = Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-readme-cards"},
        method="POST",
    )
    with urlopen(req, timeout=25) as response:
        result = json.load(response)
    if result.get("errors"):
        raise RuntimeError(f"GitHub GraphQL returned errors: {result['errors']}")
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    data = {"totalContributions": calendar["totalContributions"], "days": days}
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    return data


def activity(data: dict | None) -> None:
    days = data.get("days", []) if data else []
    monthly: dict[str, int] = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["contributionCount"]
    today = date.today()
    months = []
    for offset in range(11, -1, -1):
        year = today.year + (today.month - 1 - offset) // 12
        month = (today.month - 1 - offset) % 12 + 1
        months.append(f"{year:04d}-{month:02d}")
    counts = [monthly[key] for key in months]
    best = max(counts, default=0)
    total = data.get("totalContributions", 0) if data else 0
    active = sum(day["contributionCount"] > 0 for day in days)
    summary = f"{total} PUBLIC CONTRIBUTIONS   /   {active} ACTIVE DAYS" if data else "PUBLIC ACTIVITY  /  SYNCING FROM GITHUB"
    body = header("GITHUB ACTIVITY  /  MONTH BY MONTH", 1200)
    body += f'<text x="30" y="125" font-size="18" class="muted">{xml(summary)}</text>'
    bars = []
    for i, (month, count) in enumerate(zip(months, counts)):
        x = 57 + i * 94
        height = max(6, round(count / best * 102)) if best else 6
        color = BLUE if count == best and best else TEAL
        bars.append(f'<rect x="{x}" y="{252-height}" width="48" height="{height}" rx="7" fill="{color}" opacity=".85" class="bar" style="animation-delay:{1.8+i*.07:.2f}s"/>')
        bars.append(f'<text x="{x+24}" y="273" font-size="14" text-anchor="middle" class="muted">{datetime.strptime(month, "%Y-%m").strftime("%b").upper()}</text>')
        if count:
            bars.append(f'<text x="{x+24}" y="{243-height}" font-size="14" text-anchor="middle" fill="{color}">{count}</text>')
    body += '<path d="M35 253H1165" stroke="#35516A"/>' + "".join(bars)
    save("activity.svg", svg(1200, 295, "Monthly GitHub contributions", body))


def graph(data: dict | None) -> None:
    days = data.get("days", []) if data else []
    total = data.get("totalContributions", 0) if data else 0
    active = sum(day["contributionCount"] > 0 for day in days)
    best_day = max(days, key=lambda day: day["contributionCount"], default=None)
    longest = current = 0
    for day in days:
        current = current + 1 if day["contributionCount"] else 0
        longest = max(longest, current)

    body = header("CONTRIBUTION CALENDAR  /  LAST 12 MONTHS", 1200)
    body += '''<g class="rise" style="animation-delay:1.95s">
<text x="30" y="142" font-size="35" class="bold">A YEAR IN <tspan fill="url(#shine)">PIXELS</tspan></text>
<text x="32" y="174" font-size="16" class="muted">Every square is a real day of building on GitHub.</text></g>
<circle cx="1000" cy="159" r="99" fill="url(#eye-glow)"/>
<path d="M855 161 Q1000 50 1145 161 Q1000 272 855 161Z" fill="none" stroke="url(#shine)" stroke-width="2.5" opacity=".8"/>
<path d="M883 161 Q1000 79 1117 161 Q1000 243 883 161Z" fill="none" stroke="#80AFFF" opacity=".38"/>
<circle cx="1000" cy="161" r="52" fill="#10293A" stroke="#5CE5C4" stroke-width="2"/>
<circle cx="1000" cy="161" r="27" fill="#183F4C" stroke="#80AFFF" stroke-width="2"/>
<circle cx="1000" cy="161" r="12" fill="#5CE5C4" class="pulse"/>
<path d="M855 161H827L809 143H792M1145 161h27M1000 109V87l18-18h38M1000 213v21l-15 14h-49" fill="none" stroke="#5CE5C4" stroke-width="1.5" opacity=".5"/>
<circle cx="792" cy="143" r="3" fill="#5CE5C4"/><circle cx="1056" cy="69" r="3" fill="#80AFFF"/>
<circle cx="936" cy="248" r="3" fill="#5CE5C4"/><circle cx="1172" cy="161" r="3" fill="#80AFFF"/>'''

    busiest = (
        f'{best_day["contributionCount"]} / {datetime.strptime(best_day["date"], "%Y-%m-%d").strftime("%d %b").upper()}'
        if best_day and best_day["contributionCount"] else "0 / —"
    )
    stats = [
        (str(total), "CONTRIBUTIONS"),
        (str(active), "ACTIVE DAYS"),
        (str(longest), "BEST STREAK / DAYS"),
        (busiest, "BUSIEST DAY"),
    ]
    for i, (value, label) in enumerate(stats):
        x = 30 + i * 191
        body += f'''<g class="rise" style="animation-delay:{2.05+i*.09:.2f}s">
<rect x="{x}" y="189" width="180" height="57" rx="12" fill="#142438" stroke="#34536A"/>
<path d="M{x+1} 202V226" stroke="{TEAL if i < 2 else BLUE}" stroke-width="3"/>
<text x="{x+13}" y="215" font-size="17" class="bold">{xml(value)}</text>
<text x="{x+13}" y="235" font-size="10" class="muted" letter-spacing="1.3">{label}</text></g>'''

    body += '''<rect x="28" y="276" width="1144" height="166" rx="17" fill="#0B1726" stroke="#2A4158"/>
<path d="M88 284V433" stroke="#2A4158"/>
<text x="40" y="307" font-size="12" class="muted">SUN</text>
<text x="40" y="364" font-size="12" class="muted">WED</text>
<text x="40" y="421" font-size="12" class="muted">SAT</text>'''
    if days:
        first = date.fromisoformat(days[0]["date"])
        first_sunday = first - timedelta(days=(first.weekday() + 1) % 7)
        day_map = {entry["date"]: entry["contributionCount"] for entry in days}
        last = date.fromisoformat(days[-1]["date"])
        d = first_sunday
        cells = []
        last_month = None
        while d <= last:
            col = (d - first_sunday).days // 7
            row = (d.weekday() + 1) % 7
            if d == first_sunday or d.day == 1:
                label_date = first if d == first_sunday else d
                label_month = (label_date.year, label_date.month)
                if label_month != last_month and col < 54:
                    cells.append(f'<text x="{102+col*19}" y="268" font-size="12" class="muted">{label_date.strftime("%b").upper()}</text>')
                    last_month = label_month
            count = day_map.get(d.isoformat())
            if count is not None:
                level = 0 if count == 0 else 1 if count == 1 else 2 if count <= 3 else 3 if count <= 7 else 4
                color = ("#1C2D3F", "#245B61", "#348E83", "#42BDA5", TEAL)[level]
                cells.append(f'<rect x="{102+col*19}" y="{292+row*19}" width="14" height="14" rx="3" fill="{color}" class="pop" style="animation-delay:{2.35+col*.017:.2f}s"><title>{d.isoformat()}: {count} contributions</title></rect>')
            d += timedelta(days=1)
        body += "".join(cells)
    else:
        body += '<text x="350" y="370" font-size="20" class="muted">Activity graph updates automatically every day</text>'
    body += '<text x="30" y="472" font-size="13" class="muted">LIVE CONTRIBUTION DATA  /  REFRESHED DAILY</text>'
    body += '<text x="931" y="472" font-size="13" class="muted">LESS</text>'
    for i, color in enumerate(("#1C2D3F", "#245B61", "#348E83", "#42BDA5", TEAL)):
        body += f'<rect x="{970+i*21}" y="459" width="13" height="13" rx="3" fill="{color}"/>'
    body += '<text x="1085" y="472" font-size="13" class="muted">MORE</text>'
    extra = '<radialGradient id="eye-glow"><stop stop-color="#5CE5C4" stop-opacity=".23"/><stop offset="1" stop-color="#5CE5C4" stop-opacity="0"/></radialGradient>'
    save("graph.svg", svg(1200, 490, "A year in pixels — real GitHub contribution calendar", body, extra))


def main() -> None:
    hero()
    tiles()
    projects()
    data = fetch_contributions()
    activity(data)
    graph(data)
    print(f"Rendered {len(list(CARDS.glob('*.svg')))} SVG cards")


if __name__ == "__main__":
    main()
