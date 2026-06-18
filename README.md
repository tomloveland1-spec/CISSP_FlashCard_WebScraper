# CISSP FlashCard WebScraper

Scrape CISSP study content (term → definition) and export it as a tab-separated
`.txt` file ready to paste-import into [Quizlet](https://quizlet.com).

There are two scrapers:

| Script        | Source                                            | Auth needed |
| ------------- | ------------------------------------------------- | ----------- |
| `wiley.py`    | Wiley "Online Test Banks" (study.learning.wiley.com) flashcards | Yes (login) |
| `scraper.py`  | Generic static HTML glossaries (config-driven)    | No          |

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`
- For the **Wiley login step only**: a Playwright-supported OS and a browser:
  `python -m playwright install chromium`

### Which OS to run the Wiley path from

Wiley's content is an authenticated React app behind Cloudflare; logging in needs
a real browser (Playwright/Chromium). Chromium runs cleanly on:

- **Windows 10/11 (native)** — easiest; `playwright install chromium` just works.
- **Ubuntu 22.04 / 24.04 LTS** — `python -m playwright install --with-deps chromium`.
- **macOS** — supported.

> Note: Ubuntu **26.04** (and other very new distros) currently have **no
> Playwright Chromium build**, so the browser login can't run there. Once you have
> a token, the rest (`wiley.py`) is plain HTTP and runs anywhere.

## Wiley flashcards (`wiley.py`)

The flashcards come from a GraphQL API that requires an OIDC token (sent as the
raw JWT in the `Authorization` header — no `Bearer ` prefix). You can get one two
ways.

### Option A — automated browser login (recommended)

On a Playwright-supported machine, put your credentials in `.env` (see below), then:

```bash
python wiley.py --login                 # logs in, scrapes, writes the deck
python wiley.py --login --headed        # show the browser (needed for MFA/CAPTCHA)
```

### Option B — paste a token (works on any machine, no browser)

1. Open the product in a browser where you're already logged in.
2. DevTools → **Network** → click any request to `study.learning.wiley.com/graphql`.
3. Copy the `authorization` request-header value (the raw `eyJ...` JWT).
4. Run:

```bash
python wiley.py --token "<paste>"        # or --token-file token.txt
WILEY_TOKEN="<paste>" python wiley.py
```

Tokens expire in ~5 minutes, but a full scrape finishes well within that.

### Credentials (`.env`)

Copy `.env.sample` to `.env` and fill it in: **two bare lines**, username (email)
then password, taken verbatim — no quotes, no escaping, so special characters in
the password just work. **`.env` is gitignored — never commit it.** Only
`wiley_login.py` reads it.

```
you@example.com
your-password
```

### Useful flags

`--product-id <uuid>` (defaults to the configured CISSP product), `--out <path>`,
`--limit N` (testing), `--workers N` (concurrent requests), `--verbose`.

## Generic glossary scraper (`scraper.py`)

For static HTML term/definition pages, configure a source in [config.py](config.py)
and run `python scraper.py --source main` (or `--url <URL>`). Supports definition
lists, two-column tables, and bolded-term list items. See `config.py` for selector
details.

## Importing into Quizlet

1. In Quizlet, create a new set and click **Import**.
2. Paste the contents of `output/cissp_quizlet.txt`.
3. Set **Between term and definition** to **Tab**.
4. Set **Between cards** to **New line**.
5. Preview, then **Import**.

## Running the tests

Tests are offline (no network/browser):

```bash
python -m pytest
```

## Note

For personal study use with content you have legitimate, paid access to. This
automates *your own* logged-in access using *your* credentials; respect Wiley's
terms of service and don't redistribute scraped content.
