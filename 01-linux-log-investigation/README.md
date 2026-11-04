# 01 | Linux Security Log Investigation

**Status:** Planned / in progress. No findings claimed yet.

## Scenario

You are a SOC L1 analyst reviewing a Linux workstation. Your assignment is to distinguish routine system activity from events that warrant additional investigation.

## Objective

- Learn how `systemd-journald` records events and how `journalctl` queries them.
- Identify timestamps, sources, severity and relevant context.
- Produce a timeline and a short triage report based on **observed** facts.
- Explain at least one benign event and one potentially relevant event (if present). Do not invent suspicious activity.

## Environment

Ubuntu 24.04 LTS on an HP laptop. No additional VM or heavy SIEM is required.

## Investigation workflow

1. **Baseline (read-only)**: record date/time, current boot, journal disk usage, and recent events.
2. **Scope**: select a narrow question, such as authentication failures or service errors.
3. **Collect**: capture only relevant excerpts; do not commit unredacted host logs.
4. **Analyze**: explain what each event actually establishes, and what it does not.
5. **Report**: use [the report template](report-template.md) and add redacted evidence to an `evidence/` directory when available.

### Safe commands to discuss and run deliberately

```bash
date -Is
journalctl --list-boots --no-pager
journalctl --disk-usage
journalctl -b -n 30 --no-pager
journalctl -b -p warning -n 30 --no-pager
```

These commands query system information and journal data. They do not modify configuration. Logs may contain hostnames, usernames, IP addresses and other sensitive details: inspect and redact before sharing or committing.

## Acceptance criteria

- [ ] One clear investigation question and rationale.
- [ ] Evidence from the host, annotated and sanitized.
- [ ] A timeline or event summary with timestamps and sources.
- [ ] Severity/triage assessment that distinguishes observed facts and assumptions.
- [ ] Completed report reviewed by the author.
- [ ] Reproducible procedure and explicit limitations.

Do not mark this project complete before the investigation and report actually exist.
