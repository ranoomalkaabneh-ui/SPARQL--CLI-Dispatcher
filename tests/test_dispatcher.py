import subprocess
import sys

import pytest

from query import build_query


def test_authors_intent_returns_select():
    sparql = build_query("list authors at NeurIPS")
    assert "SELECT DISTINCT ?author" in sparql
    assert ":publishedIn :NeurIPS" in sparql


def test_papers_per_topic_uses_group_by():
    sparql = build_query("papers per topic")
    assert "COUNT(?paper)" in sparql
    assert "GROUP BY ?topic" in sparql


def test_construct_intent_returns_construct():
    sparql = build_query("2023 papers with authors")
    assert "CONSTRUCT" in sparql
    assert ":year 2023" in sparql


def test_ask_intent_returns_ask():
    sparql = build_query("has prolific author")
    assert "ASK" in sparql
    assert "HAVING (COUNT(?p) > 10)" in sparql


def test_unknown_intent_raises_value_error():
    with pytest.raises(ValueError):
        build_query("unknown intent")


def test_unknown_intent_cli_exits_nonzero():
    result = subprocess.run(
        [sys.executable, "query.py", "unknown intent"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Unknown intent" in result.stderr
    assert "usage:" in result.stderr