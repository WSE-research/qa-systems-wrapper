"""Unit tests for routers/config.py: the question-normalisation, gerbil-body
parsing, JSON loading and MongoDB cache helpers (the DB is faked)."""
import json
from unittest.mock import MagicMock

from routers import config


def test_preprocess_normalises_whitespace_and_case():
    assert config.preprocess("  Where was Angela Merkel born?? ") == "where was angela merkel born"


def test_preprocess_keeps_cyrillic_letters():
    assert config.preprocess("Где место рождения?") == "где место рождения"


def test_parse_gerbil_extracts_query_and_lang():
    body = "b'query=Where%20born&lang=en'"
    query, lang = config.parse_gerbil(body)
    assert query == "Where%20born"
    assert lang == "en"


def test_read_json_round_trip(tmp_path):
    data = {"concepts": ["a", "b"]}
    path = tmp_path / "concepts.json"
    path.write_text(json.dumps(data))
    assert config.read_json(str(path)) == data


def test_find_in_cache_returns_stored_output(monkeypatch):
    fake_db = MagicMock()
    fake_db.__getitem__.return_value.find_one.return_value = {"output": {"answer": 42}}
    monkeypatch.setattr(config, "db", fake_db)
    assert config.find_in_cache("sys", "/p", "Question?") == {"answer": 42}


def test_find_in_cache_returns_none_on_miss(monkeypatch):
    fake_db = MagicMock()
    fake_db.__getitem__.return_value.find_one.return_value = None
    monkeypatch.setattr(config, "db", fake_db)
    assert config.find_in_cache("sys", "/p", "Question?") is None


def test_find_in_cache_swallows_errors(monkeypatch):
    fake_db = MagicMock()
    fake_db.__getitem__.return_value.find_one.side_effect = RuntimeError("boom")
    monkeypatch.setattr(config, "db", fake_db)
    assert config.find_in_cache("sys", "/p", "Question?") is None


def test_cache_question_inserts_document(monkeypatch):
    fake_db = MagicMock()
    monkeypatch.setattr(config, "db", fake_db)
    config.cache_question("sys", "/p", "Question?", {"x": 1}, {"answer": 1})
    fake_db.__getitem__.return_value.insert_one.assert_called_once()
    inserted = fake_db.__getitem__.return_value.insert_one.call_args[0][0]
    assert inserted["question"] == "question"
    assert inserted["raw_question"] == "Question?"


def test_delete_cache_calls_delete_many(monkeypatch):
    fake_db = MagicMock()
    monkeypatch.setattr(config, "db", fake_db)
    config.delete_cache("sys", "/p")
    fake_db.__getitem__.return_value.delete_many.assert_called_once_with({"path": "/p"})
