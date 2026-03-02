"""Response cache for offline/demo mode.

Provides transparent caching of LLM-generated content (query answers, artifacts).
Cache files are human-readable JSON stored in data/cache/.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class CacheManager:
    """Manages two cache levels: query results and artifact outputs."""

    def __init__(self, cache_dir: str | Path = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.query_dir = self.cache_dir / "queries"
        self.artifact_dir = self.cache_dir / "artifacts"
        self.query_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def get_query(self, cache_key: str) -> Optional[dict]:
        """Return cached query result or None."""
        path = self.query_dir / f"{cache_key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def put_query(self, cache_key: str, result: dict) -> None:
        """Save query result to cache."""
        result["cache_key"] = cache_key
        result["cached_at"] = datetime.now(timezone.utc).isoformat()
        path = self.query_dir / f"{cache_key}.json"
        path.write_text(
            json.dumps(result, default=str, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_artifact(self, cache_key: str) -> Optional[dict]:
        """Return cached artifact or None."""
        path = self.artifact_dir / f"{cache_key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def put_artifact(self, cache_key: str, artifact: dict) -> None:
        """Save artifact to cache."""
        artifact["cache_key"] = cache_key
        artifact["cached_at"] = datetime.now(timezone.utc).isoformat()
        path = self.artifact_dir / f"{cache_key}.json"
        path.write_text(
            json.dumps(artifact, default=str, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def list_cached_queries(self) -> list[str]:
        """Return list of cached query keys."""
        return [p.stem for p in self.query_dir.glob("*.json")]

    @staticmethod
    def make_query_key(query: str, use_reranker: bool, where: Optional[dict] = None) -> str:
        """Deterministic hash from query parameters."""
        payload = json.dumps(
            {
                "query": query.strip().lower(),
                "reranker": use_reranker,
                "filters": where or {},
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    @staticmethod
    def make_artifact_key(thread_id: str, artifact_type: str) -> str:
        """Deterministic hash from thread + artifact type."""
        payload = json.dumps(
            {"thread_id": thread_id, "artifact_type": artifact_type},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
