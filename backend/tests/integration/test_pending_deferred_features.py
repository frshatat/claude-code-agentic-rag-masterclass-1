from __future__ import annotations

import pytest


@pytest.mark.xfail(reason="Pending scope: realtime ingestion status is not wired yet", strict=False)
def test_realtime_ingestion_status_stream_pending() -> None:
    pytest.xfail("Deferred to future implementation")


@pytest.mark.xfail(reason="Pending scope: retrieval tool calling is deferred to Phase 8", strict=False)
def test_retrieval_tool_calling_pending() -> None:
    pytest.xfail("Deferred to future implementation")
