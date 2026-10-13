"""Check the library against RFC 9110, RFC 9112, RFC 3986 and MDN, read from the pinned files.

The files are not committed (URL, size and sha256 in tests/upstream/MANIFEST.json); the
tests that read them skip until `python scripts/fetch_upstream.py` has fetched them.
"""

from __future__ import annotations

import re
import string

from viaheader import Hop, ViaError, build, parse


def _section(text: str, title: str, end: str) -> str:
    """The body of a section: its last heading (the first is in the contents) to ``end``."""
    return text.rsplit(title, 1)[1].split(end, 1)[0]


def _via_lines(text: str) -> list[str]:
    return re.findall(r"^ *Via: (.+)$", text, flags=re.MULTILINE)


def _codes(rule: str) -> set[int]:
    """Code points of an ABNF alternation: quoted literals, %xNN, %xNN-MM and core rules."""
    core = {
        "HTAB": {0x09},
        "SP": {0x20},
        "VCHAR": set(range(0x21, 0x7F)),
        "DIGIT": {ord(c) for c in string.digits},
        "ALPHA": {ord(c) for c in string.ascii_letters},
        "obs-text": set(range(0x80, 0x100)),
    }
    codes = {ord(literal) for literal in re.findall(r'"(.)"', rule)}
    for low, high in re.findall(r"%x([0-9A-F]{2})(?:-([0-9A-F]{2}))?", rule):
        codes |= set(range(int(low, 16), int(high or low, 16) + 1))
    for name, members in core.items():
        if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", rule):
            codes |= members
    return codes


def _rule(text: str, name: str) -> str:
    """One ABNF rule from the collected grammar of Appendix A, joined onto one line."""
    collected = text.rsplit("Appendix A.  Collected ABNF", 1)[1]
    match = re.search(rf"^   {re.escape(name)} = (.+?)(?=^   \S|\Z)", collected, re.M | re.S)
    assert match is not None, name
    return " ".join(re.sub(r";[^\n]*", "", match.group(1)).split())


def test_the_via_grammar_is_the_one_implemented(rfc9110: str) -> None:
    assert _rule(rfc9110, "received-protocol") == '[ protocol-name "/" ] protocol-version'
    assert _rule(rfc9110, "received-by") == 'pseudonym [ ":" port ]'
    assert _rule(rfc9110, "pseudonym") == _rule(rfc9110, "protocol-name") == "token"
    assert _rule(rfc9110, "protocol-version") == "token"
    assert _rule(rfc9110, "comment") == '"(" *( ctext / quoted-pair / comment ) ")"'
    element = "received-protocol RWS received-by [ RWS comment ]"
    assert _rule(rfc9110, "Via") == f'[ ( {element} ) *( OWS "," OWS ( {element} ) ) ]'


def test_the_examples_of_section_7_6_3_parse_strictly(rfc9110: str) -> None:
    lines = _via_lines(_section(rfc9110, "7.6.3.  Via", "7.7.  "))
    assert lines == [
        "1.0 fred, 1.1 p.example.net",
        "1.0 ricky, 1.1 ethel, 1.1 fred, 1.0 lucy",
        "1.0 ricky, 1.1 mertz, 1.0 lucy",
    ]
    assert parse(lines[0], strict=True) == [Hop("fred", "1.0"), Hop("p.example.net", "1.1")]
    for line in lines:
        assert build(parse(line, strict=True)) == line


def test_tokens_are_exactly_the_rfc_9110_tchar(rfc9110: str) -> None:
    tchar = _codes(_rule(rfc9110, "tchar"))
    assert len(tchar) == 77
    for code in range(0x100):
        char = chr(code)
        valid = code in tchar
        assert (parse(f"1.1 a{char}b", strict=False) == [Hop(f"a{char}b", "1.1")]) == valid, code
        try:
            build([Hop("p", f"1{char}")])
        except ViaError:
            assert not valid, code
        else:
            assert valid, code


def test_comments_accept_exactly_ctext_and_quoted_pairs(rfc9110: str) -> None:
    ctext = _codes(_rule(rfc9110, "ctext"))
    quotable = _codes(_rule(rfc9110, "quoted-pair").removeprefix('"\\"'))
    assert len(ctext) == 2 + 7 + 50 + 34 + 128
    assert quotable == ctext | {ord("("), ord(")"), ord("\\")}
    for code in range(0x180):
        char = chr(code)
        for text, valid in ((f"(a{char})", code in ctext), (f"(\\{char})", code in quotable)):
            try:
                parse(f"1.1 p {text}", strict=True)
            except ViaError:
                assert not valid, (code, text)
            else:
                assert valid, (code, text)


def test_ports_are_any_number_of_digits(rfc3986: str) -> None:
    rules = {rule.strip() for rule in re.findall(r"^ +port +=(.+)$", rfc3986, flags=re.MULTILINE)}
    assert rules == {"*DIGIT"}
    for port in ("", "0", "8080", "0000080", "99999999"):
        assert parse(f"1.1 p:{port}", strict=True)[0].received_by == f"p:{port}"


def test_the_list_examples_of_section_5_6_1_2(rfc9110: str) -> None:
    section = _section(rfc9110, "5.6.1.2.  Recipient Requirements", "5.6.2.  ")
    valid, invalid = section.split("In contrast", 1)
    lists = re.findall(r'^ +"([^"]*)"$', valid, flags=re.MULTILINE)
    assert lists == ["foo,bar", "foo ,bar,", "foo , ,bar,charlie"]
    for example in lists:
        value = ",".join(f"1.1 {name}" if name.strip() else name for name in example.split(","))
        names = [name.strip() for name in example.split(",") if name.strip()]
        assert [hop.received_by for hop in parse(value, strict=True)] == names
    empties = re.findall(r'^ +"([^"]*)"$', invalid, flags=re.MULTILINE)
    assert empties == ["", ",", ",   ,"]
    for example in empties:
        assert parse(example, strict=True) == []


def test_obsolete_line_folding_reads_as_space(rfc9112: str) -> None:
    (rule,) = re.findall(r"obs-fold += (.+)", rfc9112)[:1]
    assert rule.split(";")[0].strip() == "OWS CRLF RWS"
    assert parse("1.1 a (x\r\n\ty), 1.1 b") == [Hop("a", "1.1", comment="x  \ty"), Hop("b", "1.1")]


def test_the_mdn_examples(mdn_via: str) -> None:
    examples = _via_lines(mdn_via.split("## Examples", 1)[1])
    assert examples == ["1.1 vegur", "HTTP/1.1 GWA", "1.0 fred, 1.1 p.example.net"]
    assert [parse(line, strict=True) for line in examples] == [
        [Hop("vegur", "1.1")],
        [Hop("GWA", "1.1")],
        [Hop("fred", "1.0"), Hop("p.example.net", "1.1")],
    ]
