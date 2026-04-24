"""Canonical RAG (embedding + chunking) configuration.

Per rollout plan Wave 3.5 + the des subsystem report's "HIGHEST LEVERAGE"
finding — des-agent and des-chatbot were using different embedding models
(768-dim nomic vs. 384-dim MiniLM), making their Qdrant collections
uncross-queryable.

This module publishes the ONE canonical choice. Both consumers pin to
des-contracts >= <current major>, import `EMBEDDING_CONFIG`, and align.

Updating the embedding model here requires:
  1. Re-indexing every Qdrant collection.
  2. Major version bump of des-contracts (breaking change).
  3. Coordinated rollout across all consumers.

The versioning below is strict — a mismatch means consumers will detect
it at startup and refuse to load incompatible Qdrant collections.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    """Immutable snapshot of the canonical embedding configuration.

    All fields contribute to `.identity`, which is the short string
    consumers stamp into their Qdrant collection metadata so mismatches
    are detectable.
    """

    model: str                # Ollama tag
    dimensions: int           # output vector dim
    version: str              # YYYY-MM revision of THIS config
    chunk_size: int           # default chunk size in characters
    chunk_overlap: int        # default chunk overlap in characters

    @property
    def identity(self) -> str:
        """Stable identity string; stamp this into Qdrant collection metadata.

        Example: "nomic-embed-text:v1.5@2026-04|768|cs512|co64"
        """
        return (
            f"{self.model}@{self.version}"
            f"|{self.dimensions}"
            f"|cs{self.chunk_size}"
            f"|co{self.chunk_overlap}"
        )


# Canonical choice as of 2026-04. Rationale:
#   - Kept nomic-embed-text:v1.5 because des-agent's Qdrant collections
#     are already at 768-dim — flipping to a 384-dim model would force a
#     reindex with no qualitative win.
#   - des-chatbot migrates TO this (currently uses all-MiniLM-L6-v2 at
#     384-dim). Reindex is required; see docs/migration-2026-04.md in
#     des-chatbot for the plan.
#   - Chunk size 512 chars + overlap 64 matches des-agent's existing
#     config/chunking.yaml. des-chatbot was using implicit per-page
#     chunks; it migrates to this too.
EMBEDDING_CONFIG = EmbeddingConfig(
    model="nomic-embed-text:v1.5",
    dimensions=768,
    version="2026-04",
    chunk_size=512,
    chunk_overlap=64,
)


__all__ = [
    "EmbeddingConfig",
    "EMBEDDING_CONFIG",
]
