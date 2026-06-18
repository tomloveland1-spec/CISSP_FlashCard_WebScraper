"""Log into Wiley with a real browser and capture an OIDC Bearer token.

Wiley's SSO uses the Authorization Code + PKCE flow, so a real browser is the
reliable way to authenticate (it also handles any MFA or bot checks). This
script drives Chromium via Playwright, signs in with the credentials in
``.env`` at login.education.wiley.com, and grabs the ``Authorization`` token
that the app sends to its GraphQL API.

Requirements: a Playwright-supported OS (Windows / macOS / Ubuntu 22.04|24.04):
    pip install -r requirements.txt
    python -m playwright install chromium

Usage:
    python wiley_login.py                 # print the token
    python wiley_login.py --save token.txt --headed
    # or, end-to-end, let wiley.py call this:  python wiley.py --login

Credentials file (.env -- matches .env.sample). Two bare lines, taken
verbatim (no quotes, no escapes -- special characters just work):
    you@example.com
    your-password
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import config

CRED_PATH = Path(".env")


def load_credentials(path: Path = CRED_PATH) -> dict:
    """Load username/password from .env, taking values verbatim.

    Two accepted layouts (blank lines and ``#`` comments are ignored):

    1. Bare positional -- first content line is the username, second is the
       password::

           you@example.com
           s3cr#t&p@ss

    2. Keyed -- ``username: ...`` / ``password: ...`` (``:`` or ``=`` separator).

    Values are read literally: no quoting, no escapes. This deliberately avoids
    YAML so passwords full of special characters (``& $ \\ ' "``) just work, and
    a parse error can never echo the password into a traceback.
    """
    if not path.exists():
        raise SystemExit(f"Credentials file {path} not found. Copy .env.sample to .env and fill it in.")

    lines = [
        ln for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]

    creds: dict[str, str] = {}
    positional: list[str] = []
    for ln in lines:
        key, sep, val = _split_keyed(ln)
        if sep and key in ("username", "password"):
            creds[key] = val
        else:
            positional.append(ln)

    if "username" not in creds and positional:
        creds["username"] = positional.pop(0)
    if "password" not in creds and positional:
        creds["password"] = positional.pop(0)

    if not creds.get("username") or not creds.get("password"):
        raise SystemExit(
            f"{path} must provide a username and password -- either two bare lines "
            "(username then password) or 'username:'/'password:' keys. See .env.sample."
        )
    return creds


def _split_keyed(line: str) -> tuple[str, bool, str]:
    """Split 'key: value' / 'key=value' into (key.lower(), found, value).

    Returns (line, False, '') when the line isn't keyed, so the caller can
    treat it positionally. Only the FIRST separator splits, so a password
    containing ':' or '=' is preserved.
    """
    idx_colon = line.find(":")
    idx_eq = line.find("=")
    candidates = [i for i in (idx_colon, idx_eq) if i != -1]
    if not candidates:
        return line, False, ""
    i = min(candidates)
    key = line[:i].strip().lower()
    if key not in ("username", "password"):
        return line, False, ""
    return key, True, line[i + 1:].strip()


def login_and_get_token(
    *,
    headless: bool = True,
    product_id: str | None = None,
    timeout_s: int = 90,
    channel: str | None = None,
) -> str:
    """Open the product, sign in, and return the Bearer token the app uses."""
    try:
        from playwright.sync_api import TimeoutError as PWTimeout
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "Playwright is not installed. Run `pip install -r requirements.txt` and "
            "`python -m playwright install chromium` on a supported OS "
            "(Windows / macOS / Ubuntu 22.04|24.04)."
        ) from exc

    creds = load_credentials()
    product_id = product_id or config.WILEY["default_product_id"]
    product_url = f"{config.WILEY['app_url']}/products/{product_id}?tab=units"
    graphql_host = config.WILEY["graphql_url"]

    captured: dict[str, str] = {}

    def on_request(request) -> None:
        if graphql_host in request.url:
            # The app sends the raw JWT as the Authorization header (no "Bearer "
            # prefix). Capture whatever non-empty value it sends, minus a prefix
            # if one ever appears.
            auth = request.headers.get("authorization", "").strip()
            if auth:
                if auth[:7].lower() == "bearer ":
                    auth = auth[7:].strip()
                captured.setdefault("token", auth)

    with sync_playwright() as p:
        # channel="chrome" drives an installed Google Chrome (no Chromium download).
        launch_kwargs = {"headless": headless}
        if channel:
            launch_kwargs["channel"] = channel
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context()
        page = context.new_page()
        page.on("request", on_request)

        page.goto(product_url, wait_until="domcontentloaded")

        # Fill the Wiley account login form if it appears (skip if already
        # signed in). The live page is login.education.wiley.com (NOT the
        # Keycloak realm the old docs described): email field #email, password
        # field #filled-adornment-password, submit is a "LOG IN" button. A
        # cookie-consent banner can overlay the submit button, so dismiss it.
        try:
            page.wait_for_selector("#email", timeout=20_000)

            # Dismiss the cookie banner if present (it covers the LOG IN button).
            try:
                page.get_by_role("button", name="Accept", exact=True).click(timeout=3_000)
            except PWTimeout:
                pass

            page.fill("#email", creds["username"])
            page.fill("#filled-adornment-password", creds["password"])
            try:
                page.get_by_role("button", name="LOG IN", exact=True).click(timeout=5_000)
            except PWTimeout:
                page.click("button[type=submit]")
        except PWTimeout:
            pass  # no login form -> existing session

        # Wait until the app issues an authenticated GraphQL request.
        deadline = timeout_s
        while "token" not in captured and deadline > 0:
            page.wait_for_timeout(500)
            deadline -= 0.5
        browser.close()

    if "token" not in captured:
        raise SystemExit(
            "Could not capture a token. Login may have failed (wrong credentials, "
            "MFA, or a CAPTCHA). Re-run with --headed to complete it interactively."
        )
    return captured["token"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--product-id", default=None, help="Wiley product UUID.")
    parser.add_argument("--headed", action="store_true", help="Show the browser window.")
    parser.add_argument("--channel", default=None,
                        help="Browser channel, e.g. 'chrome' to use installed Google Chrome.")
    parser.add_argument("--save", help="Write the token to this file instead of printing it.")
    args = parser.parse_args(argv)

    token = login_and_get_token(
        headless=not args.headed, product_id=args.product_id, channel=args.channel
    )
    if args.save:
        Path(args.save).write_text(token, encoding="utf-8")
        print(f"Token saved to {args.save}")
    else:
        print(token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
