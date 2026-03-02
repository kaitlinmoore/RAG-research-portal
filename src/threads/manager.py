"""Research thread persistence.

Threads are saved as JSON files in outputs/threads/.
Each thread captures a query, its answer, retrieved chunks, and metadata.
"""

import json
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ThreadManager:
    """Save, load, list, and delete research threads."""

    def __init__(self, threads_dir: str | Path = "outputs/threads"):
        self.threads_dir = Path(threads_dir)
        self.threads_dir.mkdir(parents=True, exist_ok=True)

    def _generate_id(self) -> str:
        """Generate a thread ID: thr_{YYYYMMDD}_{HHMMSS}_{random6}."""
        now = datetime.now(timezone.utc)
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"thr_{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}_{suffix}"

    def save(self, thread: dict) -> str:
        """Save thread to disk. Generates thread_id if not present.

        Returns the thread_id.
        """
        if "thread_id" not in thread or not thread["thread_id"]:
            thread["thread_id"] = self._generate_id()
        if "created_at" not in thread:
            thread["created_at"] = datetime.now(timezone.utc).isoformat()
        if "artifacts" not in thread:
            thread["artifacts"] = {}

        path = self.threads_dir / f"{thread['thread_id']}.json"
        path.write_text(
            json.dumps(thread, default=str, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return thread["thread_id"]

    def load(self, thread_id: str) -> Optional[dict]:
        """Load a thread by ID. Returns None if not found."""
        path = self.threads_dir / f"{thread_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def list_threads(self) -> list[dict]:
        """Return summaries of all saved threads, newest first.

        Each summary has: thread_id, query, created_at, has_artifacts.
        """
        summaries = []
        for path in self.threads_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                summaries.append(
                    {
                        "thread_id": data.get("thread_id", path.stem),
                        "query": data.get("query", ""),
                        "created_at": data.get("created_at", ""),
                        "has_artifacts": bool(data.get("artifacts")),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        summaries.sort(key=lambda s: s["created_at"], reverse=True)
        return summaries

    def delete(self, thread_id: str) -> bool:
        """Delete a thread by ID. Returns True if deleted."""
        path = self.threads_dir / f"{thread_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False
