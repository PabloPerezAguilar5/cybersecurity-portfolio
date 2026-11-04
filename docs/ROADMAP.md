# SOC Portfolio Roadmap

This is a sequence of small, individually demonstrable projects. Each project begins as **planned**, not completed.

| ID | Project | Core question | Evidence/deliverable |
|---|---|---|---|
| 01 | Linux Security Log Investigation | What happened on this Linux host? | Annotated timeline + incident investigation report |
| 02 | SSH Authentication & Detection | Are repeated login failures benign or suspicious? | Controlled SSH authentication events + triage report |
| 03 | Python Security Log Analyzer | Can we detect a reproducible pattern in log samples? | Script, tests, sample sanitized logs, limitations |
| 04 | Network Traffic Investigation | What protocols and endpoints explain this capture? | Safe capture, protocol analysis, report |
| 05 | Vulnerability Assessment | Which controlled-lab findings are actionable? | Scope, scan methodology, validation, remediation |
| 06 | Mini SOC Monitoring & Alerts | Can a pipeline collect events and fire meaningful alerts? | Architecture, alert rules, evaluation, screenshots |
| 07 | Incident Response Exercise | How would an analyst triage and contain a simulated incident? | Synthetic event timeline + containment/recovery plan |
| 08 | SOC Alert Triage Casebook | Can we prioritize and document multiple types of alerts? | TP/FP case files with escalation decisions |

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

## First sprint

1. Confirm disk space and journal availability (read-only).
2. Capture a harmless baseline of boot and authentication-related events.
3. Choose and investigate one defensible observation.
4. Complete report and attach redacted evidence.
5. Review before marking project 01 as complete.
