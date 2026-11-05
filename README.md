# Cybersecurity Portfolio | SOC Labs

Hands-on defensive cybersecurity projects focused on SOC L1 analysis, log investigation, threat detection, and incident response.

> Status: **In progress**. This is a personal learning laboratory, not professional SOC employment or evidence of production incidents.

## Goal

Build a series of small, reproducible security investigations. Each completed project will include a clear question, safe lab method, evidence, findings, limitations, and a report that can be explained in an interview.

## Lab environment

- HP laptop with AMD Ryzen 5 5500U, currently 8 GB RAM.
- Ubuntu 24.04 LTS installed alongside Windows 11 (dual boot).
- VirtualBox with Kali Linux as a guest VM.
- Resource-aware approach: no full Wazuh/Elastic stack until hardware and free disk capacity are reassessed.

## Projects

| # | Project | Status |
|---|---|---|
| 01 | [Linux Security Log Investigation](01-linux-log-investigation/README.md) | Completed: two reviewed cases |
| 02 | [SSH Authentication & Detection](02-ssh-detection/README.md) | Partially completed: controlled cases, detector, live monitor and Telegram demonstration; validation gaps remain |
| 03 | Python Security Log Analyzer | Planned |
| 04 | Network Traffic Investigation | Planned |
| 05 | Vulnerability Assessment | Planned |
| 06 | Mini SOC Monitoring & Alerts | Planned |
| 07 | Incident Response Exercise | Planned |
| 08 | SOC Alert Triage Casebook | Planned |

See [roadmap](docs/ROADMAP.md) for scope and completion criteria.

## Working method

1. Define a precise security question and expected observable evidence.
2. Work only on systems owned by or expressly authorized for the lab.
3. Collect minimally necessary evidence; redact usernames, IPs, tokens, secrets and personal information before committing.
4. Document commands, reasoning, findings, false positives, and limitations.
5. Mark a project **completed** only once it is tested, reproducible, and explained in the author's own words.

**Safe scope:** self-controlled VMs and systems only. No scans or exploitation of third-party targets without explicit authorization.

## Collaboration

- Human operator: executes, understands, validates, and documents findings.
- Codex: assists with local commands, scripts and documentation in the cloned repository.
- ChatGPT: reviews project scope, technical evidence and portfolio clarity.

The repository contains sanitized lab evidence and records AI assistance. Controlled test activity is distinguished from real incidents; no professional SOC employment is implied. See individual cases for the evidence and its limits.
