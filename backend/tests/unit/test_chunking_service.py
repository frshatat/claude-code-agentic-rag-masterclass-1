from __future__ import annotations

import pytest

from app.services.chunking_service import chunk_text


def test_chunk_text_empty_returns_empty_list() -> None:
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_validates_parameters() -> None:
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        chunk_text("hello", chunk_size=0)

    with pytest.raises(ValueError, match="chunk_overlap must be non-negative"):
        chunk_text("hello", chunk_overlap=-1)

    with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
        chunk_text("hello", chunk_size=10, chunk_overlap=10)


def test_chunk_text_uses_overlap_and_sequence() -> None:
    chunks = chunk_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, chunk_overlap=3)

    assert [c["sequence"] for c in chunks] == [0, 1, 2, 3]
    assert chunks[0]["raw_text"] == "abcdefghij"
    assert chunks[1]["raw_text"].startswith("hij")
    assert all(c["char_count"] == len(c["raw_text"]) for c in chunks)
