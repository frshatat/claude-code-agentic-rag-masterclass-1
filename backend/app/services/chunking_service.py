from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    """Split text into overlapping chunks suitable for embeddings."""
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be less than chunk_size")

    chunks: list[dict] = []
    start = 0
    sequence = 0
    text_length = len(cleaned)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        raw_chunk = cleaned[start:end].strip()
        if raw_chunk:
            chunks.append(
                {
                    "sequence": sequence,
                    "raw_text": raw_chunk,
                    "char_count": len(raw_chunk),
                }
            )
            sequence += 1

        if end >= text_length:
            break
        start = end - chunk_overlap

    return chunks
