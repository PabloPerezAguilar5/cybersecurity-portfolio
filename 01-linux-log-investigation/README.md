# 01 | Linux Security Log Investigation

**Status:** Completed for the documented learning scope. Two reviewed cases; neither establishes a real security incident.

[← Portfolio overview](../README.md) · [Report template](report-template.md)

## Objective

Investigate events in a real Linux workstation journal, reconstruct a short timeline, distinguish observations from assumptions, and make a defensible triage decision.

**Environment:** Personal Ubuntu 24.04 LTS workstation. **Tools:** `systemd-journald`, `journalctl`, package metadata queries, sanitized evidence and written incident reports.

## Investigations and findings

| Case | Question | Evidence-backed outcome |
| --- | --- | --- |
| [LAB-01-001 — Privileged execution](analysis-report.md) | Why was `pkexec` used to run an `update-notifier` helper? | A journal timeline and package metadata support a **probably legitimate** update-related explanation. The classification remains **provisional**; request origin, authorization and file integrity were not established. |
| [LAB-01-002 — Authentication failure](LAB-01-002-analysis-report.md) | What do the `su` and PAM messages demonstrate? | The journal records an authentication failure and `FAILED SU` for the same process. The author reports an intentional incorrect-password test; no hostile activity was established. |

**What this demonstrates:** scoped evidence collection, log interpretation, timeline reconstruction, assessment of benign explanations, clear escalation reasoning, and explicit documentation of limitations.

## How I approached the cases

1. Establish a read-only baseline for the boot and the journal.
2. Select a narrow investigative question and time window.
3. Review relevant events and neighboring context.
4. Preserve **sanitized** evidence and separate observed facts from hypotheses.
5. Write a report with findings, limitations, and a reasoned triage decision.

The complete methodology, timelines and evidence references are in the linked reports, not compressed into this overview.

## Safe, read-only starting commands

```bash
date -Is
journalctl --list-boots --no-pager
journalctl --disk-usage
journalctl -b -n 30 --no-pager
journalctl -b -p warning -n 30 --no-pager
```

These commands query local information; they do not change system configuration. System logs can contain private hostnames, usernames, and addresses, so inspect them before copying or committing anything.

## Evidence and limits

- [Sanitized update-related journal excerpt](evidence/sanitized-log-excerpts.txt)
- [Sanitized authentication-failure excerpt](evidence/LAB-01-002-sanitized-log-excerpts.txt)
- [Full privileged-execution report](analysis-report.md)
- [Full controlled-failure report](LAB-01-002-analysis-report.md)

No compromise was confirmed; the first assessment is intentionally provisional. AI assisted with queries, analysis, and drafting; the author reviewed and documented the laboratory work.
