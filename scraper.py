"""CISSP FlashCard WebScraper.

Scrape term -> definition pairs from a configured web source and export them as a
tab-separated ``.txt`` file ready to paste-import into Quizlet.

Usage:
    python scraper.py --source main
    python scraper.py --url https://example.com/glossary --out output/deck.txt
    python scraper.py --source main --limit 10 --verbose
"""

from __future__ import annotations

import argparse
import html
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger("cissp_scraper")

_WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class Flashcard:
    """A single term -> definition study card."""

    term: str
    definition: str


# --------------------------------------------------------------------------- #
# Text cleaning
# --------------------------------------------------------------------------- #
def clean_text(text: str) -> str:
    """Unescape HTML entities and collapse all whitespace to single spaces."""
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", html.unescape(text)).strip()


def sanitize_field(text: str) -> str:
    """Make a field safe for one line of a tab/newline-delimited Quizlet file.

    Any embedded tab or newline would split a card into pieces on import, so
    replace them with spaces. Run after :func:`clean_text`.
    """
    return text.replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #
def robots_allows(url: str, user_agent: str = config.USER_AGENT) -> bool:
    """Return True if ``url`` is allowed for ``user_agent`` per the site robots.txt.

    If robots.txt cannot be fetched we follow the common convention of allowing
    the crawl, but we log it so the operator is aware.
    """
    parts = urlsplit(url)
    robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception as exc:  # network error, malformed file, etc.
        logger.warning("Could not read %s (%s); assuming crawl is allowed.", robots_url, exc)
        return True
    return parser.can_fetch(user_agent, url)


def fetch_html(url: str, *, session: requests.Session | None = None) -> str:
    """Fetch a page as text, honoring robots.txt and retrying transient errors."""
    if not robots_allows(url):
        raise PermissionError(f"robots.txt disallows fetching {url}")

    sess = session or requests.Session()
    headers = {"User-Agent": config.USER_AGENT}
    last_exc: Exception | None = None
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            resp = sess.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
            backoff = 2 ** (attempt - 1)
            logger.warning("Fetch failed (attempt %d/%d) for %s: %s",
                           attempt, config.MAX_RETRIES, url, exc)
            if attempt < config.MAX_RETRIES:
                time.sleep(backoff)
    raise RuntimeError(f"Failed to fetch {url} after {config.MAX_RETRIES} attempts") from last_exc


def _paginated_urls(source_cfg: dict) -> list[str]:
    """Expand a source's pagination config into a list of page URLs."""
    base = source_cfg["url"]
    pagination = source_cfg.get("pagination")
    if not pagination:
        return [base]

    param = pagination["param"]
    start = pagination.get("start", 1)
    max_pages = pagination["max_pages"]
    urls = []
    for page in range(start, start + max_pages):
        split = urlsplit(base)
        query = dict(parse_qsl(split.query))
        query[param] = str(page)
        urls.append(urlunsplit(
            (split.scheme, split.netloc, split.path, urlencode(query), split.fragment)
        ))
    return urls


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def _parse_definition_list(soup: BeautifulSoup, source_cfg: dict) -> list[Flashcard]:
    """Pair each ``<dt>`` with the ``<dd>`` sibling(s) that follow it."""
    cards: list[Flashcard] = []
    for dl in soup.select(source_cfg["row_selector"]):
        for dt in dl.find_all("dt"):
            term = clean_text(dt.get_text(" "))
            definition_parts = []
            for sib in dt.find_next_siblings():
                if sib.name == "dt":
                    break
                if sib.name == "dd":
                    definition_parts.append(clean_text(sib.get_text(" ")))
            definition = " ".join(p for p in definition_parts if p)
            if term and definition:
                cards.append(Flashcard(term, definition))
    return cards


