"""Offline tests for the CISSP flashcard scraper (no network access)."""

from pathlib import Path

import config
import scraper
from scraper import Flashcard

FIXTURE = (Path(__file__).parent / "fixtures" / "sample.html").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def test_clean_text_collapses_whitespace_and_unescapes():
    assert scraper.clean_text("  hello\n   world  ") == "hello world"
    assert scraper.clean_text("accuracy &amp; completeness") == "accuracy & completeness"
    assert scraper.clean_text("") == ""


def test_sanitize_field_strips_tabs_and_newlines():
    assert scraper.sanitize_field("a\tb\nc\rd") == "a b c d"


# --------------------------------------------------------------------------- #
# Parsing: the three supported shapes
# --------------------------------------------------------------------------- #
def test_parse_definition_list():
    cards = scraper.parse_cards(FIXTURE, config.DEFAULT_SELECTORS)
    terms = [c.term for c in cards]

    # Both Availability entries appear (dedupe happens later); Orphan is skipped.
    assert terms == ["Confidentiality", "Integrity", "Availability", "Availability"]
    assert "Orphan Term" not in terms

    integrity = next(c for c in cards if c.term == "Integrity")
    assert integrity.definition == (
        "Safeguarding the accuracy & completeness of information and processing methods."
    )


def test_parse_two_column_table():
    cfg = {
        "row_selector": "table.terms tr",
        "term_selector": "td:nth-of-type(1)",
        "definition_selector": "td:nth-of-type(2)",
    }
    cards = scraper.parse_cards(FIXTURE, cfg)
    assert [c.term for c in cards] == ["AAA", "DAC"]  # header row (th) skipped
    assert cards[0].definition == "Authentication, Authorization, and Accounting."


def test_parse_list_items_with_bold_term():
    cfg = {"row_selector": "ul.defs li", "term_selector": "strong", "definition_selector": None}
    cards = scraper.parse_cards(FIXTURE, cfg)
    by_term = {c.term: c.definition for c in cards}
    assert by_term["Nonrepudiation"] == "assurance that a party cannot deny a previous action."
    assert by_term["Least Privilege"] == "granting only the access necessary to perform a task."


# --------------------------------------------------------------------------- #
# Dedupe
# --------------------------------------------------------------------------- #
def test_dedupe_keeps_longest_definition_and_sorts():
    cards = scraper.parse_cards(FIXTURE, config.DEFAULT_SELECTORS)
    deduped = scraper.dedupe(cards)

    assert [c.term for c in deduped] == ["Availability", "Confidentiality", "Integrity"]
    availability = next(c for c in deduped if c.term == "Availability")
    assert "reliable and timely" in availability.definition  # the longer definition won


def test_dedupe_is_case_insensitive():
    cards = [Flashcard("DAC", "short"), Flashcard("dac", "a much longer definition")]
    deduped = scraper.dedupe(cards)
    assert len(deduped) == 1
    assert deduped[0].definition == "a much longer definition"


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #
def test_export_quizlet_txt_one_card_per_line(tmp_path):
    cards = [Flashcard("Term A", "Def A"), Flashcard("Term B", "Def B")]
    out = tmp_path / "deck.txt"
    scraper.export_quizlet_txt(cards, out)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines == ["Term A\tDef A", "Term B\tDef B"]
    # Exactly one tab per line keeps each card intact on import.
    assert all(line.count("\t") == 1 for line in lines)


def test_export_sanitizes_embedded_delimiters(tmp_path):
    cards = [Flashcard("Has\ttab", "multi\nline\tdefinition")]
    out = tmp_path / "deck.txt"
    scraper.export_quizlet_txt(cards, out)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert lines[0].count("\t") == 1
    assert lines[0] == "Has tab\tmulti line definition"
