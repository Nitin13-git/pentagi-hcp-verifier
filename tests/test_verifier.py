from unittest.mock import MagicMock

from pentagi_hcp_verifier.client import FlowStatus
from pentagi_hcp_verifier.verifier import PentagiVerifier


def _client(status: str, evidence: list[str]) -> MagicMock:
    client = MagicMock()
    client.flow_status.return_value = FlowStatus(id="42", status=status)
    client.raw_evidence.return_value = evidence
    return client


def test_passes_when_finished_with_evidence() -> None:
    verifier = PentagiVerifier(_client("finished", ["nmap scan output"]))
    report = verifier.run("42")
    assert report.passed is True
    assert "finished" in report.evidence
    assert "nmap scan output" in report.evidence


def test_fails_when_not_finished() -> None:
    verifier = PentagiVerifier(_client("running", ["nmap scan output"]))
    report = verifier.run("42")
    assert report.passed is False


def test_fails_when_finished_but_no_evidence() -> None:
    """Catches exactly the case PentAGI's own README doesn't guard against:
    a flow marked finished with no underlying tool-execution record —
    i.e. a claim with nothing behind it.
    """
    verifier = PentagiVerifier(_client("finished", []))
    report = verifier.run("42")
    assert report.passed is False


def test_min_evidence_entries_is_configurable() -> None:
    verifier = PentagiVerifier(_client("finished", ["one entry"]), min_evidence_entries=2)
    report = verifier.run("42")
    assert report.passed is False
