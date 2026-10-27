# pentagi-hcp-verifier

An [HCP](https://github.com/Nitin13-git/hcp)-conformant `Verifier` backed by
[PentAGI](https://github.com/vxcontrol/pentagi)'s own public GraphQL API.
**Requires no changes to PentAGI** — it's a read-only client against
PentAGI's existing `flow`, `terminalLogs`, and `searchLogs` queries.

## Why

PentAGI's README documents task completion as depending on agent-reported
status plus a supervisory "Reflector" agent — there's no independent check
confirming a claimed finding is actually correct. (Full writeup: the
[PentAGI Frontier Harness Design Breakdown](https://github.com/Nitin13-git/learn-harness-security).)
This package doesn't propose PentAGI add anything — it reads what's
already there, from the outside, and checks it independently.

## What it checks, honestly

`PentagiVerifier.run(flow_id)` passes only if:
1. The flow's status is `finished` (per PentAGI's own `StatusType` enum).
2. There's at least one raw tool-execution record (`terminalLogs` or
   `searchLogs`) backing that claim — not just the agent's own synthesized
   `Task.result` summary text.

That's a real step up from trusting a self-reported summary — raw tool
logs are harder to fabricate than a narrative — but it is **not** full
re-execution verification. It doesn't replay the exploit or independently
reproduce the finding; a `finished` flow with plausible-looking but
fabricated tool logs would still pass. A stronger version would re-run the
actual check against the target. Not built here — see
[HCP's Open Problems](https://github.com/Nitin13-git/learn-harness-security)
for the general version of this gap (verification that isn't a string/log
match).

## Status: untested against a live PentAGI instance

Everything here is built and tested against PentAGI's **documented GraphQL
schema** (`backend/pkg/graph/schema.graphqls` as of this writing), with
tests run against a mocked endpoint. It has not been run against a real,
running PentAGI deployment. If the schema has since changed, or if there
are auth/session details not visible from the public schema alone, this
may need adjustment before it works against a live instance.

## Quickstart

```bash
pip install -e ".[dev]"
pytest
```

```python
from pentagi_hcp_verifier import PentagiClient, PentagiVerifier

client = PentagiClient("https://your-pentagi-instance/graphql", auth_cookie="...")
verifier = PentagiVerifier(client)

report = verifier.run(flow_id="42")
print(report.passed, report.evidence)
```

## License

MIT
