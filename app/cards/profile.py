"""Hero, about, tech stack, what-I-build, collaborate, headings and buttons."""

from __future__ import annotations

from datetime import datetime, timezone

from .. import config
from .. import github as gh
from .theme import (AMBER, BLUE, BORDER, CARD2, ETH, FESTIVAL_CSS, FESTIVALS, GREEN, GROUND_FESTIVALS, LOW_SUN, MUTED, ORANGE,
                    SKIES, TEXT, bullet_list, celestial, compact, count_badge, cube, d, dot, esc, festival_ground,
                    festival_sky, festival_today, frame, heading, ist_now, panel, phase_label, sky, sky_phase, skyline, stars, svg,
                    synced, wrap)

P = config.PROFILE


def _years(user: dict) -> int:
    if P.get("years_experience"):
        return int(P["years_experience"])
    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    return max(1, (datetime.now(timezone.utc) - created).days // 365)


# ---------------------------------------------------------------- hero

def hero(user: dict) -> str:
    W, H = 850, 330
    phase, fest = sky_phase(), festival_today()
    b = frame(W, H) + sky(1, 1, W - 2, H - 2, phase)
    # sky for the current time (and festival) in India + skyline behind the right column
    b += f'<circle cx="690" cy="300" r="140" fill="{SKIES[phase][1]}" fill-opacity=".10" filter="url(#softglow)" class="glowpulse"/>'
    if phase == "night":
        b += stars(412, 10, 130, 200, n=22, seed=11)
    if fest != "eid":  # Eid brings its own crescent
        b += f'<g class="fade" {d(.4)}>{celestial(482, 150 if phase in LOW_SUN else 64, phase)}</g>'
    if fest:
        b += festival_sky(fest, 395, 12, 145, 195, seed=11)
    lit, colors = (FESTIVALS[fest][2], FESTIVALS[fest][1]) if fest else (SKIES[phase][3], None)
    b += skyline(380, H - 1, 468, seed=11, opacity=.55, max_h=110, lit=lit, colors=colors)
    if fest in GROUND_FESTIVALS:
        b += festival_ground(fest, 560, H - 14, 280, n=14)
    b += f'<rect x="1" y="{H - 60}" width="{W - 2}" height="59" rx="14" fill="url(#emberg)"/>'

    first, _, rest = user["name"].partition(" ")
    name = (f'<tspan>{esc(first)} </tspan><tspan fill="url(#og)">{esc(rest)}</tspan>' if rest
            else f'<tspan fill="url(#og)">{esc(first)}</tspan>')
    greeting = {"morning": "Suprabhat ☀", "afternoon": "Namaste 🙏", "evening": "Shubh Sandhya 🪔",
                "night": "Shubh Ratri 🌙"}[phase]
    b += f'<text x="34" y="56" font-size="17" class="muted rise">{greeting} — I\'m</text>'
    b += f'<text x="32" y="102" font-size="44" font-weight="800" class="rise" {d(.15)} filter="url(#glow)">{name}</text>'
    b += f'<text x="34" y="134" font-size="19" font-weight="600" class="rise" {d(.3)}>{esc(P["role"])}</text>'
    for i, line in enumerate(wrap(P["tagline"], 66, 3)):
        b += f'<text x="34" y="{162 + i * 17}" font-size="12.5" class="muted rise" {d(.45 + i * .08)}>{esc(line)}</text>'

    x = 34
    for i, chip in enumerate(P["chips"]):
        w = len(chip) * 6.6 + 22
        hot = chip in P.get("highlight_chips", [])
        b += (f'<g class="pop" {d(.7 + i * .08)}><rect x="{x}" y="222" width="{w:.0f}" height="24" rx="6" '
              + (f'fill="{ETH}" fill-opacity=".16" stroke="{ETH}" filter="url(#glow)" class="glowpulse"/>' if hot
                 else f'fill="{CARD2}" stroke="{BORDER}"/>') +
              f'<text x="{x + w / 2:.0f}" y="238" text-anchor="middle" font-size="11" fill="{"#c9cbff" if hot else "#c9d1d9"}" '
              f'font-weight="{700 if hot else 400}">{esc(chip)}</text></g>')
        x += w + 8

    status = "Available for new opportunities" if P.get("available") else "Currently busy building"
    meta = [status]
    if user.get("location"):
        meta.append(user["location"])
    meta.append(f"GitHub since {user['created_at'][:4]}")
    x = 34
    for i, m in enumerate(meta):
        b += f'<g class="fade" {d(1 + i * .1)}>'
        b += dot(x + 4, 274, 3.5, GREEN if i == 0 else ORANGE, "pulse" if i == 0 else "")
        b += f'<text x="{x + 14}" y="278" font-size="11.5" fill="#c9d1d9">{esc(m)}</text></g>'
        x += len(m) * 6.3 + 34
    b += synced(34, 306, right=False)
    b += (f'<text x="{34 + len(f"live · {ist_now()}") * 5.75 + 22:.0f}" y="306" font-size="9.5" class="dim mono fade" {d(1.3)}>'
          f'· {esc(phase_label(phase, user.get("location", "")))}'
          + (f'<tspan fill="{AMBER}" font-weight="700"> · {esc(FESTIVALS[fest][0])}</tspan>' if fest else "") + '</text>')

    # terminal
    tx, ty, tw, th = 548, 24, 276, 152
    b += f'<g class="rise" {d(.3)}>' + panel(tx, ty, tw, th, 10, stroke="#2b3646", fill="#0a0e15")
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        b += f'<circle cx="{tx + 14 + i * 13}" cy="{ty + 13}" r="4" fill="{c}"/>'
    b += f'<text x="{tx + tw - 12}" y="{ty + 17}" text-anchor="end" font-size="9.5" class="dim mono">bash</text>'
    b += f'<line x1="{tx}" y1="{ty + 26}" x2="{tx + tw}" y2="{ty + 26}" stroke="#1d2633"/>'
    prompt = f"{user['login']}@dev:~$"
    b += (f'<text x="{tx + 12}" y="{ty + 46}" font-size="11" class="mono type" {d(.6)}>'
          f'<tspan fill="{GREEN}">{esc(prompt)}</tspan><tspan fill="{TEXT}"> cat focus.txt</tspan></text>')
    for i, line in enumerate(P["terminal_lines"][:5]):
        b += (f'<text x="{tx + 12}" y="{ty + 68 + i * 18}" font-size="11" class="mono fade" {d(1.6 + i * .35)}>'
              f'<tspan fill="{ORANGE}">&gt; </tspan><tspan fill="#c9d1d9">{esc(line)}</tspan></text>')
    last_y = ty + 68 + (min(5, len(P["terminal_lines"])) - 1) * 18
    end_x = tx + 12 + (len(P["terminal_lines"][-1]) + 2) * 6.65
    b += f'<rect x="{end_x:.0f}" y="{last_y - 10}" width="7" height="13" fill="{ORANGE}" class="blink"/></g>'

    # neon sign
    nx, ny, nw, nh = 548, 188, 276, 46
    b += f'<g class="rise" {d(.5)}>' + panel(nx, ny, nw, nh, 10, stroke=ORANGE, fill="#120b06", extra='stroke-opacity=".55"')
    words = P["neon_words"]
    fs, cw, gap = 12.5, 7.2, 10
    total = sum(len(w) for w in words) * cw + gap * (len(words) - 1)
    x = nx + (nw - total) / 2
    cycle = len(words) * 0.9
    for i, w in enumerate(words):
        b += (f'<text x="{x:.1f}" y="{ny + 28}" font-size="{fs}" font-weight="700" class="mono neon" fill="{AMBER}" textLength="{len(w) * cw:.1f}" lengthAdjust="spacingAndGlyphs" '
              f'filter="url(#glow)" style="animation-delay:{i * .9:.1f}s;animation-duration:{cycle:.1f}s">{esc(w)}</text>')
        x += len(w) * cw + gap
    b += "</g>"

    stats = (f"{user['public_repos']} repos  ·  {compact(user['followers'])} followers  ·  "
             f"{compact(user['following'])} following")
    b += f'<text x="{nx + nw / 2}" y="256" text-anchor="middle" font-size="11" class="mono ink fade" fill="#c9d1d9" {d(1.3)}>{esc(stats)}</text>'

    css = ("@keyframes neon{0%,100%{opacity:.3}8%,22%{opacity:1}34%{opacity:.3}}.neon{opacity:.3;animation:neon 4.5s ease-in-out infinite}"
           + FESTIVAL_CSS)
    return svg(W, H, b, css, title=f"{user['name']} - {P['role']}")


# ---------------------------------------------------------------- about

def about(user: dict, n: int = 2) -> str:
    W, H = 850, 300
    b = frame(W, H) + heading(24, 20, n, "About Me", P["about_subtitle"])

    for i, line in enumerate(wrap(P["about"], 46, 7)):
        b += f'<text x="24" y="{88 + i * 18}" font-size="12" fill="#c9d1d9" class="rise" {d(.2 + i * .06)}>{esc(line)}</text>'
    facts = []
    if user.get("location"):
        facts.append(("Based in", user["location"]))
    facts.append(("On GitHub since", user["created_at"][:4]))
    for i, (k, v) in enumerate(facts):
        y = 232 + i * 20
        b += (f'<text x="24" y="{y}" font-size="11" class="fade" {d(.8 + i * .1)}>'
              f'<tspan class="dim">{esc(k)}  </tspan><tspan fill="{AMBER}">{esc(v)}</tspan></text>')
    b += synced(24, 284, right=False)

    # stats
    tech_count = sum(len(v) for v in config.TECH_STACK.values())
    stats = [
        (f"{_years(user)}+", "Years", "Coding"),
        (str(user["public_repos"]), "Public", "Projects"),
        (f"{tech_count}+", "Tech", "Mastered"),
        ("Open" if P.get("available") else "Busy", "To New", "Opportunities"),
    ]
    sx = 318
    for i, (val, l1, l2) in enumerate(stats):
        x = sx + i * 84
        b += (f'<g class="pop" {d(.3 + i * .1)}>' + panel(x, 66, 76, 66, 9) +
              f'<text x="{x + 38}" y="{93}" text-anchor="middle" font-size="20" font-weight="800" fill="url(#og)">{esc(val)}</text>'
              f'<text x="{x + 38}" y="{110}" text-anchor="middle" font-size="9.5" class="muted">{esc(l1)}</text>'
              f'<text x="{x + 38}" y="{122}" text-anchor="middle" font-size="9.5" class="muted">{esc(l2)}</text></g>')

    palette = [ORANGE, BLUE, "#f0b72f", "#ff7b72", "#bc8cff", "#39c5cf"]
    for i, (title, desc) in enumerate(P["capabilities"][:6]):
        col, row = i % 3, i // 3
        x, y = sx + col * 111, 142 + row * 72
        c = palette[i % len(palette)]
        b += (f'<g class="rise" {d(.6 + i * .08)}>' + panel(x, y, 104, 64, 9) +
              f'<rect x="{x + 10}" y="{y + 10}" width="20" height="20" rx="5" fill="{c}" fill-opacity=".15" stroke="{c}" filter="url(#glow)"/>'
              f'<rect x="{x + 16}" y="{y + 16}" width="8" height="8" rx="2" fill="{c}"/>'
              f'<text x="{x + 10}" y="{y + 45}" font-size="10.5" font-weight="700">{esc(title)}</text>'
              f'<text x="{x + 10}" y="{y + 57}" font-size="8.6" class="muted">{esc(desc)}</text></g>')

    # globe
    cx, cy, r = 748, 96, 52
    g = f'<g class="fade" {d(.4)}>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="{ORANGE}" fill-opacity=".12" filter="url(#softglow)" class="glowpulse"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0c1018" stroke="{ORANGE}" stroke-opacity=".8" filter="url(#glow)"/>'
    for k in (-0.6, -0.3, 0, 0.3, 0.6):
        yy = cy + k * r
        rx = (r * r - (k * r) ** 2) ** .5
        g += f'<ellipse cx="{cx}" cy="{yy:.1f}" rx="{rx:.1f}" ry="{rx * .18:.1f}" stroke="{ORANGE}" stroke-opacity=".3"/>'
    for i in range(4):
        g += (f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r}" stroke="{AMBER}" stroke-opacity=".45">'
              f'<animate attributeName="rx" values="{r};0;{r}" dur="8s" begin="{-i * 2}s" repeatCount="indefinite"/></ellipse>')
    for i, (ax, ay) in enumerate(((-20, -18), (14, -30), (26, 8), (-6, 22), (-32, 6), (8, -4))):
        g += f'<circle cx="{cx + ax}" cy="{cy + ay}" r="2.2" fill="{AMBER}" class="twinkle" style="animation-delay:{i * .5}s"/>'
    orbit = f"M{cx - r - 16},{cy} a{r + 16},{(r + 16) * .32} 0 1,0 {2 * (r + 16)},0 a{r + 16},{(r + 16) * .32} 0 1,0 {-2 * (r + 16)},0"
    g += f'<path d="{orbit}" stroke="{ORANGE}" stroke-opacity=".35" stroke-dasharray="3 5"/>'
    g += f'<circle r="3.5" fill="{AMBER}" filter="url(#glow)"><animateMotion dur="6s" repeatCount="indefinite" path="{orbit}"/></circle>'
    b += g + "</g>"
    b += bullet_list(672, 182, P["highlights"][:6], gap=17.5, size=11)
    return svg(W, H, b, title="About Me")


