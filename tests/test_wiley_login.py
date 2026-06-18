"""Offline tests for credential loading (no browser, no network).

load_credentials reads values verbatim so passwords full of special characters
work without any quoting/escaping -- and a malformed file never leaks the
password into a traceback.
"""

import pytest

from wiley_login import load_credentials


def _write(tmp_path, text):
    p = tmp_path / ".env"
    p.write_text(text, encoding="utf-8")
    return p


def test_bare_positional_lines(tmp_path):
    creds = load_credentials(_write(tmp_path, "you@example.com\ns3cr#t&p@ss\n"))
    assert creds["username"] == "you@example.com"
    assert creds["password"] == "s3cr#t&p@ss"


def test_values_are_verbatim_special_chars(tmp_path):
    # & $ \ ' " : = must all survive untouched -- the whole reason we dropped YAML.
    pw = "&=bgX&i/$O\\f'ifc\"nZ7@:x=y"
    creds = load_credentials(_write(tmp_path, f"user@x.com\n{pw}\n"))
    assert creds["password"] == pw


def test_keyed_form(tmp_path):
    creds = load_credentials(_write(tmp_path, "username: user@x.com\npassword: pw123\n"))
    assert creds == {"username": "user@x.com", "password": "pw123"}


def test_keyed_password_keeps_separators(tmp_path):
    # Only the first separator splits, so ':' / '=' inside the value survive.
    creds = load_credentials(_write(tmp_path, "username=user@x.com\npassword=a:b=c\n"))
    assert creds["password"] == "a:b=c"


def test_comments_and_blank_lines_ignored(tmp_path):
    text = "# a comment\n\nyou@example.com\n\n# another\nmypw\n"
    creds = load_credentials(_write(tmp_path, text))
    assert creds["username"] == "you@example.com"
    assert creds["password"] == "mypw"


def test_missing_file_raises(tmp_path):
    with pytest.raises(SystemExit):
        load_credentials(tmp_path / "nope.env")


def test_incomplete_raises(tmp_path):
    with pytest.raises(SystemExit):
        load_credentials(_write(tmp_path, "only-a-username\n"))
