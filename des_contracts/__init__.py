"""des-contracts — shared contracts for the Digital Earth Sweden agentic workflow.

Re-exports the most commonly used symbols at the top level so consumers can write:

    from des_contracts import UNIFIED_CLASSES, Analyzer, EMBEDDING_CONFIG

without having to remember the submodule layout.

Submodules:
    schema    — 23-class unified LULC (NMD + LPIS + SKS)
    analyzer  — Analyzer protocol + result types
    kg        — JSON Schema for swedish-space-ecosystem KG exports
    rag       — canonical embedding + chunking config
    registry  — analyzer registry format
"""
from __future__ import annotations

__version__ = "0.1.0"

# Top-level re-exports. Keep this list short — each import is a small contract
# that consuming code will lean on. Breaking any of them requires a major bump.
from des_contracts.schema import (
    SCHEMA_VERSION,
    UNIFIED_CLASSES,
    SJV_TO_UNIFIED,
    NMD_TO_UNIFIED,
    class_name,
)
from des_contracts.analyzer import (
    Analyzer,
    AnalyzerInput,
    AnalyzerResult,
    AnalyzerStatus,
)
from des_contracts.rag import EMBEDDING_CONFIG, EmbeddingConfig

__all__ = [
    "__version__",
    # schema
    "SCHEMA_VERSION",
    "UNIFIED_CLASSES",
    "SJV_TO_UNIFIED",
    "NMD_TO_UNIFIED",
    "class_name",
    # analyzer
    "Analyzer",
    "AnalyzerInput",
    "AnalyzerResult",
    "AnalyzerStatus",
    # rag
    "EMBEDDING_CONFIG",
    "EmbeddingConfig",
]