# ----------------------------------------------------------- tech stack

def _tile(x, y, name, label, color, delay, repos=0):
    fs = 15 if len(label) <= 2 else 11.5
    short = name if len(name) <= 9 else name[:8] + "…"
    return (f'<g class="pop" {d(delay)}>'
            f'<rect x="{x}" y="{y}" width="38" height="38" rx="9" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".75"/>'
            f'<text x="{x + 19}" y="{y + 19 + fs * .36:.1f}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="{color}">{esc(label)}</text>'
            f'<text x="{x + 19}" y="{y + 51}" text-anchor="middle" font-size="9" class="muted">{esc(short)}</text>'
            f'{count_badge(x + 37, y + 1, repos)}</g>')


def tech_stack(tech: dict, n: int = 3) -> str:
    W = 850
    cats = [(cat, [(name, label, color, gh.tech_count(tech, name)) for name, label, color in items])
            for cat, items in config.TECH_STACK.items()]
    used = len(tech["repos"])
    rows = max((len(items) + 2) // 3 for _, items in cats)
    ph = 40 + rows * 62
    H = 76 + ph + 18
    b = frame(W, H) + heading(24, 20, n, "Tech Stack", f"Tools & technologies I work with · scanned {used} repos")

    tabs = ["All"] + [c for c, _ in cats]
    x = W - 24
    for i, t in enumerate(reversed(tabs)):
        w = len(t) * 6.2 + 20
        x -= w
        active = t == "All"
        b += (f'<g class="fade" {d(.2)}><rect x="{x:.0f}" y="26" width="{w:.0f}" height="22" rx="6" '
              f'fill="{ORANGE if active else CARD2}" fill-opacity="{1 if active else .9}" stroke="{ORANGE if active else BORDER}"/>'
              f'<text x="{x + w / 2:.0f}" y="41" text-anchor="middle" font-size="10.5" fill="{"#1a0d02" if active else MUTED}" '
              f'font-weight="{700 if active else 400}">{esc(t)}</text></g>')
        x -= 6

    gap = 10
    cw = (W - 48 - gap * (len(cats) - 1)) / len(cats)
    k = 0
    for ci, (cat, items) in enumerate(cats):
        x0 = 24 + ci * (cw + gap)
        b += f'<g class="rise" {d(.1 + ci * .1)}>' + panel(round(x0), 76, round(cw), ph, 10)
        b += f'<text x="{x0 + 12:.0f}" y="98" font-size="12" font-weight="700">{esc(cat)}</text>'
        b += f'<rect x="{x0 + 12:.0f}" y="104" width="22" height="2" rx="1" fill="{ORANGE}"/></g>'
        inner = (cw - 3 * 38) / 4
        for i, (name, label, color, repos) in enumerate(items):
            col, row = i % 3, i // 3
            b += _tile(round(x0 + inner + col * (38 + inner)), 116 + row * 62, name, label, color, .3 + k * .05, repos)
            k += 1
    b += synced(W - 24, H - 6)
    return svg(W, H, b, title="Tech Stack")


# --------------------------------------------------------- what I build

def what_i_build(n: int = 4) -> str:
    W, H = 850, 206
    b = frame(W, H) + heading(24, 20, n, "What I Build", "End-to-end solutions for real world problems")
    items = config.WHAT_I_BUILD[:6]
    gap = 10
    tw = (W - 48 - gap * (len(items) - 1)) / len(items)
    for i, (title, desc) in enumerate(items):
        x = 24 + i * (tw + gap)
        blue = i % 2 == 1
        icon = (cube(x + 30, 100, 15, top="#7cc4ff", left="#1f6feb", right="#0d419d", stroke="#a5d6ff") if blue
                else cube(x + 30, 100, 15))
        b += (f'<g class="rise" {d(.15 + i * .1)}>' + panel(round(x), 70, round(tw), 118, 10) +
              f'<g class="float" style="animation-delay:{i * .4}s">{icon}</g>'
              f'<text x="{x + 12:.0f}" y="146" font-size="11.5" font-weight="700">{esc(title)}</text>')
        for j, line in enumerate(wrap(desc, 24, 2)):
            b += f'<text x="{x + 12:.0f}" y="{162 + j * 12}" font-size="9.3" class="muted">{esc(line)}</text>'
        b += "</g>"
    return svg(W, H, b, title="What I Build")


# ---------------------------------------------------------- collaborate

SERVICES = ["Web Application", "Backend System", "REST API", "Admin Dashboard",
            "WordPress Website", "Cloud Deployment", "API Integration"]


def collaborate(user: dict, n: int = 21) -> str:
    W, H = 850, 176
    phase = sky_phase()
    b = frame(W, H) + sky(1, 1, W - 2, H - 2, phase)
    b += skyline(0, H - 1, W, seed=3, opacity=.35, max_h=60, lit=SKIES[phase][3])
    b += heading(24, 20, n, "Let's Collaborate", "Have a project in mind? Let's build something amazing together.")
    x, y = 24, 78
    for i, s in enumerate(SERVICES):
        w = len(s) * 6.1 + 20
        if x + w > 610:
            x, y = 24, y + 32
        b += (f'<g class="pop" {d(.2 + i * .07)}><rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="6" fill="{CARD2}" stroke="{BORDER}"/>'
              f'<text x="{x + w / 2:.0f}" y="{y + 16}" text-anchor="middle" font-size="10.5" fill="#c9d1d9">{esc(s)}</text></g>')
        x += w + 8
    bx, by = 638, 78
    b += (f'<g class="pop" {d(.6)}><rect x="{bx}" y="{by}" width="188" height="46" rx="10" fill="url(#og)" filter="url(#glow)" class="glowpulse"/>'
          f'<text x="{bx + 94}" y="{by + 28}" text-anchor="middle" font-size="14" font-weight="800" fill="#1a0d02">Start a Project  →</text></g>')
    b += (f'<text x="24" y="158" font-size="11" class="muted fade" {d(1)}>Built with <tspan fill="{ORANGE}">♥</tspan> '
          f'using code, coffee and curiosity.</text>')
    b += f'<text x="826" y="158" text-anchor="end" font-size="11" class="muted fade" {d(1)}>Open to opportunities worldwide · @{esc(user["login"])}</text>'
    return svg(W, H, b, title="Let's Collaborate")


# -------------------------------------------------------------- heading

def section_heading(title: str, subtitle: str = "", n: int | None = None, width: int = 850) -> str:
    H = 64
    b = heading(4, 10, n, title, subtitle)
    tx = 46 if n is not None else 4
    b += f'<rect x="{tx}" y="58" width="{width - tx - 4}" height="1.5" fill="url(#og)" class="grow" {d(.3)} opacity=".6"/>'
    return svg(width, H, b, title=title)


# --------------------------------------------------------------- button

GH = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94"
      "-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07"
      "-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 "
      "1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54"
      ".73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z")


