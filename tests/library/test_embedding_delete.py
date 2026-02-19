"""Tests for delete_installed_embedding resetting to initial value.

Verifies fix for GitHub issue #1094:
When deleting the last embedding, the embedding field should reset to the initial
value rather than becoming an empty list.
"""

from llmware.resources import SQLiteWriter, PGWriter


class TestEmbeddingRecordHandler:
    """Test _update_embedding_record_handler behavior when deleting embeddings."""

    def test_delete_last_embedding_resets_to_initial_value_sqlite(self):
        """Test that SQLiteWriter resets embedding to initial value after deleting last embedding."""
        initial_embedding = [{"embedding_status": "yes", "embedding_model": "test-model",
                              "embedding_db": "chromadb", "embedded_blocks": 100,
                              "embedding_dims": 384, "time_stamp": "test"}]

        delete_value = {"embedding_status": "delete", "embedding_model": "test-model",
                        "embedding_db": "chromadb", "embedded_blocks": 0,
                        "embedding_dims": 384, "time_stamp": "NA"}

        writer = SQLiteWriter.__new__(SQLiteWriter)
        result = writer._update_embedding_record_handler(
            initial_embedding.copy(), delete_value, delete_record=True
        )

        assert len(result) == 1
        assert result[0]["embedding_status"] == "no"
        assert result[0]["embedding_model"] == "none"
        assert result[0]["embedding_db"] == "none"
        assert result[0]["embedded_blocks"] == 0
        assert result[0]["embedding_dims"] == 0

    def test_delete_last_embedding_resets_to_initial_value_postgres(self):
        """Test that PGWriter resets embedding to initial value after deleting last embedding."""
        initial_embedding = [{"embedding_status": "yes", "embedding_model": "test-model",
                              "embedding_db": "chromadb", "embedded_blocks": 100,
                              "embedding_dims": 384, "time_stamp": "test"}]

        delete_value = {"embedding_status": "delete", "embedding_model": "test-model",
                        "embedding_db": "chromadb", "embedded_blocks": 0,
                        "embedding_dims": 384, "time_stamp": "NA"}

        writer = PGWriter.__new__(PGWriter)
        result = writer._update_embedding_record_handler(
            initial_embedding.copy(), delete_value, delete_record=True
        )

        assert len(result) == 1
        assert result[0]["embedding_status"] == "no"
        assert result[0]["embedding_model"] == "none"
        assert result[0]["embedding_db"] == "none"
        assert result[0]["embedded_blocks"] == 0
        assert result[0]["embedding_dims"] == 0

    def test_delete_one_of_multiple_embeddings_keeps_others(self):
        """Test that deleting one embedding from multiple keeps the others."""
        initial_embeddings = [
            {"embedding_status": "yes", "embedding_model": "model-a",
             "embedding_db": "chromadb", "embedded_blocks": 100,
             "embedding_dims": 384, "time_stamp": "test1"},
            {"embedding_status": "yes", "embedding_model": "model-b",
             "embedding_db": "chromadb", "embedded_blocks": 200,
             "embedding_dims": 768, "time_stamp": "test2"}
        ]

        delete_value = {"embedding_status": "delete", "embedding_model": "model-a",
                        "embedding_db": "chromadb", "embedded_blocks": 0,
                        "embedding_dims": 384, "time_stamp": "NA"}

        writer = SQLiteWriter.__new__(SQLiteWriter)
        result = writer._update_embedding_record_handler(
            initial_embeddings.copy(), delete_value, delete_record=True
        )

        assert len(result) == 1
        assert result[0]["embedding_model"] == "model-b"
        assert result[0]["embedded_blocks"] == 200
