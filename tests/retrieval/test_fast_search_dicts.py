""" Regression tests for the in-memory phrase search in Utilities().fast_search_dicts - no models or DB required. """

from llmware.util import Utilities


def search(query, texts, **kwargs):
    entries = [{"text": t} for t in texts]
    return [e["text"] for e in Utilities().fast_search_dicts(query, entries, **kwargs)]


def test_multi_token_phrase_at_end_of_text():
    assert search("governing law", ["This agreement has governing law"]) == ["This agreement has governing law"]


def test_multi_token_phrase_is_whole_text():
    assert search("governing law", ["governing law"]) == ["governing law"]


def test_multi_token_phrase_at_start_and_middle_of_text():
    texts = ["governing law applies", "the governing law of Delaware"]
    assert search("governing law", texts) == texts


def test_three_token_phrase_at_end_of_text():
    assert search("target annual bonus", ["Executive is eligible for a target annual bonus"]) == \
        ["Executive is eligible for a target annual bonus"]


def test_partial_or_noncontiguous_phrase_does_not_match():
    texts = ["governing", "governing contract terms", "governing contract law", "law governing"]
    assert search("governing law", texts) == []


def test_single_token_query_at_end_of_text():
    assert search("salary", ["base salary"]) == ["base salary"]


def test_custom_text_key_and_metadata_with_phrase_at_end():
    entries = [{"body": "Section 12 Governing Law.", "master_index": 4}]
    output = Utilities().fast_search_dicts("governing law", entries, text_key="body")

    assert len(output) == 1
    assert output[0]["page_num"] == 4
    assert output[0]["query"] == "governing law"


def test_phrase_ending_in_stop_word_when_stop_words_kept():
    texts = ["the parties agree to the terms set out below", "the terms set out"]
    assert search("set out", texts, remove_stop_words=False) == texts