def parse_cards(page_html: str, source_cfg: dict) -> list[Flashcard]:
    """Extract flashcards from page HTML using a source's selectors."""
    soup = BeautifulSoup(page_html, "lxml")
    term_sel = source_cfg.get("term_selector")
    def_sel = source_cfg.get("definition_selector")

    # Definition lists need sibling pairing, not row containment.
    if term_sel == "dt" and def_sel == "dd":
        return _parse_definition_list(soup, source_cfg)

    cards: list[Flashcard] = []
    for row in soup.select(source_cfg["row_selector"]):
        term_el = row.select_one(term_sel) if term_sel else None
        if term_el is None:
            continue
        term = clean_text(term_el.get_text(" "))

        if def_sel:
            def_el = row.select_one(def_sel)
            definition = clean_text(def_el.get_text(" ")) if def_el else ""
        else:
            # No definition selector: definition is the row text minus the term.
            row_text = clean_text(row.get_text(" "))
            definition = clean_text(row_text[len(term):]) if row_text.startswith(term) else row_text
            definition = definition.lstrip(":-–— ").strip()

        if term and definition:
            cards.append(Flashcard(term, definition))
    return cards


# --------------------------------------------------------------------------- #
# Dedupe + export
# --------------------------------------------------------------------------- #
def dedupe(cards: list[Flashcard], *, sort: bool = True) -> list[Flashcard]:
    """Drop duplicate terms (case-insensitive), keeping the longest definition."""
    best: dict[str, Flashcard] = {}
    for card in cards:
        key = card.term.casefold()
        existing = best.get(key)
        if existing is None or len(card.definition) > len(existing.definition):
            best[key] = card
    result = list(best.values())
    if sort:
        result.sort(key=lambda c: c.term.casefold())
    return result


def export_quizlet_txt(cards: list[Flashcard], path: str | Path, *, delimiter: str = "\t") -> None:
    """Write cards as ``term<delimiter>definition``, one card per line (UTF-8)."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{sanitize_field(c.term)}{delimiter}{sanitize_field(c.definition)}"
        for c in cards
    ]
    out_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def scrape_source(source_cfg: dict, *, limit: int | None = None) -> list[Flashcard]:
    """Fetch and parse every page of a source, returning deduped cards."""
    session = requests.Session()
    all_cards: list[Flashcard] = []
    urls = _paginated_urls(source_cfg)
    for i, url in enumerate(urls):
        logger.info("Fetching %s", url)
        page_html = fetch_html(url, session=session)
        page_cards = parse_cards(page_html, source_cfg)
        logger.info("  parsed %d cards", len(page_cards))
        all_cards.extend(page_cards)
        if i < len(urls) - 1:
            time.sleep(config.REQUEST_DELAY)

    cards = dedupe(all_cards)
    if limit is not None:
        cards = cards[:limit]
    return cards


def _resolve_source(args: argparse.Namespace) -> dict:
    """Build a source config from CLI args (--url overrides --source)."""
    if args.url:
        return {"url": args.url, **config.DEFAULT_SELECTORS}
    if args.source not in config.SOURCES:
        raise SystemExit(
            f"Unknown source '{args.source}'. Known: {', '.join(config.SOURCES)}"
        )
    return config.SOURCES[args.source]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--source", default="main",
                        help="Name of a source in config.SOURCES (default: main).")
    parser.add_argument("--url",
                        help="Scrape this URL directly with default selectors "
                             "(overrides --source).")
    parser.add_argument("--out", default="output/cissp_quizlet.txt",
                        help="Output file path (default: output/cissp_quizlet.txt).")
    parser.add_argument("--delimiter", default="\t",
                        help="Field delimiter; default is a tab (for Quizlet).")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap the number of cards (useful for testing).")
    parser.add_argument("--verbose", action="store_true", help="Enable info logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    source_cfg = _resolve_source(args)
    try:
        cards = scrape_source(source_cfg, limit=args.limit)
    except PermissionError as exc:
        logger.error("%s", exc)
        return 2
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1

    if not cards:
        logger.error("No cards found. Check the source URL and selectors in config.py.")
        return 1

    export_quizlet_txt(cards, args.out, delimiter=args.delimiter)
    print(f"Wrote {len(cards)} cards to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
