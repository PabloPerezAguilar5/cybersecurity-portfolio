# 02 | SSH Authentication & Detection Lab

**Status:** Completed for the reviewed educational scope: one controlled SSH failure and an offline repeated-failure detector. A successful SSH login baseline was not verified; see the remaining item below. Repeated-failure detections use synthetic data only. No real attack or incident is claimed.

## Goal

Learn to identify and triage failed SSH logins in a controlled environment and create a simple, testable detection method. Emphasis is on SOC L1 investigation rather than offensive penetration testing.

## Lab constraints

- Host: Ubuntu 24.04 LTS, Windows 11 dual boot, 8 GB system RAM.
- Guest: Kali Linux in VirtualBox (2 GB RAM, NAT configured as of initial setup).
- All activity must remain on owned, explicitly authorized systems.
- No scanning, credential attacks, password guessing, or requests to public services.
- Do not expose SSH to the Internet or change firewalls / VM network mode without explicit permission.
- Do not install software, enable SSH services, or modify configuration until the human author inspects the environment and agrees.

## Investigation phases

### Phase A: Establish lab topology (read-only)

On Ubuntu, record:
```bash
cat /etc/os-release | grep PRETTY_NAME
ip -br addr
command -v ssh || true
command -v sshd || true
systemctl is-active ssh 2>/dev/null || true
ss -ltn | grep ':22 ' || true
df -h /
```

On Kali, record:
```bash
ip -br addr
command -v ssh || true
command -v sshd || true
```

Do not assume the Kali VM can directly connect to the Ubuntu host just because the guest has NAT. Confirm the actual network path and permission boundaries.

### Phase B: Baseline

Identify which host will act as the controlled SSH server and which will be the client. Record the expected normal authentication events before generating any test. Choose minimal configuration changes only after explicit approval.

### Phase C: Single known failed attempt

On the authorized lab server, produce **one** controlled failed SSH authentication, then identify its timestamp, service, account, process and source. Do not run high-rate or automated login attempts. Keep any credentials out of shell history and commits.

### Phase D: Detection logic

Use sanitized synthetic sample logs to build and test a simple rule or Python script for repeated failures over a fixed time window. Note false positives, thresholds, grouping fields, and what evidence does/does not establish an attack.

### Phase E: Triage report

Report observations from the actual controlled single attempt separately from any synthetic data used in detection-rule tests. Never claim a real attack happened.

## Definition of done

- [ ] Approved topology diagram or text description: the author reports Kali as the client and Ubuntu as the server, but the complete network configuration was not independently verified in this review.
- [ ] Baseline log source and successful/failed authentication patterns: the failed pattern was observed in the journal; a successful SSH login baseline has not been verified.
- [x] One author-reported controlled failed login investigated against the journal.
- [x] Sanitized evidence with timestamps and fields.
- [x] Reproducible, tested detection logic over clearly labeled synthetic samples.
- [x] A triage report explaining classification, alternatives and limitations.
- [x] No secrets, private identifiers, raw system logs or unrelated data found in the reviewed project files.

## Portfolio integrity

All lab activity is simulated and must be labeled as such. AI assistance may accelerate scripting and documentation, but the human author must understand, validate and defend each finding.

## Controlled event and synthetic detector

- [LAB-02-001](LAB-02-001-controlled-ssh-failure.md) describes the real, controlled single failure and links to its sanitized evidence. The author's account supplies the intent and topology; the journal establishes what was logged.
- `evidence/LAB-02-001-parseable-anonymized.txt` is derived from that real entry, **not synthetic event data**. Its hostname, username, source IP and port were substituted with fictitious values; `192.0.2.101` is a documentation address, not the actual client IP. Its timestamp, process, PID and failure text remain from the observed event. The transformations preserve parser compatibility but are not original field values.
- `detect_ssh_failures.py` analyzes an existing text file. It does not connect to a host or generate authentication attempts.
- `synthetic/ssh-sample.txt` is entirely **synthetic**: its IP addresses are documentation examples, not observed sources. It contains two widely spaced failures from one source, three failures in 60 seconds from another, and an unrelated successful-authentication message.

Run from this directory with Python 3.10 or newer; no third-party dependencies are required:

```bash
python3 detect_ssh_failures.py synthetic/ssh-sample.txt
python3 detect_ssh_failures.py synthetic/ssh-sample.txt --threshold 4 --window-seconds 60
python3 detect_ssh_failures.py evidence/LAB-02-001-parseable-anonymized.txt
python3 -m unittest -v
```

The defaults are **3 failures within 60 seconds**, inclusive: failures exactly 60 seconds apart are included. The synthetic sample produces one detection with default settings and none with threshold 4. The transformed real entry produced one matching failure, zero ignored lines, and zero detections at the default threshold. These thresholds are demonstration choices, not validated security policy. Detections are indicators for review, not proof of an attack. Exit status 0 means analysis completed, even if detections were found; invalid settings or input errors return a nonzero status.

### How it works

1. Parse OpenSSH `Failed password` lines in `journalctl -o short-iso` format, including `invalid user` and valid IPv4 or IPv6 addresses. Timestamps must include a timezone offset; unrelated or malformed lines are counted as ignored.
2. Sort matching events by timestamp and group them by source IP. For each source, retain a sliding window of recent failures, dropping entries older than the configured duration.
3. Emit a detection when a source reaches the threshold. Further failures in that continuous burst do not create duplicate detections. Once the retained count falls below the threshold, a later event can trigger a new detection. The displayed count is the count at the crossing, not a total for the entire burst.

### Limitations and safe handling

The parser intentionally handles only the specified `short-iso` OpenSSH `Failed password` format. It ignores traditional syslog dates without a year or timezone, other timestamp layouts, hostnames instead of IP addresses, PAM-only messages, other SSH authentication methods, and differently formatted entries. Duplicate input lines are counted separately. The tool sorts and holds input in memory and is intended for small offline files, not continuous production monitoring. It neither detects distributed attempts across IPs nor correlates a subsequent success. Shared NAT, mistyped passwords, incomplete or duplicated logs, and threshold choice can cause false positives or false negatives; a human must investigate context.

The original redacted excerpt uses markers rather than an IP and is deliberately not machine-parseable. Its separate transformed copy uses fictitious parser-compatible values, as described above. For actual logs, a suitable `journalctl -o short-iso` export may contain usernames, addresses and other sensitive information. Keep raw exports and detector output containing real IPs private; review and anonymize any evidence before committing. This implementation does not read the journal itself or write evidence automatically.
