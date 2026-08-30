"""Small, local, snapshot based retrieval augmented generation index."""

from cfdc.knowledge import (
    KnowledgeArtifact,
    KnowledgeContext,
    RetrievalRequest,
    RuleDecision,
)

from .core import (
    CHUNK_OVERLAP_TOKENS,
    DEFAULT_EMBEDDING_MODEL,
    MAX_CHUNK_TOKENS,
    MAX_RESULTS,
    RAG_SCHEMA_VERSION,
    RAGIndex,
    SearchResult,
    SentenceTransformerEncoder,
    build_index,
    calibrate_relevance_threshold,
    evaluate_retrieval,
    load_index,
)

__all__ = [
    "CHUNK_OVERLAP_TOKENS",
    "DEFAULT_EMBEDDING_MODEL",
    "MAX_CHUNK_TOKENS",
    "MAX_RESULTS",
    "RAG_SCHEMA_VERSION",
    "KnowledgeArtifact",
    "KnowledgeContext",
    "RAGIndex",
    "RetrievalRequest",
    "RuleDecision",
    "SearchResult",
    "SentenceTransformerEncoder",
    "build_index",
    "calibrate_relevance_threshold",
    "evaluate_retrieval",
    "load_index",
]
