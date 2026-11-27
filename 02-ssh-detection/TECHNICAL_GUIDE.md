# SSH Authentication & Detection — Detailed Technical Guide

[← Project overview](README.md) · [← Portfolio overview](../README.md)

This guide preserves the full lab procedure, architecture, implementation notes, safety constraints, and evidence references. For a quick recruiter-friendly summary, start with the [project overview](README.md).

---

# 02 | SSH Authentication & Detection Lab

**Status:** Partially completed. A controlled end-to-end SSH monitoring test is supported by journal and operational logs, with Telegram receipt reported by the author; see [LAB-02-002](LAB-02-002-end-to-end-ssh-monitor.md). The author also reports a controlled Hydra/RockYou exercise; [LAB-02-003](LAB-02-003-hydra-exercise.md) records what can and cannot be corroborated. A successful SSH login baseline and the Hydra-to-alert correlation remain unverified. No real incident is claimed.

## Goal

Learn to identify and triage failed SSH logins in a controlled environment and create a simple, testable detection method. Emphasis is on SOC L1 investigation rather than offensive penetration testing.

## Lab constraints

- Host: Ubuntu 24.04 LTS, Windows 11 dual boot, 8 GB system RAM.
- Guest: Kali Linux in VirtualBox (2 GB RAM, NAT configured as of initial setup).
- All activity must remain on owned, explicitly authorized systems.
- No activity against public services or systems outside the explicitly authorized lab. Any controlled password testing is limited to the owner's lab and requires explicit authorization.
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

Controlled tests are lab exercises, not real-world incidents; label them accordingly and separate observed records from author-reported context and untested explanations. AI assistance may accelerate scripting and documentation, but the human author must understand, validate and defend each finding.

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

## Telegram notifications (offline lab)

`telegram_alerts.py` uses the standard library and the official Telegram Bot API. It can send a test message or reuse the existing detector on an offline file. It sends a concise detection summary, not full log lines. Telegram receives the source IP in each detection; use `--simulation` with synthetic data. The optional `--real` mode sends real IPs to Telegram and must only be used when this disclosure is authorized.

### Set up in your own terminal

Run these commands in the VS Code integrated terminal from `02-ssh-detection`:

```bash
python3 telegram_alerts.py setup
python3 telegram_alerts.py test
python3 telegram_alerts.py alert synthetic/ssh-sample.txt --simulation
```

`setup` asks for a hidden token and your numeric private chat ID once. It saves
plain-text JSON outside the repository at `~/.config/soc-monitor/credentials.json`.
The directory has mode `700` and the file `600` (owner access only). It asks before
replacing existing credentials; Enter declines. Cancelled or invalid input leaves
existing credentials untouched. Hidden input must be supported by the terminal.
Setup validates format locally; it does not contact Telegram or verify delivery.

