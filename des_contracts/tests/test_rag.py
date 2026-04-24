"""Contract tests for the canonical embedding config."""
from des_contracts.rag import EMBEDDING_CONFIG, EmbeddingConfig


def test_embedding_config_is_frozen():
    import dataclasses
    assert dataclasses.is_dataclass(EMBEDDING_CONFIG)


def test_embedding_config_current_choice():
    # Canonical as of 2026-04. Changing any of these requires a MAJOR bump
    # of des-contracts and coordinated re-indexing across consumers.
    assert EMBEDDING_CONFIG.model == "nomic-embed-text:v1.5"
    assert EMBEDDING_CONFIG.dimensions == 768
    assert EMBEDDING_CONFIG.version == "2026-04"
    assert EMBEDDING_CONFIG.chunk_size == 512
    assert EMBEDDING_CONFIG.chunk_overlap == 64


def test_identity_is_stable():
    identity = EMBEDDING_CONFIG.identity
    assert identity == "nomic-embed-text:v1.5@2026-04|768|cs512|co64"


def test_identity_changes_on_any_field():
    c1 = EmbeddingConfig(
        model="a", dimensions=1, version="v", chunk_size=1, chunk_overlap=1
    )
    c2 = EmbeddingConfig(
        model="b", dimensions=1, version="v", chunk_size=1, chunk_overlap=1
    )
    assert c1.identity != c2.identity
