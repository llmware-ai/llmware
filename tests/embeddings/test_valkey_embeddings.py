"""Test for embedding vector creation, search, and deletion using Valkey as the vector database.

Requirements:
    - Valkey server >= 9.1 running on localhost:6379 with valkey-search module >= 1.2.0
    - pip install valkey-glide-sync

To run a Valkey instance with the search module for testing:
    docker run -d --name valkey-test -p 6379:6379 valkey/valkey-bundle:latest
"""

import os
import pytest
import numpy as np

from llmware.configs import LLMWareConfig, ValkeyConfig, VectorDBRegistry
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


def is_valkey_available():
    """Check if a Valkey server with the search module is reachable."""
    try:
        from glide_sync import GlideClient
        from glide_shared.config import GlideClientConfiguration, NodeAddress

        host = ValkeyConfig.get_config("host")
        port = ValkeyConfig.get_config("port")

        addresses = [NodeAddress(host=host, port=port)]
        config = GlideClientConfiguration(addresses=addresses)
        client = GlideClient.create(config)

        # Ping to verify connectivity
        client.custom_command(["PING"])
        client.close()
        return True
    except Exception:
        return False


def is_torch_available():
    """Check if torch is installed (needed for embedding models)."""
    try:
        import torch
        return True
    except ImportError:
        return False


_valkey_available = is_valkey_available()
_torch_available = is_torch_available()

# Skip integration tests if Valkey or torch is not available
requires_valkey = pytest.mark.skipif(
    not (_valkey_available and _torch_available),
    reason="Requires Valkey server with valkey-search module and torch installed"
)


@pytest.fixture
def library_with_docs():
    """Create a library with sample documents for embedding tests."""

    LLMWareConfig().set_active_db("sqlite")

    library_name = "test_valkey_embeddings"

    # Clean up any previous test library
    try:
        Library().delete_library(library_name)
    except Exception:
        pass

    library = Library().create_new_library(library_name)

    # Load sample files
    sample_files_path = Setup().load_sample_files(over_write=False)

    # Parse a small subset of documents
    library.add_files(
        input_folder_path=os.path.join(sample_files_path, "Agreements"),
        chunk_size=400,
        max_chunk_size=600,
        smart_chunking=1
    )

    yield library

    # Cleanup
    try:
        Library().delete_library(library_name)
    except Exception:
        pass


class TestValkeyEmbeddings:
    """Tests for the Valkey vector database integration."""

    def test_valkey_registered(self):
        """Verify Valkey is registered in the VectorDBRegistry."""
        dbs = VectorDBRegistry.get_vector_db_list()
        assert "valkey" in dbs
        assert dbs["valkey"]["class"] == "EmbeddingValkey"
        assert dbs["valkey"]["module"] == "llmware.embeddings"

    def test_valkey_config(self):
        """Verify ValkeyConfig has expected defaults."""
        assert ValkeyConfig.get_config("host") == os.environ.get("USER_MANAGED_VALKEY_HOST", "localhost")
        assert ValkeyConfig.get_config("port") == int(os.environ.get("USER_MANAGED_VALKEY_PORT", 6379))
        assert ValkeyConfig.get_config("use_tls") is False

    def test_valkey_config_set(self):
        """Verify ValkeyConfig can be updated."""
        original_host = ValkeyConfig.get_config("host")
        ValkeyConfig.set_config("host", "custom-host")
        assert ValkeyConfig.get_config("host") == "custom-host"
        # Restore
        ValkeyConfig.set_config("host", original_host)

    def test_embedding_class_loads(self):
        """Verify EmbeddingValkey class can be imported."""
        from llmware.embeddings import EmbeddingValkey
        assert EmbeddingValkey is not None

    @requires_valkey
    def test_install_valkey_embedding(self, library_with_docs):
        """Test creating embeddings and storing them in Valkey."""

        library = library_with_docs
        vector_db = "valkey"
        embedding_model = "mini-lm-sbert"

        LLMWareConfig().set_vector_db(vector_db)

        # Create the embedding
        library.install_new_embedding(
            embedding_model_name=embedding_model,
            vector_db=vector_db,
            batch_size=100
        )

        # Verify embedding was created
        embedding_record = library.get_embedding_status()
        assert embedding_record is not None
        assert len(embedding_record) > 0

    @requires_valkey
    def test_semantic_query_valkey(self, library_with_docs):
        """Test semantic search against Valkey vector index."""

        library = library_with_docs
        vector_db = "valkey"
        embedding_model = "mini-lm-sbert"

        LLMWareConfig().set_vector_db(vector_db)

        # Create the embedding
        library.install_new_embedding(
            embedding_model_name=embedding_model,
            vector_db=vector_db,
            batch_size=100
        )

        # Run a semantic query
        query_results = Query(library).semantic_query("incentive compensation", result_count=10)

        assert query_results is not None
        assert len(query_results) > 0

        # Verify result structure
        first_result = query_results[0]
        assert "text" in first_result
        assert "file_source" in first_result
        assert "distance" in first_result

    @requires_valkey
    def test_delete_valkey_embedding(self, library_with_docs):
        """Test deleting a Valkey vector index."""

        library = library_with_docs
        vector_db = "valkey"
        embedding_model = "mini-lm-sbert"

        LLMWareConfig().set_vector_db(vector_db)

        # Create the embedding
        library.install_new_embedding(
            embedding_model_name=embedding_model,
            vector_db=vector_db,
            batch_size=100
        )

        # Delete the embedding
        library.delete_installed_embedding(
            embedding_model_name=embedding_model,
            vector_db=vector_db
        )

        # Verify embedding was removed
        embedding_record = library.get_embedding_status()
        # After deletion, the embedding record should be empty or not contain our model
        has_valkey_embedding = False
        if embedding_record:
            for record in embedding_record:
                if isinstance(record, dict) and record.get("embedding_db") == "valkey":
                    has_valkey_embedding = True
        assert not has_valkey_embedding
