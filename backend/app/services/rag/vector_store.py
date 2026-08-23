import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import VECTORSTORE_DIR

class SemanticVectorStore:
    """
    Self-contained semantic vector store for Agricultural Extension Bulletins.
    Computes TF-IDF / semantic cosine similarity over advisory chunks with metadata filtering.
    """
    def __init__(self, storage_dir: Path = VECTORSTORE_DIR):
        self.storage_file = storage_dir / "advisory_vectors.json"
        self.chunks: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.load()

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        self.chunks.extend(new_chunks)
        self._rebuild_index()
        self.save()

    def search(self, query: str, crop_filter: Optional[str] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        query_vec = self._vectorize(query_tokens)
        results = []

        for chunk in self.chunks:
            # Metadata filtering
            if crop_filter and crop_filter.lower() != "general":
                chunk_crop = (chunk.get("crop") or "").lower()
                if chunk_crop != "general" and chunk_crop != crop_filter.lower():
                    continue

            chunk_tokens = self._tokenize(chunk["content"])
            chunk_vec = self._vectorize(chunk_tokens)
            sim = self._cosine_similarity(query_vec, chunk_vec)
            
            # Boost score if specific disease/crop keywords match
            if crop_filter and crop_filter.lower() in chunk["content"].lower():
                sim += 0.15

            if sim > 0.05:
                res_item = dict(chunk)
                res_item["relevance_score"] = min(0.98, round(float(sim), 3))
                results.append(res_item)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stopwords = {
            "the", "and", "for", "with", "that", "this", "from", "are", "have", "has", "was",
            "were", "will", "been", "plant", "crops", "field", "also", "should", "used", "can"
        }
        return [w for w in words if w not in stopwords]

    def _rebuild_index(self):
        doc_count = len(self.chunks)
        if doc_count == 0:
            return

        doc_freq: Dict[str, int] = {}
        for chunk in self.chunks:
            tokens = set(self._tokenize(chunk["content"]))
            for t in tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1

        self.idf = {
            term: math.log((doc_count + 1) / (freq + 1)) + 1.0
            for term, freq in doc_freq.items()
        }

    def _vectorize(self, tokens: List[str]) -> Dict[str, float]:
        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        
        # TF-IDF weighted vector
        vec = {t: count * self.idf.get(t, 1.0) for t, count in tf.items()}
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            vec = {k: v / norm for k, v in vec.items()}
        return vec

    def _cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        return sum(vec_a[k] * vec_b[k] for k in common_keys)

    def save(self):
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump({"chunks": self.chunks}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving vector store: {e}")

    def load(self):
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    self._rebuild_index()
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.chunks = []

vector_store = SemanticVectorStore()
