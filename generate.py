"""Render every profile card to static SVG files.

Used by the GitHub Actions workflow (.github/workflows/profile-cards.yml), so the
profile README can show the cards without a publicly deployed API.

    python generate.py --out dist [--readme ../alishaaverma/README.md]

--readme rewrites two blocks of the profile README so they follow GitHub:
<!-- PROJECTS:START --> / <!-- PROJECTS:END -->: each card links to the repo it shows;
<!-- CONTACT:START --> / <!-- CONTACT:END -->: one button per link on my GitHub profile
(LinkedIn and other social accounts, public email, website).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

from app import config
from app import github as gh
from app.cards import engineering as eng
from app.cards import desi, live
from app.cards import profile as prof
from app.cards.theme import set_festival_dates, set_sun_times

BUTTONS = {
    "button-view-my-work": ("View My Work", "github", True),
    "button-github": ("GitHub", "", False),
    "button-linkedin": ("LinkedIn", "", False),
    "button-email": ("Email", "", False),
    "button-resume": ("Resume", "", False),
    "button-website": ("Website", "", False),
    "button-x": ("X", "", False),
    "button-feed-byte": ("Feed Byte a cookie", "cookie", True),
    "button-vote": ("Vote on an idea", "vote", True),
    "button-ama": ("Ask me anything", "ama", False),
}
RAW = f"https://raw.githubusercontent.com/{config.GITHUB_USERNAME}/{config.GITHUB_USERNAME}/output"


async def render(login: str, count_views: bool = False) -> tuple[dict[str, str], list[dict], dict, list[dict], dict | None]:
    (user, repos, events, stats, cal, tech, festivals, weather, commits, til, feeds, ideas, ama,
     socials) = await asyncio.gather(
        gh.get_user(login), gh.get_repos(login), gh.get_events(login), gh.get_stats(login), gh.get_calendar(login),
        gh.get_tech(login), gh.get_festival_dates(), gh.get_weather(), gh.get_commit_log(login), gh.get_til(login),
        gh.get_byte_feeds(login), gh.get_ideas(login), gh.get_ama(login), gh.get_socials(login))
    # only the hourly workflow reads the view counter: each read is a hit it has to take off again
    views = await gh.get_profile_views(login, f"{RAW}/views.json") if count_views else None
    set_festival_dates(festivals)
    set_sun_times(weather)
    top = gh.featured(repos["repos"], 4)
    building = await gh.get_now_building(login, repos)
    ctx = prof.context(user, repos, tech, cal, building, til)

    # Section numbers follow the order of the cards in the profile README.
    cards = {
        "hero": prof.hero(user, ctx, views["views"] if views else None),
        "tldr": prof.tldr(user, stats, cal, repos, tech, ctx),
        "city": live.contribution_city(user, cal, weather, feeds, repos, building),
        "about": prof.about(user, 2, ctx),
        "smart-contracts": live.smart_contract_lab(user, repos, tech, 3),
        "featured-projects": prof.section_heading("Featured Projects",
                                                   {"newest": "My latest public repositories, live from GitHub",
                                                    "updated": "My most recently updated repositories, live from GitHub"}
                                                   .get(config.FEATURED_SORT, "Live from my GitHub repositories"), 4),
        "now-building": live.now_building(building, 5),
        "coding-dna": live.coding_dna(commits, 6),
        "thali": desi.tech_thali(tech, repos),
        "desi-corner": desi.desi_corner(user, cal, commits, repos),
        "report-card": desi.report_card(user, cal),
        "rajdhani": desi.rajdhani(repos),
        "metro": desi.metro(repos, tech),
        "cricket": desi.cricket(cal, commits),
        "dainik-commit": desi.dainik_commit(user, cal, commits, events, repos, weather),
        "community": live.community(ideas, ama, 7),
        # the rest sits under "Explore more about me" in the profile README
        "tech-stack": prof.tech_stack(tech, 9),
        "what-i-build": prof.what_i_build(10, ctx),
        "architecture": eng.architecture(tech, 11),
        "timeline": live.timeline_opensource(user, repos, stats, cal, 12),
        "analytics": live.analytics_exploring(user, stats, cal, repos, tech, til, 14),
        "activity": live.activity_terminal(user, repos, events, 16),
        "playground": live.playground(repos, f"https://api.github.com/users/{login}/repos", 18),
        "cloud": eng.cloud_deploy(tech, 19),
        # 1 Dec - 7 Jan: the year in review takes the achievements slot
        "achievements": (eng.year_in_review(user, repos, stats, cal, tech, 20) if eng.wrapped_season()
                         else eng.achievements(user, repos, stats, cal, tech, 20)),
        "collaborate": prof.collaborate(user, 21, ctx),
    }
    for i in range(4):
        cards[f"project-{i}"] = live.project_card(top[i] if i < len(top) else None, i, login)
    for name, (label, icon, primary) in BUTTONS.items():
        cards[name] = prof.button(label, icon, primary)
    return cards, top, user, socials, views


def contact_links(login: str, user: dict, socials: list[dict]) -> list[tuple[str, str, str]]:
    """(href, button card, alt) for every way to reach me that my GitHub profile lists."""
    links = [(f"https://github.com/{login}?tab=repositories", "button-view-my-work", "View My Work"),
             (f"https://github.com/{login}", "button-github", "GitHub")]
    by_provider = {s["provider"]: s["url"] for s in socials}
    if by_provider.get("linkedin"):
        links.append((by_provider["linkedin"], "button-linkedin", "LinkedIn"))
    if user.get("email"):
        links.append((f"mailto:{user['email']}", "button-email", "Email"))
    if user.get("blog"):
        url = user["blog"] if user["blog"].startswith("http") else f"https://{user['blog']}"
        resume = re.search(r"resume|cv|\.pdf|drive\.google", url, re.I)
        links.append((url, "button-resume" if resume else "button-website", "Resume" if resume else "Website"))
    twitter = by_provider.get("twitter") or (f"https://x.com/{user['twitter']}" if user.get("twitter") else "")
    if twitter:
        links.append((twitter, "button-x", "X"))
    return links


def _replace_block(text: str, name: str, body: str) -> str:
    m = re.search(rf"(<!-- {name}:START[^>]*-->\n)(.*?)(<!-- {name}:END -->)", text, re.S)
    return text[:m.start(2)] + body + text[m.end(2):] if m else text


def update_readme(path: Path, login: str, top: list[dict], user: dict, socials: list[dict]) -> bool:
    """Point each featured-project card at the repo it shows and rebuild the contact buttons.
    Returns True if the README changed."""
    text = path.read_text()
    m = re.search(r"(<!-- PROJECTS:START -->\n)(.*?)(<!-- PROJECTS:END -->)", text, re.S)
    if m:
        body = m.group(2)
        for i in range(4):
            url = top[i]["url"] if i < len(top) else f"https://github.com/{login}?tab=repositories"
            body = re.sub(rf'<a href="[^"]*">(<img src="[^"]*project-{i}\.svg)', rf'<a href="{url}">\1', body)
        text = text[:m.start(2)] + body + text[m.end(2):]
    buttons = "".join(f'  <a href="{href}"><img src="{RAW}/{card}.svg" height="44" alt="{alt}"/></a>\n'
                      for href, card, alt in contact_links(login, user, socials))
    new = _replace_block(text, "CONTACT", buttons)
    if new != path.read_text():
        path.write_text(new)
        return True
    return False


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--readme")
    ap.add_argument("--count-views", action="store_true", help="read the profile view counter (the workflow only)")
    args = ap.parse_args()

    login = config.GITHUB_USERNAME
    cards, top, user, socials, views = await render(login, args.count_views)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, body in cards.items():
        (out / f"{name}.svg").write_text(body)
    if views:
        (out / "views.json").write_text(json.dumps(views))
    print(f"Rendered {len(cards)} cards for @{login} into {out}/")

    if args.readme:
        changed = update_readme(Path(args.readme), login, top, user, socials)
        print("README links", "updated" if changed else "unchanged")


if __name__ == "__main__":
    asyncio.run(main())
