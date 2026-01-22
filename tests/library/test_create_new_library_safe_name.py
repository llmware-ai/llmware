"""Tests for create_new_library safe name handling.

This tests the fix for issue #1155 where check_if_library_exists was called
before applying the safe_name transformation, causing inconsistent behavior.
"""

import os
from unittest.mock import MagicMock, patch

from llmware.library import Library


def test_create_new_library_uses_safe_name_for_existence_check():
    """Test that safe_name is applied before checking library existence.

    This ensures that both the existence check and library creation use
    the same transformed name, fixing the bug in issue #1155.
    """
    library = Library()

    # Mock the methods to track call order and arguments
    original_library_name = "test library with spaces"
    secure_name = "test_library_with_spaces"
    db_safe_name = "test_library_with_spaces_db"

    with patch.object(library, 'check_if_library_exists', return_value=True) as mock_check, \
         patch.object(library, 'load_library', return_value=library) as mock_load, \
         patch('llmware.library.Utilities') as mock_utilities, \
         patch('llmware.library.CollectionRetrieval') as mock_retrieval:

        # Setup mocks
        mock_utilities.return_value.secure_filename.return_value = secure_name
        mock_retrieval_instance = MagicMock()
        mock_retrieval_instance.safe_name.return_value = db_safe_name
        mock_retrieval.return_value = mock_retrieval_instance

        # Call create_new_library
        library.create_new_library(original_library_name)

        # Verify safe_name was called with the secure filename
        mock_retrieval_instance.safe_name.assert_called_once_with(secure_name)

        # Verify check_if_library_exists was called with the db_safe_name
        # This is the key assertion - before the fix, it was called with secure_name
        mock_check.assert_called_once_with(db_safe_name, "llmware")

        # Verify load_library was called with the db_safe_name
        mock_load.assert_called_once_with(db_safe_name, "llmware")


def test_create_new_library_sets_library_name_to_safe_name():
    """Test that self.library_name is set to the safe name early."""
    library = Library()

    original_library_name = "test-library"
    secure_name = "test_library"
    db_safe_name = "test_library_safe"

    with patch.object(library, 'check_if_library_exists', return_value=True) as mock_check, \
         patch.object(library, 'load_library', return_value=library) as mock_load, \
         patch('llmware.library.Utilities') as mock_utilities, \
         patch('llmware.library.CollectionRetrieval') as mock_retrieval:

        mock_utilities.return_value.secure_filename.return_value = secure_name
        mock_retrieval_instance = MagicMock()
        mock_retrieval_instance.safe_name.return_value = db_safe_name
        mock_retrieval.return_value = mock_retrieval_instance

        library.create_new_library(original_library_name)

        # After the fix, library_name should be set to db_safe_name
        assert library.library_name == db_safe_name
