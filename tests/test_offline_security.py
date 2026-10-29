import socket
import pytest
from src.engine.runner import DiscoveryEngine
from src.ingestion.parser import OEISRecord


def test_zero_network_during_discovery(monkeypatch):
    """
    Strict security and offline verification:
    Ensures that running the mathematical discovery engine NEVER attempts any socket network connection.
    """
    def forbidden_connect(*args, **kwargs):
        raise RuntimeError("CRITICAL ERROR: Discovery engine attempted external network call!")

    monkeypatch.setattr(socket.socket, "connect", forbidden_connect)

    rec = OEISRecord(
        a_number="TEST_SEC",
        id_number=999,
        name="Security test sequence",
        offset_first_term=0,
        terms=[2**n for n in range(15)],
    )

    engine = DiscoveryEngine()
    # If any network connection is attempted, it will trigger RuntimeError
    cands = engine.analyze_sequence(rec)
    assert len(cands) >= 1

