"""Stable signatures, values, serialization and executable public examples."""

from __future__ import annotations

import copy
import doctest
import inspect
import pickle
import typing
from dataclasses import FrozenInstanceError, asdict, replace

import pytest

import viaheader
from viaheader import Hop, ViaError, append, build, has_loop, parse


@pytest.mark.parametrize("name", viaheader.__all__)
def test_public_examples_and_runtime_annotations(name: str) -> None:
    obj = getattr(viaheader, name)
    assert ">>>" in (inspect.getdoc(obj) or "")
    assert typing.get_type_hints(obj)
    finder = doctest.DocTestFinder()
    runner = doctest.DocTestRunner()
    for example in finder.find(obj, name, globs=vars(viaheader)):
        runner.run(example)
    assert runner.tries > 0
    assert runner.failures == 0


def test_hop_properties_have_executable_examples() -> None:
    runner = doctest.DocTestRunner()
    for name in ("host", "port"):
        prop = getattr(Hop, name)
        assert ">>>" in prop.__doc__
        example = doctest.DocTestParser().get_doctest(prop.__doc__, {}, name, "Hop", 0)
        runner.run(example)
    assert runner.tries == 5 and runner.failures == 0


def test_stable_parameter_names_kinds_and_defaults() -> None:
    contracts = [
        (Hop, "received_by version protocol comment", {"protocol": "HTTP", "comment": None}),
        (ViaError, "message line position", {"line": None, "position": None}),
        (parse, "value strict", {"strict": False}),
        (build, "hops", {}),
        (
            append,
            "existing hop pseudonyms drop_comments",
            {"pseudonyms": None, "drop_comments": False},
        ),
        (has_loop, "value name names", {}),
    ]
    for obj, names, defaults in contracts:
        assert callable(obj)
        parameters = inspect.signature(obj).parameters
        assert list(parameters) == names.split()
        assert {k: v.default for k, v in parameters.items() if v.default is not v.empty} == defaults
        for name, param in parameters.items():
            expected: object = inspect.Parameter.POSITIONAL_OR_KEYWORD
            if name in {"line", "position", "strict", "pseudonyms", "drop_comments"}:
                expected = inspect.Parameter.KEYWORD_ONLY
            elif name == "names":
                expected = inspect.Parameter.VAR_POSITIONAL
            assert param.kind == expected


def test_frozen_hop_value_contract() -> None:
    hop = Hop("edge:80", "2", "http", "cache")
    assert asdict(hop) == {
        "received_by": "edge:80",
        "version": "2",
        "protocol": "HTTP",
        "comment": "cache",
    }
    assert hash(hop) == hash(Hop("edge:80", "2", "HTTP", "cache"))
    assert hop != Hop("other", "2", "HTTP", "cache")
    assert repr(hop) == "Hop(received_by='edge:80', version='2', protocol='HTTP', comment='cache')"
    assert replace(hop, version="1.1") == Hop("edge:80", "1.1", comment="cache")
    with pytest.raises(FrozenInstanceError):
        hop.version = "3"  # type: ignore[misc]
    assert copy.copy(hop) == copy.deepcopy(hop) == pickle.loads(pickle.dumps(hop)) == hop
    assert Hop.__module__ == ViaError.__module__ == "viaheader"


def test_error_message_position_copy_and_pickle() -> None:
    error = ViaError("bad", line=2, position=7)
    for restored in (
        error,
        copy.copy(error),
        copy.deepcopy(error),
        pickle.loads(pickle.dumps(error)),
    ):
        assert isinstance(restored, ViaError)
        assert str(restored) == "bad (line 2, offset 7)"
        assert restored.args == ("bad (line 2, offset 7)",)
        assert (restored.line, restored.position) == (2, 7)
    plain = ViaError("bad")
    assert str(plain) == "bad" and plain.line is None and plain.position is None


def test_iterable_inputs_are_consumed_once_and_ordered() -> None:
    hops = [Hop("a", "1"), Hop("b", "2")]
    assert build(hop for hop in hops) == "1 a, 2 b"
    assert append((line for line in ["1 a", "2 b"]), Hop("c", "3")) == "1 a, 2 b, 3 c"
    assert has_loop((line for line in ["1 a", "2 b"]), "b")


def test_a_pseudonym_collision_uses_the_last_mapping_entry() -> None:
    assert append("1 p", Hop("me", "2"), pseudonyms={"p": "first", "P": "last"}) == "1 last, 2 me"


def test_all_names_and_mappings_are_validated_before_reading_input() -> None:
    with pytest.raises(ViaError):
        has_loop("1 p", "p", "invalid name")
    with pytest.raises(ViaError):
        append(None, Hop("me", "1"), pseudonyms={"unused": "invalid name"})


def test_empty_port_is_a_wildcard_and_zero_is_a_specific_port() -> None:
    assert has_loop("1 p:42", "p:")
    assert has_loop("1 p:000", "p:0")
    assert not has_loop("1 p", "p:0")
    assert not has_loop("1 p:1", "p:0")
