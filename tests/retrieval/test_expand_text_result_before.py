import pytest

from llmware.library import Library
from llmware.retrieval import Query


@pytest.mark.parametrize("client_type", [Query, Library])
def test_expand_text_result_before_collects_blocks_in_document_order(client_type):
    client = object.__new__(client_type)
    blocks = {
        0: {"block_ID": 0, "doc_ID": 1, "text": "A."},
        1: {"block_ID": 1, "doc_ID": 1, "text": "B."},
        2: {"block_ID": 2, "doc_ID": 1, "text": "C."},
    }
    client.block_lookup = lambda block_id, doc_id: blocks.get(block_id)

    result = client.expand_text_result_before({"block_ID": 3, "doc_ID": 1}, window_size=5)

    assert result["expanded_text"] == "A.B.C."
    assert [block["block_ID"] for block in result["results"]] == [0, 1, 2]


@pytest.mark.parametrize("client_type", [Query, Library])
def test_expand_text_result_before_advances_past_empty_blocks_and_stops_at_gaps(client_type):
    client = object.__new__(client_type)
    blocks = {
        0: {"block_ID": 0, "doc_ID": 1, "text": "A."},
        2: {"block_ID": 2, "doc_ID": 1, "text": "C."},
    }
    client.block_lookup = lambda block_id, doc_id: blocks.get(block_id)

    result = client.expand_text_result_before({"block_ID": 3, "doc_ID": 1}, window_size=400)

    assert result["expanded_text"] == "C."
    assert [block["block_ID"] for block in result["results"]] == [2]

    blocks[1] = {"block_ID": 1, "doc_ID": 1, "text": ""}
    result = client.expand_text_result_before({"block_ID": 3, "doc_ID": 1}, window_size=400)

    assert result["expanded_text"] == "A.C."
    assert [block["block_ID"] for block in result["results"]] == [0, 1, 2]
