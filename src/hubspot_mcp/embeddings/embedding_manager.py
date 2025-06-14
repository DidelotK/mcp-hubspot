"""Embedding manager for semantic search operations."""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import faiss
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embeddings and FAISS index for semantic search operations.

    This class provides functionality to:
    - Generate embeddings from HubSpot entity data
    - Build and maintain FAISS indexes
    - Perform similarity searches
    - Cache embeddings for performance
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_type: str = "flat"):
        """Initialize the embedding manager.

        Args:
            model_name: Name of the sentence transformer model to use
            index_type: Type of FAISS index ("flat" or "ivf")
        """
        self.model_name = model_name
        self.index_type = index_type
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.entity_metadata: Dict[int, Dict[str, Any]] = {}
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.dimension: Optional[int] = None

    def _initialize_model(self) -> None:
        """Initialize the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)

    def _get_entity_text(self, entity: Dict[str, Any], entity_type: str) -> str:
        """Extract searchable text from HubSpot entity.

        Args:
            entity: HubSpot entity data
            entity_type: Type of entity (contacts, companies, deals, etc.)

        Returns:
            str: Concatenated text representation of the entity
        """
        props = entity.get("properties", {})

        if entity_type == "contacts":
            parts = [
                props.get("firstname", ""),
                props.get("lastname", ""),
                props.get("email", ""),
                props.get("jobtitle", ""),
                props.get("company", ""),
                props.get("phone", ""),
            ]
        elif entity_type == "companies":
            parts = [
                props.get("name", ""),
                props.get("domain", ""),
                props.get("industry", ""),
                props.get("description", ""),
                props.get("city", ""),
                props.get("country", ""),
            ]
        elif entity_type == "deals":
            parts = [
                props.get("dealname", ""),
                props.get("dealstage", ""),
                props.get("pipeline", ""),
                props.get("closedate", ""),
                props.get("amount", ""),
            ]
        elif entity_type == "engagements":
            parts = [
                props.get("hs_engagement_type", ""),
                props.get("hs_engagement_source", ""),
                props.get("hs_body_preview", ""),
                props.get("hs_engagement_subject", ""),
            ]
        else:
            # Generic approach for other entity types
            parts = [str(v) for v in props.values() if v is not None]

        # Filter out empty strings and join
        text_parts = [part.strip() for part in parts if part and part.strip()]
        return " ".join(text_parts)

    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for embedding text.

        Args:
            text: Text to generate key for

        Returns:
            str: SHA-256 hash of the text
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def generate_embeddings(
        self, entities: List[Dict[str, Any]], entity_type: str
    ) -> np.ndarray:
        """Generate embeddings for a list of entities.

        Args:
            entities: List of HubSpot entities
            entity_type: Type of entities (contacts, companies, deals, etc.)

        Returns:
            np.ndarray: Array of embeddings
        """
        self._initialize_model()

        texts = []
        embeddings = []

        for entity in entities:
            text = self._get_entity_text(entity, entity_type)
            if not text.strip():
                # Skip empty entities
                continue

            cache_key = self._generate_cache_key(text)

            if cache_key in self.embedding_cache:
                # Use cached embedding
                embeddings.append(self.embedding_cache[cache_key])
            else:
                texts.append(text)

        # Generate embeddings for new texts
        if texts:
            logger.info(f"Generating embeddings for {len(texts)} new {entity_type}")
            if self.model is None:
                raise RuntimeError("Model not initialized")
            new_embeddings = self.model.encode(texts, convert_to_numpy=True)

            # Cache new embeddings
            for i, text in enumerate(texts):
                cache_key = self._generate_cache_key(text)
                self.embedding_cache[cache_key] = new_embeddings[i]
                embeddings.append(new_embeddings[i])

        if not embeddings:
            if self.model is None:
                raise RuntimeError("Model not initialized")
            return np.empty((0, self.model.get_sentence_embedding_dimension()))

        return np.vstack(embeddings)

    def build_index(self, entities: List[Dict[str, Any]], entity_type: str) -> None:
        """Build FAISS index from entities.

        Args:
            entities: List of HubSpot entities
            entity_type: Type of entities
        """
        if not entities:
            logger.warning(f"No entities provided for {entity_type} index")
            return

        # Generate embeddings
        embeddings = self.generate_embeddings(entities, entity_type)

        if embeddings.shape[0] == 0:
            logger.warning(f"No valid embeddings generated for {entity_type}")
            return

        # Initialize dimension
        self.dimension = embeddings.shape[1]

        # Create FAISS index
        if self.index_type == "flat":
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # IVF index for larger datasets
            nlist = min(100, max(1, len(entities) // 10))
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(embeddings)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

        # Add embeddings to index
        self.index.add(embeddings)

        # Store metadata
        valid_entities = [
            entity
            for entity in entities
            if self._get_entity_text(entity, entity_type).strip()
        ]

        for i, entity in enumerate(valid_entities):
            self.entity_metadata[i] = {
                "entity": entity,
                "entity_type": entity_type,
                "text": self._get_entity_text(entity, entity_type),
            }

        logger.info(
            f"Built {self.index_type} index with {self.index.ntotal} embeddings "
            f"for {entity_type}"
        )

    def search_similar(
        self, query: str, k: int = 5, threshold: float = 0.8
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar entities using semantic similarity.

        Args:
            query: Search query text
            k: Number of results to return
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of tuples containing (entity, similarity_score)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No index available for search")
            return []

        self._initialize_model()

        # Generate query embedding
        if self.model is None:
            raise RuntimeError("Model not initialized")
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # No more results
                break

            # Convert L2 distance to similarity score (0-1)
            similarity = 1.0 / (1.0 + distance)

            if similarity >= threshold:
                metadata = self.entity_metadata.get(idx)
                if metadata:
                    results.append((metadata["entity"], similarity))

        return results

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index.

        Returns:
            Dict containing index statistics
        """
        if self.index is None:
            return {
                "status": "not_initialized",
                "total_entities": 0,
                "dimension": None,
                "index_type": self.index_type,
                "cache_size": len(self.embedding_cache),
            }

        return {
            "status": "ready",
            "total_entities": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "cache_size": len(self.embedding_cache),
            "model_name": self.model_name,
        }

    def clear_cache(self) -> None:
        """Clear embedding cache and reset index."""
        self.embedding_cache.clear()
        self.entity_metadata.clear()
        self.index = None
        logger.info("Embedding cache and index cleared")

    def save_index(self, filepath: str) -> None:
        """Save FAISS index and metadata to file.

        Args:
            filepath: Path to save the index
        """
        if self.index is None:
            raise ValueError("No index to save")

        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.faiss")

        # Save JSON-serializable metadata
        metadata = {
            "entity_metadata": self.entity_metadata,
            "dimension": self.dimension,
            "model_name": self.model_name,
            "index_type": self.index_type,
        }
        with open(f"{filepath}.metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Save embedding cache using joblib (safer for numpy arrays)
        if self.embedding_cache:
            joblib.dump(self.embedding_cache, f"{filepath}.cache.joblib")

        logger.info(f"Index saved to {filepath}")

    def load_index(self, filepath: str) -> None:
        """Load FAISS index and metadata from file.

        Args:
            filepath: Path to load the index from
        """
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{filepath}.faiss")

            # Load JSON metadata
            with open(f"{filepath}.metadata.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entity_metadata = data["entity_metadata"]
                self.dimension = data["dimension"]
                self.model_name = data["model_name"]
                self.index_type = data["index_type"]

            # Load embedding cache if it exists
            cache_file = f"{filepath}.cache.joblib"
            try:
                self.embedding_cache = joblib.load(cache_file)
            except FileNotFoundError:
                # Cache file doesn't exist, start with empty cache
                self.embedding_cache = {}
                logger.info("No cache file found, starting with empty embedding cache")

            logger.info(f"Index loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load index from {filepath}: {e}")
            raise
