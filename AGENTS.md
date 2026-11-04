# Codex instructions: SOC cybersecurity portfolio

You are assisting with a private, evidence-based learning portfolio aimed at entry-level SOC / security analyst roles. Communicate with the user in **Argentine Spanish**, using short steps. Repo documentation should be clear, professional English unless user directs otherwise.

## Context

- Host is an HP laptop, Ryzen 5 5500U, currently 8 GB RAM.
- Ubuntu 24.04 LTS and Windows 11 are installed in dual boot.
- VirtualBox and a Kali Linux guest are already available.
- Storage is limited; check resources before suggesting VM images, log collection or installations.
- The first task is `01-linux-log-investigation`. Do not build the entire SOC at once.

## Working rules

1. Inspect before changing. Prefer safe, read-only commands in the first stage.
2. Explain what each command does and why it matters to a SOC analyst; let the user interpret results.
3. Do not install heavy monitoring stacks (Wazuh, Elastic, multiple VMs) without checking free RAM and disk and asking permission.
4. Do not alter BIOS, bootloaders, partitions, Windows, firewall rules, network exposure, or system services without explicit user authorization.
5. Generate activity only on owned or explicitly authorized lab systems. Never run intrusive scans against third parties.
6. Do not claim an incident, an alert, a vulnerability, or a detection has occurred unless actual evidence supports it.
7. Keep raw system logs, credentials, tokens, personal details, private IPs and sensitive artifacts out of commits. Use sanitized excerpts with clear labels.
8. Do not claim professional SOC experience from a personal lab. Document the author's own contributions and AI assistance accurately.
9. Make small, reviewable commits. Do not replace existing work without inspecting it.
10. After each task, report what changed, what was observed, what remains unverified, and what the human must still test.

## Immediate goal

Open `01-linux-log-investigation/README.md`, inspect the current Ubuntu journal with read-only commands, and plan the first investigation before implementing or installing anything.
