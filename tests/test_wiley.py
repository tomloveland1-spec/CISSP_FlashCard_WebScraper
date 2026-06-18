"""Offline tests for the Wiley GraphQL scraper (no network, no browser)."""

import pytest

import wiley
from scraper import Flashcard


# --------------------------------------------------------------------------- #
# strip_html
# --------------------------------------------------------------------------- #
def test_strip_html_removes_tags_and_unescapes():
    assert wiley.strip_html("<p>Hello&nbsp;<b>World</b></p>") == "Hello World"
    assert wiley.strip_html("Risk = likelihood &amp; impact") == "Risk = likelihood & impact"
    assert wiley.strip_html("") == ""
    assert wiley.strip_html(None) == ""


# --------------------------------------------------------------------------- #
# collect_cards (with a fake client -- no network)
# --------------------------------------------------------------------------- #
class FakeClient:
    """Stand-in for WileyClient exposing the two methods collect_cards uses."""

    def __init__(self, topics, infos):
        self._topics = topics
        self._infos = infos

    def flashcard_topics(self, product_id):
        return self._topics

    def flashcard_info(self, flashcard_id):
        return self._infos[flashcard_id]


def test_collect_cards_builds_flashcards_from_topics():
    topics = [
        {"title": "Domain 1", "topicId": "t1", "ids": ["a", "b"]},
        {"title": "Domain 2", "topicId": "t2", "ids": ["c", "empty"]},
    ]
    infos = {
        "a": {"frontText": "<b>Confidentiality</b>", "backText": "Only the authorized can read it."},
        "b": {"frontText": "Integrity", "backText": "Data is <i>accurate</i> &amp; complete."},
        "c": {"frontText": "Availability", "backText": "Access when needed."},
        "empty": {"frontText": "", "backText": "no front -> dropped"},
    }
    client = FakeClient(topics, infos)
    cards = wiley.collect_cards(client, "pid", max_workers=2)

    by_term = {c.term: c.definition for c in cards}
    assert by_term["Confidentiality"] == "Only the authorized can read it."
    assert by_term["Integrity"] == "Data is accurate & complete."   # HTML stripped, entity unescaped
    assert by_term["Availability"] == "Access when needed."
    assert "" not in by_term            # the empty-front card was dropped
    assert len(cards) == 3


def test_collect_cards_respects_limit():
    topics = [{"title": "D", "topicId": "t", "ids": ["a", "b", "c"]}]
    infos = {k: {"frontText": k.upper(), "backText": f"def {k}"} for k in "abc"}
    cards = wiley.collect_cards(FakeClient(topics, infos), "pid", limit=2, max_workers=2)
    assert len(cards) == 2


# --------------------------------------------------------------------------- #
# WileyClient token handling
# --------------------------------------------------------------------------- #
def test_client_stores_raw_token_and_strips_bearer_prefix():
    # The app sends the raw JWT with no "Bearer " prefix; tolerate a pasted one.
    assert wiley.WileyClient("  rawjwt  ").token == "rawjwt"
    assert wiley.WileyClient("Bearer rawjwt").token == "rawjwt"
    assert wiley.WileyClient("bearer  rawjwt ").token == "rawjwt"
    # A token that merely contains "bearer" later is untouched.
    assert wiley.WileyClient("abearer").token == "abearer"


# --------------------------------------------------------------------------- #
# resolve_token
# --------------------------------------------------------------------------- #
def _args(**overrides):
    args = wiley.build_parser().parse_args([])
    for k, v in overrides.items():
        setattr(args, k, v)
    return args


def test_resolve_token_from_flag():
    assert wiley.resolve_token(_args(token="  abc123  ")) == "abc123"


def test_resolve_token_from_file(tmp_path):
    f = tmp_path / "token.txt"
    f.write_text("filetoken\n", encoding="utf-8")
    assert wiley.resolve_token(_args(token_file=str(f))) == "filetoken"


def test_resolve_token_from_env(monkeypatch):
    monkeypatch.setenv("WILEY_TOKEN", "envtoken")
    assert wiley.resolve_token(_args()) == "envtoken"


def test_resolve_token_missing_raises(monkeypatch):
    monkeypatch.delenv("WILEY_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        wiley.resolve_token(_args())
