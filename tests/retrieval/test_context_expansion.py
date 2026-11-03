"""Exercise neighboring-context retrieval against an isolated SQLite library."""

import pytest

from llmware.configs import LLMWareConfig, SQLiteConfig
from llmware.library import Library
from llmware.resources import CollectionWriter
from llmware.retrieval import Query


@pytest.fixture(params=[Library, Query], ids=["library", "query"])
def context_source(request, tmp_path, monkeypatch):
    monkeypatch.setitem(LLMWareConfig._base_fp, "home_path", str(tmp_path))
    monkeypatch.setitem(LLMWareConfig._conf, "collection_db", "sqlite")
    monkeypatch.setitem(SQLiteConfig._conf, "sqlite_db_folder_path", str(tmp_path))
    library = Library().create_new_library("context_expansion")

    def build(rows):
        def insert(doc_id, block_id, text, file_source):
            record = dict.fromkeys([
                "content_type", "file_type", "master_index2", "coords_x", "coords_y", "coords_cx", "coords_cy",
                "author_or_speaker", "added_to_collection", "table", "modified_date", "created_date", "creator_tool",
                "external_files", "header_text", "user_tags", "special_field1", "special_field2", "special_field3",
                "graph_status", "dialog",
            ], "")
            record.update(doc_ID=doc_id, block_ID=block_id, master_index=1,
                          text=text, text_search=text, file_source=file_source)
            CollectionWriter(library.library_name).write_new_parsing_record(record)

        for block_id, text in rows:
            insert(1, block_id, text, "example.txt")
        # A matching block ID in another document must not enter the context.
        insert(2, 0, "unrelated", "other.txt")
        source = library if request.param is Library else Query(library, save_history=False)
        lookup = source.block_lookup
        visited = set()

        def bounded_lookup(block_id, doc_id):
            # Detect the original non-progressing loop without a hanging test.
            assert (doc_id, block_id) not in visited, "context expansion revisited the same block"
            visited.add((doc_id, block_id))
            return lookup(block_id, doc_id)

        monkeypatch.setattr(source, "block_lookup", bounded_lookup)
        return source

    return build


@pytest.mark.parametrize("window, expected_ids, expected_text", [
    (5, [0, 1, 2], "A.B.C."),
    (3, [1, 2], "B.C."),
    (1, [2], "C."),
    (0, [], ""),
    (-1, [], ""),
])
def test_preceding_context_in_document_order(context_source, window, expected_ids, expected_text):
    source = context_source([(0, "A."), (1, "B."), (2, "C."), (3, "anchor")])
    anchor = {"doc_ID": 1, "block_ID": 3}
    result = source.expand_text_result_before(anchor, window_size=window)
    assert result["expanded_text"] == expected_text
    assert [block["block_ID"] for block in result["results"]] == expected_ids
    assert all(block["doc_ID"] == 1 for block in result["results"])
    assert anchor == {"doc_ID": 1, "block_ID": 3}


@pytest.mark.parametrize("rows, anchor_id, expected_ids, expected_text", [
    ([(0, "A.")], 0, [], ""),
    ([(0, "A.")], 3, [], ""),
    ([(0, "A."), (2, "C.")], 3, [2], "C."),
    ([(0, "A."), (1, ""), (2, "C.")], 3, [0, 1, 2], "A.C."),
    ([(0, ""), (1, "")], 2, [0, 1], ""),
])
def test_preceding_context_terminates_at_boundary_or_gap(context_source, rows, anchor_id, expected_ids, expected_text):
    source = context_source(rows)
    result = source.expand_text_result_before({"doc_ID": 1, "block_ID": anchor_id}, window_size=20)
    assert result["expanded_text"] == expected_text
    assert [block["block_ID"] for block in result["results"]] == expected_ids


@pytest.mark.parametrize("rows, window, expected_ids, expected_text", [
    ([(0, "anchor"), (1, "B."), (2, "C.")], 3, [1, 2], "B.C."),
    ([(0, "anchor"), (1, ""), (2, "C.")], 3, [1, 2], "C."),
    ([(0, "anchor"), (2, "C.")], 20, [], ""),
    ([(0, "anchor"), (1, "B.")], 0, [], ""),
])
def test_following_context_control(context_source, rows, window, expected_ids, expected_text):
    source = context_source(rows)
    result = source.expand_text_result_after({"doc_ID": 1, "block_ID": 0}, window_size=window)
    assert result["expanded_text"] == expected_text
    assert [block["block_ID"] for block in result["results"]] == expected_ids
