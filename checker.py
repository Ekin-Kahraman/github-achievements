"""Read achievement badges actually visible in public GitHub profile HTML."""

from html.parser import HTMLParser
import re
from urllib.request import Request, urlopen

TIER_ORDER = {"default": 0, "bronze": 1, "silver": 2, "gold": 3}
USERNAME = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")


class BadgeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.badges = {}

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        attrs = dict(attrs)
        if "achievement-badge" not in attrs.get("class", ""):
            return
        alt = attrs.get("alt", "")
        if not alt.startswith("Achievement: "):
            return
        name = alt.removeprefix("Achievement: ").strip()
        if not name:
            return
        slug = name.lower().replace(" ", "-")
        match = re.search(r"-(default|bronze|silver|gold)-", attrs.get("src", ""))
        tier = match.group(1) if match else "unknown"
        previous = self.badges.get(slug)
        if previous is None or TIER_ORDER.get(tier, -1) > TIER_ORDER.get(previous["tier"], -1):
            self.badges[slug] = {"name": name, "tier": tier}


def parse_badges(html):
    parser = BadgeParser()
    parser.feed(html)
    return parser.badges


def fetch_profile(username):
    if not USERNAME.fullmatch(username):
        raise ValueError("Invalid GitHub username")
    request = Request(
        f"https://github.com/{username}",
        headers={"User-Agent": "github-achievements-checker/1.0"},
    )
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")
