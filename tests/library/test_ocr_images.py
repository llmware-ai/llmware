"""OCR persistence regression tests using an isolated SQLite library."""

import copy
import importlib.util
from importlib.machinery import ModuleSpec
import sqlite3

import pytest

from llmware.configs import LLMWareConfig, SQLiteConfig
from llmware.library import Library
from llmware.parsers import ImageParser
from llmware.resources import CollectionRetrieval, CollectionWriter
from llmware.retrieval import Query


@pytest.fixture
def image_library(tmp_path, monkeypatch):
    for attribute in ("_base_fp", "_fp", "_conf", "_supported"):
        monkeypatch.setattr(LLMWareConfig, attribute,
                            copy.deepcopy(getattr(LLMWareConfig, attribute)))
    monkeypatch.setattr(SQLiteConfig, "_conf", copy.deepcopy(SQLiteConfig._conf))
    LLMWareConfig.set_home(str(tmp_path))
    LLMWareConfig.set_active_db("sqlite")
    SQLiteConfig.set_config("sqlite_db_folder_path", str(tmp_path))
    library = Library().create_new_library("ocr_regression")
    record = dict.fromkeys((
        "file_type", "author_or_speaker", "added_to_collection", "file_source",
        "table", "modified_date", "created_date", "creator_tool", "text",
        "header_text", "text_search", "user_tags", "special_field1",
        "special_field2", "special_field3", "graph_status", "dialog"), "")
    record.update(dict.fromkeys(("master_index", "master_index2", "coords_x",
                                "coords_y", "coords_cx", "coords_cy"), 0))
    record.update(block_ID=7, doc_ID=1, content_type="image",
                  external_files="page.png", embedding_flags={})
    CollectionWriter(library.library_name).write_new_parsing_record(record)
    return library


@pytest.mark.parametrize("add_to_library", [True, False])
def test_ocr_text_persistence(image_library, monkeypatch, add_to_library):
    chunks = ["quartz first OCR paragraph", "quartz second OCR paragraph",
              "", "   ", "tiny", "1234567890"]
    calls = []

    def process_ocr(self, image_path, image_name, preserve_spacing):
        calls.append((image_path, image_name, preserve_spacing))
        return chunks

    # OCR itself is mocked, so its optional Python dependency is not required.
    original_find_spec = importlib.util.find_spec

    def find_spec(name, package=None):
        if name == "pytesseract":
            return ModuleSpec(name, loader=None)
        return original_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", find_spec)
    monkeypatch.setattr(ImageParser, "process_ocr", process_ocr)
    name = image_library.library_name
    original_images = list(CollectionRetrieval(name).filter_by_key("content_type", "image"))
    count = image_library.run_ocr_on_images(
        add_to_library=add_to_library, min_size=10, realtime_progress=False)
    assert count == (2 if add_to_library else 0)
    assert calls == [(image_library.image_path, "page.png", False)]
    assert list(CollectionRetrieval(name).filter_by_key("content_type", "image")) == original_images
    blocks = sorted(CollectionRetrieval(name).filter_by_key("content_type", "text"),
                    key=lambda block: block["block_ID"])
    expected = chunks[:2] if add_to_library else []
    assert [block["text"] for block in blocks] == expected
    assert [block["text_search"] for block in blocks] == expected
    assert [block["block_ID"] for block in blocks] == ([100000, 100001] if add_to_library else [])
    assert all(block["special_field1"] == "document-1&block-7" for block in blocks)
    with sqlite3.connect(SQLiteConfig.get_uri_string()) as connection:
        rows = connection.execute(
            "SELECT text_block, text_search FROM ocr_regression WHERE content_type = 'text' ORDER BY block_ID"
        ).fetchall()
    assert rows == [(chunk, chunk) for chunk in expected]
    results = Query(image_library).text_query("quartz")
    assert sorted(result["text"] for result in results) == sorted(expected)
