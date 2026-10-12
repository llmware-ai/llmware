import json
from unittest.mock import Mock

import pytest
import requests

from solutions.use_cases import adanos_market_sentiment as example


def response(body, status=200):
    value = requests.Response()
    value.status_code = status
    value._content = body
    value._content_consumed = True
    return value


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("ADANOS_API_KEY", "synthetic-placeholder")


def test_without_key_does_not_connect_or_load_model(monkeypatch):
    from llmware.models import ModelCatalog

    monkeypatch.delenv("ADANOS_API_KEY", raising=False)
    monkeypatch.setattr(requests, "get", lambda *a, **kw: pytest.fail("unexpected request"))
    monkeypatch.setattr(ModelCatalog, "load_model", lambda *a, **kw: pytest.fail("unexpected model load"))
    assert example.run_example("EXM", "reddit_stocks", "2026-10-01", "2026-10-02") is None


@pytest.mark.parametrize("source,path", [
    ("reddit_stocks", "reddit/stocks/v1/stock/EXM"),
    ("reddit_crypto", "reddit/crypto/v1/token/EXM"),
    ("x_stocks", "x/stocks/v1/stock/EXM"),
    ("news_stocks", "news/stocks/v1/stock/EXM"),
    ("polymarket_stocks", "polymarket/stocks/v1/stock/EXM"),
])
def test_source_routes_and_utc_context(key, monkeypatch, source, path):
    get = Mock(return_value=response(b'{"sentiment_score":0.3,"mentions":12}'))
    monkeypatch.setattr(requests, "get", get)
    context = example.fetch_sentiment("EXM", source, "2026-10-01", "2026-10-02")
    get.assert_called_once_with(f"https://api.adanos.org/{path}", headers={"X-API-Key": "synthetic-placeholder"}, params={"from": "2026-10-01", "to": "2026-10-02"}, timeout=20, allow_redirects=False, stream=True)
    assert context["data"] == {"sentiment_score": 0.3, "mentions": 12}
    assert context["source"] == source
    assert context["from"] == "2026-10-01"
    assert "synthetic-placeholder" not in json.dumps(context)


@pytest.mark.parametrize("args", [
    ("EXM", "news_crypto", "2026-10-01", "2026-10-02"),
    ("../health", "reddit_stocks", "2026-10-01", "2026-10-02"),
    ("EXM", "reddit_stocks", "2026-02-30", "2026-10-02"),
    ("EXM", "reddit_stocks", "2026-10-03", "2026-10-02"),
])
def test_invalid_inputs_never_connect(key, monkeypatch, args):
    monkeypatch.setattr(requests, "get", lambda *a, **kw: pytest.fail("unexpected request"))
    with pytest.raises(ValueError):
        example.fetch_sentiment(*args)


@pytest.mark.parametrize("status", [301, 401, 403, 429, 500])
def test_http_errors_do_not_leak_body_or_become_neutral(key, monkeypatch, status):
    monkeypatch.setattr(requests, "get", Mock(return_value=response(b"private-provider-detail", status)))
    with pytest.raises(RuntimeError, match=f"HTTP {status}") as error:
        example.fetch_sentiment("EXM", "reddit_stocks", "2026-10-01", "2026-10-02")
    assert "private-provider-detail" not in str(error.value)


@pytest.mark.parametrize("failure", ["timeout", "json", "oversize"])
def test_unavailable_data_does_not_become_evidence(key, monkeypatch, failure):
    get = Mock(return_value=response(b"data"))
    if failure == "timeout":
        get.side_effect = requests.Timeout("private-provider-detail")
    elif failure == "json":
        get.return_value = response(b"private-provider-detail")
    else:
        get.return_value = response(b"x" * 32_001)
    monkeypatch.setattr(requests, "get", get)
    with pytest.raises(RuntimeError) as error:
        example.fetch_sentiment("EXM", "reddit_stocks", "2026-10-01", "2026-10-02")
    assert "private-provider-detail" not in str(error.value)


def test_handoff_to_native_model_preserves_context_and_provenance(key, monkeypatch):
    from llmware.models import ModelCatalog

    monkeypatch.setattr(requests, "get", Mock(return_value=response(b'{"sentiment_score":0.3}')))
    model = Mock()
    model.inference.return_value = {"llm_response": "Synthetic answer"}
    monkeypatch.setattr(ModelCatalog, "load_model", Mock(return_value=model))
    result = example.run_example("BRK", "news_stocks", "2026-10-01", "2026-10-02")
    assert result["answer"] == {"llm_response": "Synthetic answer"}
    context = json.loads(model.inference.call_args.kwargs["add_context"])
    assert context == result["evidence"]
    assert context["data"] == {"sentiment_score": 0.3}
    assert context["source"] == "news_stocks"
    assert "not investment advice" in model.inference.call_args.args[0]


def test_context_budget_refuses_before_loading_model(key, monkeypatch):
    from llmware.models import ModelCatalog

    monkeypatch.setattr(requests, "get", Mock(return_value=response(json.dumps({"text": "x" * 3000}).encode())))
    monkeypatch.setattr(ModelCatalog, "load_model", lambda *a, **kw: pytest.fail("unexpected model load"))
    with pytest.raises(RuntimeError, match="budget"):
        example.run_example("EXM", "reddit_stocks", "2026-10-01", "2026-10-02")


@pytest.mark.parametrize("payload", [None, [], {"error": "unavailable"}])
def test_invalid_snapshot_shape_is_not_evidence(key, monkeypatch, payload):
    monkeypatch.setattr(requests, "get", Mock(return_value=response(json.dumps(payload).encode())))
    with pytest.raises(RuntimeError, match="valid snapshot"):
        example.fetch_sentiment("EXM", "reddit_stocks", "2026-10-01", "2026-10-02")
