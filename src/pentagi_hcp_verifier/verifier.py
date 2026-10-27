"""An HCP-conformant Verifier backed by PentAGI's own GraphQL API.

PentAGI's README documents task completion as depending on agent-reported
status plus a supervisory "Reflector" agent — there's no independent check
confirming a claimed result is actually correct (see the breakdown this
was built from: learn-harness-security's Frontier Harness Design
Breakdowns). This Verifier doesn't require changing PentAGI at all; it
reads PentAGI's *existing* public GraphQL schema from the outside.

Honest limitation, stated plainly: this checks that PentAGI's Flow status
is "finished" AND that real tool-execution evidence exists (terminal/search
logs), not just an agent's narrative summary — but it does not re-run or
independently reproduce the finding itself. That's a real step up from
trusting the agent's synthesized `Task.result` text alone (raw tool logs
are harder to fabricate than a summary), not a full re-execution verifier.
A stronger version would replay the actual exploit and check the response —
not built here.
"""

from __future__ import annotations

from hcp.verification import VerificationReport, Verifier

from pentagi_hcp_verifier.client import PentagiClient

_PASSING_STATUS = "finished"


class PentagiVerifier(Verifier):
    def __init__(self, client: PentagiClient, *, min_evidence_entries: int = 1) -> None:
        self._client = client
        self._min_evidence_entries = min_evidence_entries

    def run(self, target: str) -> VerificationReport:
        """`target` is a PentAGI flow id."""
        import time

        start = time.monotonic()
        status = self._client.flow_status(target)
        evidence_entries = self._client.raw_evidence(target)

        passed = status.status == _PASSING_STATUS and len(evidence_entries) >= self._min_evidence_entries
        evidence_text = (
            f"flow {status.id} status={status.status}; "
            f"{len(evidence_entries)} raw tool-execution record(s)\n"
            + "\n".join(evidence_entries[:20])
        )
        duration_s = time.monotonic() - start
        return VerificationReport(passed=passed, evidence=evidence_text[:4000], duration_s=duration_s)
