# CLAUDE.md — CISSP FlashCard WebScraper

Project context for continuing this work (handoff from a WSL session to Windows).

## Purpose
Scrape CISSP **term → definition** flashcards from the user's *paid* Wiley
"Online Test Banks" product and export a tab-separated `.txt` for Quizlet import.
Personal study use, automating the user's own logged-in access with their own
credentials.

## ⚠️ Hard constraints
- **NEVER read `.env`.** It holds the user's Wiley login. Format is two bare lines,
  taken verbatim — `username` (email) on line 1, `password` on line 2; no quotes, no
  escaping (see `.env.sample`). Only `wiley_login.py` reads it at runtime, via
  `load_credentials`, which parses defensively so a malformed file can't leak the
  password into a traceback. `.env` is gitignored — never commit it.
- Don't build anything to evade Cloudflare/bot protection beyond what a normal
  browser does. A real browser logging in with the user's creds is the approach.

## Current status (2026-06-18 — WORKING END-TO-END on Windows)
- Repo lives on Windows at `C:\Users\toman\Repositories\CISSP_FlashCard_WebScraper`.
  (WSL was abandoned: Ubuntu 26.04 has no Playwright Chromium build / no `libnss3`.)
- `python -m pytest` → **24 offline tests pass**.
- **Verified end-to-end on Windows:** `python wiley.py --login --headed --verbose`
  logs in with `.env` creds, captures the token, and writes **1065 cards** to
  `output\cissp_quizlet.txt`. The token-paste / `--token-file` path also verified.
- The first real run revealed the handoff's site notes were stale; they have been
  corrected below and in code. Summary of what actually changed:
  - Login page is **login.education.wiley.com** (a normal Wiley account form), NOT
    the Keycloak realm. Selectors: `#email`, `#filled-adornment-password`, submit
    `button[type=submit]` ("LOG IN"); a cookie banner ("Accept") overlays the button.
  - GraphQL endpoint is now same-origin **`https://study.learning.wiley.com/graphql`**
    (the old AppSync host is unused by the app).
  - Auth header is the **raw JWT** (`eyJ...`) with **NO `Bearer ` prefix**.

## Files
- `wiley.py` — main scraper. Token-authed GraphQL (`GetFlashcards` → `GetFlashcardInfo`
  → dedupe → Quizlet export). Pure HTTP; runs anywhere **given a token**.
- `wiley_login.py` — Playwright login (reads `.env`), captures the raw JWT from the
  `Authorization` header of the app's own GraphQL request. Needs a browser. Flags:
  `--channel chrome` (use installed Google Chrome), `--headed`.
- `scraper.py` — generic static-HTML glossary scraper; also provides reused helpers
  (`Flashcard`, `clean_text`, `dedupe`, `export_quizlet_txt`).
- `config.py` — `WILEY` constants + `WILEY_QUERIES`; `SOURCES` for the generic scraper.
- `tests/` — offline tests (no network/browser).

## How the Wiley site works (verified live 2026-06-18 — do NOT re-derive)
- React SPA behind Cloudflare; content served by a same-origin **GraphQL** gateway.
- Prod GraphQL endpoint: **`https://study.learning.wiley.com/graphql`**.
  (Historically the app hit AWS AppSync directly at
  `https://di2fuedp4zfr3kyvihx2yudgay.appsync-api.us-east-1.amazonaws.com/graphql`;
  that host is no longer used.)
- Auth: `Authorization: <raw OIDC JWT>` — **no `Bearer ` prefix**. No token →
  HTTP 401. `wiley.py` sends the token verbatim and strips a stray `Bearer ` if pasted.
- Login: a normal Wiley account form at **`https://login.education.wiley.com/login`**
  (NOT Keycloak). Field ids: `#email`, `#filled-adornment-password`; submit is
  `button[type=submit]` (text "LOG IN"). A cookie-consent banner ("Accept" /
  "Deny Non-Essential") can overlay the submit button — dismiss it first. After
  submit the SPA redirects back to the product and fires authenticated GraphQL calls,
  from which we capture the token. (No MFA/CAPTCHA seen on the user's account.)
- Queries (unchanged, confirmed against the live schema): `GetFlashcards($productId)`
  → topics each with a list of flashcard `ids`; `GetFlashcardInfo($flashcardId)` →
  `frontText` (term) / `backText` (definition); `GetProductInfo($productId)` → counts.
  Default productId (the CISSP product): `8e14c3b0-ca0c-4031-bf9b-7a3887432107`.

## Run it (Windows)
Deps + Playwright Chromium are already installed on this machine. To run:
```powershell
cd C:\Users\toman\Repositories\CISSP_FlashCard_WebScraper
python wiley.py --login --headed --verbose      # bundled Chromium; --headed for safety
```
(First-time setup, if needed: `pip install -r requirements.txt` then
`python -m playwright install chromium`. `--channel chrome` uses installed Google
Chrome instead of the bundled browser. `--headed` is optional but lets you complete
an MFA/CAPTCHA prompt if one ever appears.)
Output → `output\cissp_quizlet.txt`. Quizlet import: **Tab** between term/definition,
**New line** between cards.

Token-paste fallback (no browser, runs anywhere): in DevTools → Network on any
`study.learning.wiley.com/graphql` request, copy the `authorization` request-header
value (the raw `eyJ...` JWT), then `python wiley.py --token "<paste>"`.

## Troubleshooting (if a future run breaks)
- Token capture works by intercepting the `authorization` header on the app's own
  GraphQL request (see `on_request` in `wiley_login.py`). If selectors drift, re-probe
  the live page (open it headed, dump inputs/buttons) and update the login block.
- Tokens are short-lived (~minutes), but a full scrape finishes well within that.
