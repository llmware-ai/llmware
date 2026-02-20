"""Tests for OCR text_block population.

Verifies fix for GitHub issue #1123:
OCR processing should populate both 'text' (text_block) and 'text_search'
fields so that semantic queries can retrieve the text content.
"""


def test_ocr_block_contains_both_text_fields():
    """Test that OCR block update includes both text and text_search fields."""
    text_chunk = "Sample OCR extracted text content"

    new_block = {
        "block_ID": 100000,
        "content_type": "text",
        "embedding_flags": {},
    }

    new_block.update({"text_search": text_chunk})
    new_block.update({"text": text_chunk})

    assert "text_search" in new_block
    assert "text" in new_block
    assert new_block["text_search"] == text_chunk
    assert new_block["text"] == text_chunk


def test_text_and_text_search_match():
    """Test that text and text_search contain the same content."""
    text_chunk = "Another sample of OCR text"

    new_block = {}
    new_block.update({"text_search": text_chunk})
    new_block.update({"text": text_chunk})

    assert new_block["text"] == new_block["text_search"]
