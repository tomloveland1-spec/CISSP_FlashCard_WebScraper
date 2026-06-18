"""Source definitions for the CISSP flashcard scraper.

Each source describes one site to scrape. The scraper selects rows with
``row_selector`` and, within each row, pulls the term and definition with
``term_selector`` / ``definition_selector`` (both relative to the row).

Three common glossary shapes are supported out of the box -- pick the selector
set that matches the page you are scraping:

1. Definition list (``<dl>`` with ``<dt>`` term / ``<dd>`` definition):
       row_selector="dl", term_selector="dt", definition_selector="dd"
   (handled specially: dt/dd are siblings, not nested -- see note below)

2. Two-column table (``<tr>`` with two ``<td>`` cells):
       row_selector="table tr", term_selector="td:nth-of-type(1)",
       definition_selector="td:nth-of-type(2)"

3. List items with a bolded lead-in (``<li><strong>term</strong> definition``):
       row_selector="li", term_selector="strong", definition_selector=None
   (when definition_selector is None the definition is the row's remaining text
   after the term is removed)

To inspect a page's structure, open it in a browser, right-click the term/
definition and "Inspect", then translate the surrounding tags into selectors.
"""

# A descriptive User-Agent is polite and helps site owners contact you.
USER_AGENT = (
    "CISSP-FlashCard-WebScraper/0.1 "
    "(+https://github.com/; personal study use)"
)

REQUEST_TIMEOUT = 20  # seconds
REQUEST_DELAY = 1.0   # seconds between paginated requests (be polite)
MAX_RETRIES = 3

# Default selectors assume a definition-list glossary. Override per source.
DEFAULT_SELECTORS = {
    "row_selector": "dl",
    "term_selector": "dt",
    "definition_selector": "dd",
}

SOURCES = {
    "main": {
        # TODO: replace with the real source URL before scraping.
        "url": "https://example.com/cissp-glossary",
        "row_selector": "dl",
        "term_selector": "dt",
        "definition_selector": "dd",
        # Optional pagination, e.g. ?page=1..N:
        # "pagination": {"param": "page", "start": 1, "max_pages": 5},
    },
}


# --------------------------------------------------------------------------- #
# Wiley "Online Test Banks" (study.learning.wiley.com)
# --------------------------------------------------------------------------- #
# This product is an authenticated React SPA whose flashcard content is served
# by an AWS AppSync GraphQL API. The API requires an OIDC Bearer token (the
# static x-api-key in the app bundle is a dummy). Tokens are minted by logging
# in through Wiley's Keycloak SSO -- see wiley_login.py (uses a real browser,
# because the SSO only supports the Authorization Code + PKCE flow).
#
# Values below were read from the app's public JS bundle (config object O1e,
# the production branch for host "study.learning.wiley.com").
WILEY = {
    # The app now calls a same-origin GraphQL gateway (verified live 2026-06).
    # It used to hit AWS AppSync directly
    # (https://di2fuedp4zfr3kyvihx2yudgay.appsync-api.us-east-1.amazonaws.com/graphql);
    # that host is no longer used by the app.
    "graphql_url": "https://study.learning.wiley.com/graphql",
    "app_url": "https://study.learning.wiley.com",
    "oidc_authority": "https://external-sso.wiley.com/auth/realms/wiley",
    "oidc_client_id": "8ef0cdf2-cd41-421f-bb45-f8bd396a5619",
    "oidc_redirect_uri": "https://study.learning.wiley.com/signin-oidc",
    # The product you want to scrape (the UUID from the product URL).
    "default_product_id": "8e14c3b0-ca0c-4031-bf9b-7a3887432107",
}

# GraphQL operations used (extracted from the app bundle). getFlashcards returns
# topics each holding a list of flashcard `ids`; getFlashcardInfo resolves one id
# to its front/back text.
WILEY_QUERIES = {
    "GetProductInfo": (
        "query GetProductInfo($productId: String!) {"
        " getProductInfo(productId: $productId)"
        " { productId title flashcardCount flashcardTopicCount } }"
    ),
    "GetFlashcards": (
        "query GetFlashcards($productId: String!) {"
        " getFlashcards(productId: $productId)"
        " { placement title topicId ids } }"
    ),
    "GetFlashcardInfo": (
        "query GetFlashcardInfo($flashcardId: String!) {"
        " getFlashcardInfo(flashcardId: $flashcardId)"
        " { backText frontText qtiId title } }"
    ),
}
