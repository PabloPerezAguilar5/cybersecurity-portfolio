# SOC Portfolio Roadmap

This is a sequence of small, individually demonstrable projects. Status reflects documented work and remaining validation, not professional experience.

| ID | Project | Status | Evidence / remaining work |
|---|---|---|---|
| 01 | [Linux Security Log Investigation](../01-linux-log-investigation/README.md) | Completed | Two reviewed cases with sanitized evidence; the privileged-execution classification remains provisional. |
| 02 | [SSH Authentication & Detection](../02-ssh-detection/README.md) | Partially completed | Controlled failures, detector, live monitor and author-confirmed Telegram receipt; successful-login baseline and Hydra-to-alert correlation remain unverified. |
| 03 | Python Security Log Analyzer | Planned | Separate general analyzer, tests and samples; the SSH-specific detector in project 02 is not completion of project 03. |
| 04 | Network Traffic Investigation | Planned | Capture, protocol analysis and report. |
| 05 | Vulnerability Assessment | Planned | Scope, methodology, validation and remediation. |
| 06 | Mini SOC Monitoring & Alerts | Planned | Broader pipeline, architecture and evaluation; project 02's monitor is a limited precursor. |
| 07 | Incident Response Exercise | Planned | Synthetic timeline and containment/recovery plan. |
| 08 | SOC Alert Triage Casebook | Planned | Multiple triage cases and escalation decisions. |

## Start small

With 8 GB RAM, do **not** launch a multi-VM enterprise environment or install a full SIEM solely for presentation value. First establish host log access, baseline behavior, event interpretation, and reproducible reporting. Move toward project 06 after checking RAM and free disk.

## Definition of done (for each project)

- [ ] Purpose and threat/behavior clearly described.
- [ ] Lab topology, operating system and tools recorded.
- [ ] Safe, reproducible steps provided.
- [ ] Relevant observations and timestamps preserved, with private data removed.
- [ ] Findings separated from assumptions; false positives and limitations discussed.
- [ ] Short incident/report write-up completed.
- [ ] Author has personally validated and can explain the results.

## First sprint (project 01)

The resource and journal checks, two investigations and sanitized reports were completed and reviewed. Project 02 adds SSH-specific cases and monitoring; its remaining checks are listed in its README.
