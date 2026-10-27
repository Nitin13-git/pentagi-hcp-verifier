"""Minimal, zero-dependency GraphQL client for PentAGI's public API.

PentAGI (https://github.com/vxcontrol/pentagi) exposes a GraphQL API
(schema at backend/pkg/graph/schema.graphqls) with a `flow(flowId)` query
returning a Flow's status, and `terminalLogs`/`searchLogs` queries
returning raw tool-execution records for that flow. This client only
reads those two things — it does not modify PentAGI or require any change
to PentAGI's own codebase.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class FlowStatus:
    id: str
    status: str  # one of: created, running, waiting, finished, failed


class PentagiClient:
    def __init__(self, endpoint: str, *, auth_cookie: str | None = None, timeout_s: float = 30.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._auth_cookie = auth_cookie
        self._timeout_s = timeout_s

    def _query(self, query: str, variables: dict) -> dict:
        body = json.dumps({"query": query, "variables": variables}).encode()
        headers = {"Content-Type": "application/json"}
        if self._auth_cookie:
            headers["Cookie"] = self._auth_cookie
        request = urllib.request.Request(self._endpoint, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
            payload = json.loads(response.read())
        if "errors" in payload:
            raise RuntimeError(f"PentAGI GraphQL error: {payload['errors']}")
        return payload["data"]

    def flow_status(self, flow_id: str) -> FlowStatus:
        data = self._query(
            "query($id: ID!) { flow(flowId: $id) { id status } }",
            {"id": flow_id},
        )
        flow = data["flow"]
        return FlowStatus(id=flow["id"], status=flow["status"])

    def raw_evidence(self, flow_id: str) -> list[str]:
        """Terminal and search logs: records of actual tool execution, not
        the agent's own synthesized summary of what it did.
        """
        data = self._query(
            """
            query($id: ID!) {
              terminalLogs(flowId: $id) { text }
              searchLogs(flowId: $id) { query result }
            }
            """,
            {"id": flow_id},
        )
        evidence = [entry["text"] for entry in data.get("terminalLogs", []) or []]
        evidence += [
            f"search: {entry['query']} -> {entry['result']}"
            for entry in data.get("searchLogs", []) or []
        ]
        return evidence
