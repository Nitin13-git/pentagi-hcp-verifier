<!-- DRAFT — NOT POSTED. For GitHub Discussions on vxcontrol/pentagi (not an
Issue — this isn't a feature request, see note below). Review before posting. -->

## Context on why this is a Discussion, not an Issue

Issue #235 (cryptographic evidence chain / signed receipts) was closed
"Not planned: no demand for signed receipts in the product." This isn't
that — no signing, no new infra, nothing added to PentAGI. It's a small
external tool that reads PentAGI's existing public GraphQL schema. Posting
as a Discussion / FYI rather than an Issue since there's nothing being
asked of the maintainers here.

## Draft post

**Title:** External, read-only independent verifier using PentAGI's existing GraphQL API

Hi — I maintain [HCP](https://github.com/Nitin13-git/hcp), a small spec
for agent-harness interfaces (state, verification, scope, lifecycle). I
read through PentAGI's README while writing a breakdown of how different
harness projects handle these four concerns, and noticed task completion
depends on agent-reported status + the Reflector agent — no independent
check confirms a finding is actually correct.

I built a small external verifier
([pentagi-hcp-verifier](https://github.com/Nitin13-git/pentagi-hcp-verifier))
that reads your existing `flow` and `terminalLogs`/`searchLogs` GraphQL
queries and checks that a `finished` flow actually has raw tool-execution
evidence behind it, not just the agent's synthesized `Task.result` text.
No changes to PentAGI needed — it's a read-only client against your
existing schema.

To be upfront about what it isn't: it doesn't re-run or independently
reproduce a finding, so a `finished` flow with fabricated-but-plausible
logs would still pass — it's a step up from trusting the summary text
alone, not full re-verification. It's also untested against a live
instance (tested against your documented schema with a mocked endpoint).

Not asking for anything to change in PentAGI — just sharing in case it's
useful, or in case I've misread how verification actually works here and
you want to set me straight. Happy to be told this already exists or
isn't needed.