def _icon(kind: str, x: float, y: float) -> str:
    k = kind.lower()
    if k == "github":
        return f'<path transform="translate({x},{y}) scale(1.1)" d="{GH}" fill="{TEXT}"/>'
    if k == "linkedin":
        return (f'<rect x="{x}" y="{y}" width="18" height="18" rx="3" fill="#0a66c2"/>'
                f'<text x="{x + 9}" y="{y + 13.5}" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">in</text>')
    if k in ("email", "mail"):
        return (f'<rect x="{x}" y="{y + 2}" width="18" height="14" rx="2" stroke="{ORANGE}" stroke-width="1.6"/>'
                f'<path d="M{x + 1} {y + 3}l8 6.5 8-6.5" stroke="{ORANGE}" stroke-width="1.6"/>')
    if k == "cookie":
        return (f'<circle cx="{x + 9}" cy="{y + 9}" r="8.5" fill="#c98b4a" stroke="#8a5a2b"/>'
                + "".join(f'<circle cx="{x + cx}" cy="{y + cy}" r="1.6" fill="#3b2412"/>'
                          for cx, cy in ((6, 6), (12, 7), (8, 12), (13, 12), (4, 10))))
    if k == "resume":
        return (f'<path d="M{x + 3} {y}h8l5 5v13h-13z" stroke="{ORANGE}" stroke-width="1.6"/>'
                f'<path d="M{x + 6} {y + 9}h7M{x + 6} {y + 12.5}h7M{x + 6} {y + 16}h4" stroke="{ORANGE}" stroke-width="1.4"/>')
    return (f'<circle cx="{x + 9}" cy="{y + 9}" r="8" stroke="{ORANGE}" stroke-width="1.6"/>'
            f'<path d="M{x + 1} {y + 9}h16M{x + 9} {y + 1}c-4 5-4 11 0 16c4-5 4-11 0-16" stroke="{ORANGE}" stroke-width="1.2"/>')


def button(label: str, icon: str = "", primary: bool = False) -> str:
    W = int(len(label) * 7.4 + 64)
    H = 44
    fill = "url(#og)" if primary else "url(#cardg)"
    b = (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{fill}" stroke="{ORANGE if primary else BORDER}" '
         f'class="{"glowpulse" if primary else ""}"/>')
    b += f'<g class="pop">{_icon(icon or label, 16, 13)}</g>'
    b += (f'<text x="44" y="27" font-size="13" font-weight="700" fill="{"#1a0d02" if primary else TEXT}" class="rise">'
          f'{esc(label)}</text>')
    b += f'<text x="{W - 16}" y="27" text-anchor="end" font-size="13" fill="{ORANGE if not primary else "#1a0d02"}" class="pulse">→</text>'
    return svg(W, H, b, title=label)