`test`, `alert`, and `chat-id` load saved credentials without prompting.
`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, when set, override the corresponding
saved value independently, including empty values (which fail validation).
Unset those variables to use saved values. Missing or invalid configuration gives
a safe error directing you to setup. No arguments defaults to `test`.

If you still need your chat ID, send `/start` to your bot, then use the temporary
environment-variable method below to run `chat-id` before setup. The automated
tests use temporary directories, fictitious credentials and mocked Telegram calls;
they never read your saved configuration. AI assisted implementation and testing.

### Alternative: temporary environment variables

1. In Telegram, use [BotFather](https://t.me/BotFather) and `/newbot` to create a bot. Keep the token private. Open your new bot and send `/start` to it.
2. From this directory, enter the token without displaying it or putting it in shell history. Keep using the same terminal for the following commands:

   ```bash
   read -r -s -p 'Telegram bot token: ' TELEGRAM_BOT_TOKEN; echo
   export TELEGRAM_BOT_TOKEN
   python3 telegram_alerts.py chat-id
   ```

   The command lists numeric IDs from private chats in the bot's pending updates; it does not show message text. Select your own private chat. If none appears, send `/start` and retry. `getUpdates` cannot be used while the bot has a webhook; do not remove or change an existing webhook without understanding its use. Do not paste your token or chat ID into a public issue or chat.
3. Enter the ID locally, then send the test message:

   ```bash
   read -r -p 'Private chat ID: ' TELEGRAM_CHAT_ID
   export TELEGRAM_CHAT_ID
   python3 telegram_alerts.py test
   ```

   Confirm the message appears on your phone. Telegram's API acceptance alone does not prove the phone displayed it.
4. Run the synthetic demonstration:

   ```bash
   python3 telegram_alerts.py alert synthetic/ssh-sample.txt --simulation
   ```

   One `LAB / SIMULATION` notification is expected. It reports the documentation-range source IP, failure count at threshold, window, timestamps, indicative severity, and need for investigation. Run `python3 -m unittest -v` to run all tests with Telegram calls mocked; tests do not send messages. When finished, `unset TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID` removes them from that shell.

An alert is sent only when the existing detector crosses its threshold, suppressing duplicate notifications within a continuous burst during one run. This offline command has **no persistent deduplication**: running it again over the same file sends the same detection again. It does not retry automatically; timeouts can leave delivery uncertain, and rerunning after an error can duplicate a message. Confirm delivery before retrying. Error messages avoid printing tokens and server responses. Environment variables remain accessible to suitably privileged local processes and child processes of the shell; use a trusted terminal, never commit credentials, and revoke a token in BotFather if exposed.

## Real-time SSH monitor

After Telegram setup, run in the VS Code integrated terminal from this directory:

```bash
python3 soc_monitor.py
```

Keep the terminal open. Stop with **Ctrl+C**; the monitor terminates and reaps its
journalctl child. This foreground program does not install a service, schedule
jobs, change SSH, edit credentials, or generate authentication attempts.

The monitor checks journal access before loading credentials. A failed command or
journal warning stops startup without printing log contents. An empty or
unparseable recent entry produces a visibility warning; access alone does not
prove all required authentication records are available. Do not run with sudo
just to bypass an access failure; investigate the user's permissions separately.

It follows `ssh.service` with `journalctl --follow --lines=0 --output=short-iso`.
Only entries arriving after the follower starts are consumed, including on restart;
history and events during downtime are not replayed. The existing `parse_line`
and `detect` functions are reused unchanged. Three OpenSSH `Failed password`
events from one IP within an inclusive 60-second window trigger a Telegram
summary. Source IPs and event timestamps are disclosed to Telegram; use this on
authorized lab systems only. Other authentication failure formats are ignored.

In-memory state suppresses repeated sends while the source stays above threshold.
Rearming follows the offline rule exactly: before adding the next failure, if
fewer than three previous failures remain in the window, a new threshold crossing
may alert again. These are distinct crossings, even if windows overlap. Identical
journal lines are distinct entries and count separately, as in the offline rule.
State is not persisted; restarting discards partial windows. Failures with a
timestamp earlier than the latest matching event are ignored (for example, after
a backward clock adjustment). Windows and source state expire on the next matching
event, keeping only 60 seconds of matching activity; memory scales with that
activity. This is intended for the small lab, not high-volume production use.

A Telegram error stops monitoring without retries because delivery may be unknown.
A closed journal stream also stops with an error. Restart manually after checking
the cause. No delivery guarantee is claimed during disconnections or downtime.

Validation: `python3 -m unittest -v` covers simulated thresholds, the inclusive
boundary, separate IPs, suppression/rearming against offline detector results,
ignored lines, backward timestamps, access warnings, cleanup on interruption and
send failure without retry. Telegram and credentials are mocked. A read-only local
check confirmed SSH journal access without warnings, and a brief real follower
started and stopped successfully without collecting or sending event contents.
No new SSH attempts were generated during implementation checks. The subsequent
controlled end-to-end test is documented below; this is not evidence of an attack.

### Detached execution with private operational logs

`soc_monitor_background.py` wraps the monitor with an exclusive advisory lock,
SIGTERM cleanup and rotating logs (256 KiB, two backups). Always use this runner
for background operation; direct `soc_monitor.py` invocations bypass its lock.
The runner stores `monitor.lock` (current PID) and `monitor.log` in
`~/.local/state/soc-monitor/`, outside Git, with directory mode 700 and file mode
600. Logs contain operational messages and sanitized errors, not journal lines,
API responses, tokens or arbitrary exception tracebacks. Log timestamps use the
host's configured timezone. Lock ownership, rather than a potentially stale PID
file, determines whether another runner is active.

To launch manually from the project directory without tying it to the terminal:

```bash
nohup python3 -u soc_monitor_background.py </dev/null >/dev/null 2>&1 &
```

Inspect the PID and status, and view operational messages:

```bash
cat ~/.local/state/soc-monitor/monitor.lock
pgrep -af 'python3.*soc_monitor'
tail -n 20 ~/.local/state/soc-monitor/monitor.log
```

To stop, verify the PID belongs to this runner with `ps -p PID -o args=`, then
run `kill -TERM PID`. This also stops its journalctl child. It is not a service:
there is no automatic startup after reboot or automatic recovery after failure.
Desktop session policies can terminate user processes on logout; detachment
specifically removes the dependency on the VS Code terminal. Starting/stopping
creates a monitoring gap; no historical entries are replayed. A live follower and
readable journal alone establish readiness, not an end-to-end SSH detection. No test
alerts are sent by the launcher.

## Verified controlled end-to-end demonstration

[LAB-02-002](LAB-02-002-end-to-end-ssh-monitor.md) documents the architecture,
evidence, limitations and manual reproduction steps for the 2026-11-04 test.
Three journal-confirmed failures occurred at 20:51:32, 20:51:53 and 20:52:00
UTC−03:00 (28 seconds). The local monitor log records API acceptance at
20:52:12.084; the author independently confirms the matching Telegram alert.
This was intentional lab activity, not an observed hostile attack.

Evidence: [anonymized journal derivative](evidence/LAB-02-002-parseable-anonymized.txt)
and [sanitized operational log](evidence/LAB-02-002-monitor-sanitized.txt).
Private IPs, accounts, host identifiers, chat IDs and bot tokens are omitted.
To reproduce the detector result without network requests or new SSH attempts:

```bash
python3 detect_ssh_failures.py evidence/LAB-02-002-parseable-anonymized.txt
python3 -m unittest -v
```

Expected: three matching failures, one detection. The comment lines are ignored.
Startup, status and shutdown commands are in the detached-execution section
above; always check for an existing monitor before launching another.

A content scan of Git-visible tracked and untracked files found no Telegram bot
tokens, private-key headers or non-placeholder credential JSON values during this
review. This is a scoped content check, not a historical Git secret audit. Saved
credentials remain outside the repository and were not read during this review.
