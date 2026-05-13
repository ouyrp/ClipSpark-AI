import hashlib
import math

from app.services.intelligence.viral_samples import VIRAL_SAMPLES


def embed_text(text: str, dimensions: int = 48) -> list[float]:
    vector = [0.0] * dimensions
    tokens = [token for token in text.lower().replace("/", " ").replace("_", " ").split() if token]
    if not tokens:
        tokens = [text.lower()[:32] or "empty"]
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % dimensions
        sign = 1 if digest[2] % 2 == 0 else -1
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def style_matches(query: str, limit: int = 3) -> list[dict]:
    query_vector = embed_text(query)
    scored = []
    for sample in VIRAL_SAMPLES:
        sample_text = " ".join(
            [
                sample["industry"],
                sample["tone"],
                sample["hook_pattern"],
                sample["pace"],
                sample["caption_style"],
                " ".join(sample["structure"]),
            ]
        )
        scored.append(
            {
                "sample_id": sample["id"],
                "score": round(cosine_similarity(query_vector, embed_text(sample_text)), 4),
                "industry": sample["industry"],
                "tone": sample["tone"],
                "hook_pattern": sample["hook_pattern"],
            }
        )
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]
