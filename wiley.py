"""Scrape CISSP flashcards from a Wiley "Online Test Banks" product.

The content lives behind an AWS AppSync GraphQL API that requires an OIDC Bearer
token. This module does the token-authenticated GraphQL work and exports a
Quizlet-importable file. It reuses the cleaning/dedupe/export helpers from
``scraper.py``.

Getting a token (the API rejects everything without a valid Bearer token):

  * Easiest, runs anywhere: open the product in a browser where you're logged in,
    DevTools -> Network -> click any "*.appsync-api.*/graphql" request -> copy the
    `authorization` request header value (the part after "Bearer "). Then:

        python wiley.py --token "<paste>"            # or --token-file token.txt
        WILEY_TOKEN="<paste>" python wiley.py

  * Automated: on a Playwright-supported OS (Windows / macOS / Ubuntu 22.04|24.04),
    let wiley_login.py log in with the .env credentials and mint a token:

        python wiley.py --login

Tokens are short-lived (~5 min), but a full scrape takes well under that.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup

import config
from scraper import Flashcard, clean_text, dedupe, export_quizlet_txt

logger = logging.getLogger("wiley")


def strip_html(text: str | None) -> str:
    """Flashcard text can be HTML (rich text). Reduce it to clean plain text."""
    if not text:
        return ""
    return clean_text(BeautifulSoup(text, "lxml").get_text(" "))


class WileyClient:
    """Minimal token-authenticated client for the Wiley AppSync GraphQL API."""

    def __init__(self, token: str, *, graphql_url: str | None = None):
        # The app sends the raw OIDC JWT as the Authorization header with NO
        # "Bearer " prefix. Tolerate a pasted value that still has the prefix.
        token = token.strip()
        if token[:7].lower() == "bearer ":
            token = token[7:].strip()
        self.token = token
        self.url = graphql_url or config.WILEY["graphql_url"]
        self.session = requests.Session()

    def _gql(self, query: str, variables: dict) -> dict:
        try:
            resp = self.session.post(
                self.url,
                json={"query": query, "variables": variables},
                headers={
                    "Authorization": self.token,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"GraphQL request failed: {exc}") from exc

        if resp.status_code in (401, 403):
            raise PermissionError(
                f"GraphQL returned {resp.status_code} -- the token is missing, "
                "invalid, or expired. Get a fresh token and retry."
            )
        if not resp.ok:
            body = resp.text[:300].strip()
            hint = (" (a malformed token can cause this -- check you copied the "
                    "full Bearer value)" if resp.status_code >= 500 else "")
            raise RuntimeError(f"GraphQL HTTP {resp.status_code}{hint}: {body}")
        payload = resp.json()
        if payload.get("errors"):
            msgs = "; ".join(e.get("message", str(e)) for e in payload["errors"])
            raise RuntimeError(f"GraphQL errors: {msgs}")
        return payload["data"]

    def product_info(self, product_id: str) -> dict:
        data = self._gql(config.WILEY_QUERIES["GetProductInfo"], {"productId": product_id})
        return data["getProductInfo"]

    def flashcard_topics(self, product_id: str) -> list[dict]:
        data = self._gql(config.WILEY_QUERIES["GetFlashcards"], {"productId": product_id})
        return data.get("getFlashcards") or []

    def flashcard_info(self, flashcard_id: str) -> dict:
        data = self._gql(config.WILEY_QUERIES["GetFlashcardInfo"], {"flashcardId": flashcard_id})
        return data["getFlashcardInfo"]


def collect_cards(
    client: WileyClient,
    product_id: str,
    *,
    limit: int | None = None,
    max_workers: int = 8,
) -> list[Flashcard]:
    """Walk topics -> flashcard ids -> front/back text, returning Flashcards."""
    topics = client.flashcard_topics(product_id)
    ids: list[str] = []
    for topic in topics:
        ids.extend(topic.get("ids") or [])
    logger.info("Found %d topics, %d flashcard ids", len(topics), len(ids))
    if limit is not None:
        ids = ids[:limit]

    def fetch(flashcard_id: str) -> Flashcard | None:
        info = client.flashcard_info(flashcard_id)
        term = strip_html(info.get("frontText"))
        definition = strip_html(info.get("backText"))
        if term and definition:
            return Flashcard(term, definition)
        return None

    cards: list[Flashcard] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for i, card in enumerate(pool.map(fetch, ids), start=1):
            if card:
                cards.append(card)
            if i % 50 == 0:
                logger.info("  fetched %d/%d", i, len(ids))
    return cards


# --------------------------------------------------------------------------- #
# Token resolution + CLI
# --------------------------------------------------------------------------- #
def resolve_token(args: argparse.Namespace) -> str:
    """Get a Bearer token from --token, --token-file, $WILEY_TOKEN, or --login."""
    if args.token:
        return args.token.strip()
    if args.token_file:
        return Path(args.token_file).read_text(encoding="utf-8").strip()
    env_token = os.environ.get("WILEY_TOKEN")
    if env_token:
        return env_token.strip()
    if args.login:
        from wiley_login import login_and_get_token  # imported lazily; needs Playwright
        return login_and_get_token(
            headless=not args.headed, product_id=args.product_id, channel=args.channel
        )
    raise SystemExit(
        "No token provided. Use --token / --token-file / $WILEY_TOKEN, or --login "
        "on a machine with Playwright installed. See `python wiley.py -h`."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape Wiley test-bank flashcards into a Quizlet file.")
    parser.add_argument("--product-id", default=config.WILEY["default_product_id"],
                        help="Wiley product UUID (default: the configured CISSP product).")
    parser.add_argument("--token", help="OIDC Bearer token (without the 'Bearer ' prefix).")
    parser.add_argument("--token-file", help="Path to a file containing the Bearer token.")
    parser.add_argument("--login", action="store_true",
                        help="Mint a token via Playwright login (reads .env credentials).")
    parser.add_argument("--headed", action="store_true",
                        help="With --login, show the browser (useful for MFA/CAPTCHA).")
    parser.add_argument("--channel", default=None,
                        help="With --login, browser channel, e.g. 'chrome' for installed Google Chrome.")
    parser.add_argument("--out", default="output/cissp_quizlet.txt", help="Output file path.")
    parser.add_argument("--delimiter", default="\t", help="Field delimiter (default: tab).")
    parser.add_argument("--limit", type=int, default=None, help="Cap number of flashcards (testing).")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent GraphQL requests.")
    parser.add_argument("--verbose", action="store_true", help="Enable info logging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        token = resolve_token(args)
        client = WileyClient(token)
        info = client.product_info(args.product_id)
        logger.info("Product: %s (flashcards=%s, topics=%s)",
                    info.get("title"), info.get("flashcardCount"), info.get("flashcardTopicCount"))
        cards = dedupe(collect_cards(client, args.product_id, limit=args.limit, max_workers=args.workers))
    except PermissionError as exc:
        logger.error("%s", exc)
        return 2
    except (RuntimeError, requests.HTTPError) as exc:
        logger.error("%s", exc)
        return 1

    if not cards:
        logger.error("No flashcards found for product %s.", args.product_id)
        return 1

    export_quizlet_txt(cards, args.out, delimiter=args.delimiter)
    print(f"Wrote {len(cards)} cards to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
