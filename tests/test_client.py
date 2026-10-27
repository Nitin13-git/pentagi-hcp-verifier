"""Tests against a mocked GraphQL endpoint — no live PentAGI instance used
or required. Response shapes match PentAGI's real schema.graphqls as read
from github.com/vxcontrol/pentagi/blob/main/backend/pkg/graph/schema.graphqls
at the time this was written; they have not been checked against a running
PentAGI server.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from pentagi_hcp_verifier.client import PentagiClient


def _mock_response(data: dict):
    response = MagicMock()
    response.read.return_value = json.dumps({"data": data}).encode()
    response.__enter__.return_value = response
    return response


def test_flow_status_parses_real_schema_shape() -> None:
    client = PentagiClient("https://example.test/graphql")
    with patch("urllib.request.urlopen", return_value=_mock_response({"flow": {"id": "42", "status": "finished"}})):
        status = client.flow_status("42")
    assert status.id == "42"
    assert status.status == "finished"


def test_raw_evidence_combines_terminal_and_search_logs() -> None:
    client = PentagiClient("https://example.test/graphql")
    data = {
        "terminalLogs": [{"text": "nmap -p 80,443 10.0.0.5"}],
        "searchLogs": [{"query": "CVE-2024-xxxx", "result": "no match"}],
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(data)):
        evidence = client.raw_evidence("42")
    assert evidence == ["nmap -p 80,443 10.0.0.5", "search: CVE-2024-xxxx -> no match"]


def test_raw_evidence_handles_empty_logs() -> None:
    client = PentagiClient("https://example.test/graphql")
    with patch("urllib.request.urlopen", return_value=_mock_response({"terminalLogs": [], "searchLogs": []})):
        evidence = client.raw_evidence("42")
    assert evidence == []


def test_graphql_errors_raise() -> None:
    client = PentagiClient("https://example.test/graphql")
    response = MagicMock()
    response.read.return_value = json.dumps({"errors": [{"message": "flow not found"}]}).encode()
    response.__enter__.return_value = response
    with patch("urllib.request.urlopen", return_value=response):
        try:
            client.flow_status("missing")
            assert False, "expected RuntimeError"
        except RuntimeError as exc:
            assert "flow not found" in str(exc)
