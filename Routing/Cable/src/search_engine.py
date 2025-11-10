import os
import json
import yaml
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from openai_service import get_embedding  # your async wrapper
from utils import NumpyJSONEncoder  # custom encoder for np.array

class SmartSearchOrchestrator:
    """Ultra-fast search engine with minimal dependencies"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.vector_store: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            "documents_processed": 0,
            "total_chunks": 0,
            "searches_performed": 0,
            "chunk_size": self.config["search"]["chunk_size"],
        }
        self._load_vector_store()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load config file, merge with defaults"""
        default_config = {
            "search": {"chunk_size": 64, "top_k": 5, "persist_path": "data/vector_store.json"},
            "api": {"secret_key": os.environ.get("API_SECRET_KEY", "your-secret-api-key")},
        }

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            # Merge recursively
            for key, val in default_config.items():
                if key in user_config and isinstance(user_config[key], dict):
                    merged = val.copy()
                    merged.update(user_config[key])
                    user_config[key] = merged
                else:
                    user_config.setdefault(key, val)
            return user_config
        else:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f)
            return default_config

    def _load_vector_store(self):
        """Load vector store from disk"""
        path = self.config["search"]["persist_path"]
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vector_store = {
                        k: {
                            "content": v["content"],
                            "file_name": v["file_name"],
                            "embedding": np.array(v["embedding"]),
                        }
                        for k, v in data.items()
                    }
                    self.stats["total_chunks"] = len(self.vector_store)
            except (json.JSONDecodeError, KeyError):
                self.vector_store = {}

    def _save_vector_store(self):
        """Persist vector store to disk"""
        path = self.config["search"]["persist_path"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Convert np.array to list for JSON
        serializable_store = {
            k: {**v, "embedding": v["embedding"].tolist()} for k, v in self.vector_store.items()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable_store, f, cls=NumpyJSONEncoder)

    def _chunk_text(self, text: str) -> List[str]:
        chunk_size = self.config["search"]["chunk_size"]
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    async def _async_get_embedding(self, text: str) -> np.ndarray:
        """Async wrapper to get embeddings"""
        return np.array(await get_embedding(text))

    async def async_add_documents(self, file_paths: List[str]) -> Dict[str, int]:
        results = {"files_processed": 0, "chunks_created": 0, "errors": []}

        for path in file_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = self._chunk_text(content)
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{path}:{i}"
                    embedding = await self._async_get_embedding(chunk)
                    self.vector_store[chunk_id] = {
                        "content": chunk,
                        "file_name": os.path.basename(path),
                        "embedding": embedding,
                    }

                results["files_processed"] += 1
                results["chunks_created"] += len(chunks)
                self.stats["documents_processed"] += 1
                self.stats["total_chunks"] += len(chunks)

            except (IOError, OSError) as e:
                results["errors"].append(f"{path}: {e}")

        self._save_vector_store()
        return results

    async def async_search(
        self, query: str, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = self.config["search"]["top_k"]

        query_embedding = await self._async_get_embedding(query)
        results = []

        for chunk_id, chunk_data in self.vector_store.items():
            similarity = float(np.dot(query_embedding, chunk_data["embedding"]))
            results.append(
                {
                    "chunk_id": chunk_id,
                    "content": chunk_data["content"],
                    "file_name": chunk_data["file_name"],
                    "score": similarity,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        self.stats["searches_performed"] += 1
        return results[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        return self.stats

    # Optional synchronous wrappers
    def add_documents(self, file_paths: List[str]) -> Dict[str, int]:
        return asyncio.run(self.async_add_documents(file_paths))

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        return asyncio.run(self.async_search(query, top_k))
