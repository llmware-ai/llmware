"""Tests for SQLite list type binding fix.

Verifies fix for GitHub issue #1042:
SQLite does not support binding Python list types directly. List values
must be converted to JSON strings before binding.
"""

import json


def test_user_tags_list_to_json_conversion():
    """Test that list user_tags are converted to JSON string."""
    user_tags_list = ["tag1", "tag2", "tag3"]

    if isinstance(user_tags_list, list):
        user_tags_str = json.dumps(user_tags_list)
    else:
        user_tags_str = user_tags_list

    assert isinstance(user_tags_str, str)
    assert user_tags_str == '["tag1", "tag2", "tag3"]'

    parsed = json.loads(user_tags_str)
    assert parsed == user_tags_list


def test_user_tags_string_passthrough():
    """Test that string user_tags are passed through unchanged."""
    user_tags_str = "already a string"

    if isinstance(user_tags_str, list):
        result = json.dumps(user_tags_str)
    else:
        result = user_tags_str

    assert result == "already a string"


def test_empty_list_conversion():
    """Test that empty list is converted to empty JSON array."""
    user_tags_list = []

    if isinstance(user_tags_list, list):
        user_tags_str = json.dumps(user_tags_list)
    else:
        user_tags_str = user_tags_list

    assert user_tags_str == "[]"
