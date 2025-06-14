"""Unit tests for the EmbeddingManager class."""

import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pytest

from hubspot_mcp.embeddings.embedding_manager import EmbeddingManager


class TestEmbeddingManager:
    """Test the EmbeddingManager class."""

    @pytest.fixture
    def manager(self):
        """Create an EmbeddingManager instance for testing."""
        return EmbeddingManager(model_name="all-MiniLM-L6-v2", index_type="flat")

    @pytest.fixture
    def mock_entities(self):
        """Create mock HubSpot entities for testing."""
        return [
            {
                "id": "1",
                "properties": {
                    "firstname": "John",
                    "lastname": "Doe",
                    "email": "john@example.com",
                    "jobtitle": "Software Engineer",
                    "company": "TechCorp",
                },
            },
            {
                "id": "2",
                "properties": {
                    "firstname": "Jane",
                    "lastname": "Smith",
                    "email": "jane@example.com",
                    "jobtitle": "Product Manager",
                    "company": "InnovateCorp",
                },
            },
            {
                "id": "3",
                "properties": {
                    "name": "TechCorp",
                    "domain": "techcorp.com",
                    "industry": "Technology",
                    "city": "San Francisco",
                    "country": "USA",
                },
            },
        ]

    def test_initialization(self, manager):
        """Test EmbeddingManager initialization."""
        assert manager.model_name == "all-MiniLM-L6-v2"
        assert manager.index_type == "flat"
        assert manager.model is None
        assert manager.index is None
        assert manager.dimension is None
        assert len(manager.entity_metadata) == 0
        assert len(manager.embedding_cache) == 0

    def test_get_entity_text_contacts(self, manager):
        """Test text extraction for contacts."""
        contact = {
            "properties": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@example.com",
                "jobtitle": "Engineer",
                "company": "TechCorp",
                "phone": "123-456-7890",
            }
        }

        text = manager._get_entity_text(contact, "contacts")
        expected = "John Doe john@example.com Engineer TechCorp 123-456-7890"
        assert text == expected

    def test_get_entity_text_companies(self, manager):
        """Test text extraction for companies."""
        company = {
            "properties": {
                "name": "TechCorp",
                "domain": "techcorp.com",
                "industry": "Technology",
                "description": "Software company",
                "city": "San Francisco",
                "country": "USA",
            }
        }

        text = manager._get_entity_text(company, "companies")
        expected = "TechCorp techcorp.com Technology Software company San Francisco USA"
        assert text == expected

    def test_get_entity_text_deals(self, manager):
        """Test text extraction for deals."""
        deal = {
            "properties": {
                "dealname": "Project Alpha",
                "dealstage": "proposal",
                "pipeline": "sales",
                "closedate": "2024-12-01",
                "amount": "50000",
            }
        }

        text = manager._get_entity_text(deal, "deals")
        expected = "Project Alpha proposal sales 2024-12-01 50000"
        assert text == expected

    def test_get_entity_text_empty_properties(self, manager):
        """Test text extraction with empty properties."""
        entity = {"properties": {}}
        text = manager._get_entity_text(entity, "contacts")
        assert text == ""

    def test_get_entity_text_missing_properties(self, manager):
        """Test text extraction with missing properties key."""
        entity = {}
        text = manager._get_entity_text(entity, "contacts")
        assert text == ""

    def test_generate_cache_key(self, manager):
        """Test cache key generation."""
        text = "John Doe john@example.com"
        key1 = manager._generate_cache_key(text)
        key2 = manager._generate_cache_key(text)

        # Same text should generate same key
        assert key1 == key2
        assert len(key1) == 64  # SHA-256 hex length

        # Different text should generate different keys
        key3 = manager._generate_cache_key("Different text")
        assert key1 != key3

    @patch("sentence_transformers.SentenceTransformer")
    def test_generate_embeddings_with_cache(
        self, mock_transformer, manager, mock_entities
    ):
        """Test embedding generation with caching."""
        # Clear any existing cache first
        manager.embedding_cache.clear()

        # Mock the transformer with realistic dimensions
        mock_model = Mock()
        mock_embeddings = np.random.rand(2, 384)  # Use realistic 384 dimensions
        mock_model.encode.return_value = mock_embeddings
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        # First call should generate embeddings
        embeddings1 = manager.generate_embeddings(mock_entities[:2], "contacts")

        assert embeddings1.shape == (2, 384)
        # Cache should be populated
        assert len(manager.embedding_cache) == 2

        # Second call with same entities should use cache
        # Store original call count to verify caching
        original_call_count = mock_model.encode.call_count
        embeddings2 = manager.generate_embeddings(mock_entities[:2], "contacts")

        # Results should be identical (from cache)
        assert np.array_equal(embeddings1, embeddings2)
        # Encode should not be called again
        assert mock_model.encode.call_count == original_call_count

    @patch("sentence_transformers.SentenceTransformer")
    def test_generate_embeddings_empty_entities(self, mock_transformer, manager):
        """Test embedding generation with empty entities."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        embeddings = manager.generate_embeddings([], "contacts")

        assert embeddings.shape == (0, 384)
        assert mock_model.encode.call_count == 0

    @patch("sentence_transformers.SentenceTransformer")
    @patch("faiss.IndexFlatL2")
    def test_build_index_flat(
        self, mock_index_class, mock_transformer, manager, mock_entities
    ):
        """Test building a flat FAISS index."""
        # Mock transformer with realistic dimensions
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(
            3, 384
        )  # 3 entities, 384 dimensions
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        # Mock FAISS index
        mock_index = Mock()
        mock_index_class.return_value = mock_index

        # Build index
        manager.build_index(mock_entities, "contacts")

        # Verify index creation and usage
        mock_index_class.assert_called_once_with(384)
        mock_index.add.assert_called_once()

        # Check metadata storage
        assert len(manager.entity_metadata) > 0
        assert manager.dimension == 384

    @patch("sentence_transformers.SentenceTransformer")
    @patch("faiss.IndexIVFFlat")
    @patch("faiss.IndexFlatL2")
    def test_build_index_ivf(
        self, mock_flat_index, mock_ivf_index, mock_transformer, manager, mock_entities
    ):
        """Test building an IVF FAISS index."""
        manager.index_type = "ivf"

        # Mock transformer with realistic dimensions
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(
            3, 384
        )  # 3 entities, 384 dimensions
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        # Mock FAISS indexes
        mock_quantizer = Mock()
        mock_flat_index.return_value = mock_quantizer
        mock_index = Mock()
        mock_ivf_index.return_value = mock_index

        # Build index
        manager.build_index(mock_entities, "contacts")

        # Verify IVF index creation
        mock_ivf_index.assert_called_once()
        mock_index.train.assert_called_once()
        mock_index.add.assert_called_once()

    def test_build_index_empty_entities(self, manager):
        """Test building index with empty entities list."""
        manager.build_index([], "contacts")

        assert manager.index is None
        assert len(manager.entity_metadata) == 0

    @patch("sentence_transformers.SentenceTransformer")
    def test_build_index_invalid_type(self, mock_transformer, manager):
        """Test building index with invalid index type."""
        # Mock transformer to ensure we get to the index type validation
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(1, 384)
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model

        manager.index_type = "invalid"

        with pytest.raises(ValueError, match="Unsupported index type"):
            manager.build_index(
                [{"properties": {"firstname": "test", "lastname": "user"}}], "contacts"
            )

    @patch("sentence_transformers.SentenceTransformer")
    def test_search_similar_no_index(self, mock_transformer, manager):
        """Test search with no index available."""
        results = manager.search_similar("software engineer", k=5)
        assert results == []

    @patch("sentence_transformers.SentenceTransformer")
    def test_search_similar_with_results(self, mock_transformer, manager):
        """Test successful similarity search."""
        # Setup mock model
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        mock_transformer.return_value = mock_model

        # Setup mock index
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_index.search.return_value = (
            np.array([[0.5, 1.0]]),  # distances
            np.array([[0, 1]]),  # indices
        )
        manager.index = mock_index

        # Setup metadata
        manager.entity_metadata = {
            0: {
                "entity": {"id": "1", "properties": {"name": "John"}},
                "entity_type": "contacts",
            },
            1: {
                "entity": {"id": "2", "properties": {"name": "Jane"}},
                "entity_type": "contacts",
            },
        }

        results = manager.search_similar("engineer", k=2, threshold=0.5)

        assert len(results) == 2
        entity1, score1 = results[0]
        assert entity1["id"] == "1"
        assert score1 > 0.5

    def test_get_index_stats_not_initialized(self, manager):
        """Test getting stats when index is not initialized."""
        stats = manager.get_index_stats()

        expected = {
            "status": "not_initialized",
            "total_entities": 0,
            "dimension": None,
            "index_type": "flat",
            "cache_size": 0,
        }
        assert stats == expected

    def test_get_index_stats_ready(self, manager):
        """Test getting stats when index is ready."""
        # Setup mock index
        mock_index = Mock()
        mock_index.ntotal = 100
        manager.index = mock_index
        manager.dimension = 384
        manager.embedding_cache = {
            "key1": np.array([1, 2, 3]),
            "key2": np.array([4, 5, 6]),
        }

        stats = manager.get_index_stats()

        expected = {
            "status": "ready",
            "total_entities": 100,
            "dimension": 384,
            "index_type": "flat",
            "cache_size": 2,
            "model_name": "all-MiniLM-L6-v2",
        }
        assert stats == expected

    def test_clear_cache(self, manager):
        """Test clearing the cache and index."""
        # Setup some data
        manager.embedding_cache = {"key": np.array([1, 2, 3])}
        manager.entity_metadata = {0: {"entity": "test"}}
        manager.index = Mock()

        # Clear cache
        manager.clear_cache()

        assert len(manager.embedding_cache) == 0
        assert len(manager.entity_metadata) == 0
        assert manager.index is None

    @patch("faiss.write_index")
    @patch("builtins.open")
    @patch("json.dump")
    @patch("joblib.dump")
    def test_save_index(
        self, mock_joblib_dump, mock_json_dump, mock_open, mock_faiss_write, manager
    ):
        """Test saving index to file."""
        manager.index = Mock()
        manager.entity_metadata = {0: {"test": "data"}}
        manager.embedding_cache = {"key": np.array([1, 2, 3])}
        manager.dimension = 384

        filepath = "/tmp/test_index"
        manager.save_index(filepath)

        # Verify FAISS index is saved
        mock_faiss_write.assert_called_once_with(manager.index, f"{filepath}.faiss")

        # Verify JSON metadata is saved
        mock_open.assert_called_with(f"{filepath}.metadata.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

        # Verify cache is saved with joblib
        mock_joblib_dump.assert_called_once_with(
            manager.embedding_cache, f"{filepath}.cache.joblib"
        )

    def test_save_index_no_index(self, manager):
        """Test saving when no index exists."""
        with pytest.raises(ValueError, match="No index to save"):
            manager.save_index("/tmp/test")

    @patch("faiss.read_index")
    @patch("builtins.open")
    @patch("json.load")
    @patch("joblib.load")
    def test_load_index(
        self, mock_joblib_load, mock_json_load, mock_open, mock_faiss_read, manager
    ):
        """Test loading index from file."""
        # Mock loaded data
        mock_index = Mock()
        mock_faiss_read.return_value = mock_index

        mock_json_data = {
            "entity_metadata": {0: {"test": "data"}},
            "dimension": 384,
            "model_name": "test-model",
            "index_type": "flat",
        }
        mock_json_load.return_value = mock_json_data

        mock_cache_data = {"key": np.array([1, 2, 3])}
        mock_joblib_load.return_value = mock_cache_data

        filepath = "/tmp/test_index"
        manager.load_index(filepath)

        # Verify loading
        mock_faiss_read.assert_called_once_with(f"{filepath}.faiss")
        mock_open.assert_called_with(f"{filepath}.metadata.json", "r", encoding="utf-8")
        mock_joblib_load.assert_called_once_with(f"{filepath}.cache.joblib")

        # Verify data is loaded
        assert manager.index == mock_index
        assert manager.entity_metadata == mock_json_data["entity_metadata"]
        assert manager.embedding_cache == mock_cache_data
        assert manager.dimension == 384
        assert manager.model_name == "test-model"

    @patch("faiss.read_index")
    @patch("builtins.open")
    @patch("json.load")
    @patch("joblib.load")
    def test_load_index_no_cache_file(
        self, mock_joblib_load, mock_json_load, mock_open, mock_faiss_read, manager
    ):
        """Test loading index when cache file doesn't exist."""
        # Mock loaded data
        mock_index = Mock()
        mock_faiss_read.return_value = mock_index

        mock_json_data = {
            "entity_metadata": {0: {"test": "data"}},
            "dimension": 384,
            "model_name": "test-model",
            "index_type": "flat",
        }
        mock_json_load.return_value = mock_json_data

        # Mock cache file not found
        mock_joblib_load.side_effect = FileNotFoundError("Cache file not found")

        filepath = "/tmp/test_index"
        manager.load_index(filepath)

        # Verify data is loaded without cache
        assert manager.index == mock_index
        assert manager.entity_metadata == mock_json_data["entity_metadata"]
        assert manager.embedding_cache == {}  # Should be empty dict
        assert manager.dimension == 384
        assert manager.model_name == "test-model"

    @patch("faiss.read_index")
    def test_load_index_file_error(self, mock_faiss_read, manager):
        """Test loading index when file doesn't exist."""
        mock_faiss_read.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            manager.load_index("/tmp/nonexistent")
