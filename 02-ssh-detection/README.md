# 02 | SSH Authentication & Detection Lab

**Status:** Planned. No SSH attacks, log events, detections, or findings claimed yet.

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

- [ ] Approved topology diagram or text description.
- [ ] Baseline log source and successful/failed authentication patterns documented.
- [ ] One controlled failed login safely generated and investigated.
- [ ] Sanitized evidence with timestamps and fields.
- [ ] Reproducible, tested detection logic over clearly labeled synthetic samples.
- [ ] A triage report explaining classification, alternatives and limitations.
- [ ] No secrets, private identifiers, raw system logs or unrelated data committed.

## Portfolio integrity

All lab activity is simulated and must be labeled as such. AI assistance may accelerate scripting and documentation, but the human author must understand, validate and defend each finding.
