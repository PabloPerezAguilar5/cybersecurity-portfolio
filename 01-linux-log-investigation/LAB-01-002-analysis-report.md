# SOC L1 Investigation Report | Authentication failure

## Case metadata

- **Case ID:** LAB-01-002
- **Analyst:** Portfolio author, with AI assistance for journal queries, analysis, and drafting.
- **Environment / scope:** Personal Ubuntu 24.04.5 LTS workstation; current boot; focused journal review of 2026-11-04 11:34:30–11:36:30 (UTC−03:00).
- **Investigation date and timezone:** 2026-11-04, UTC−03:00.
- **Status:** Completed. Controlled lab simulation; no real incident confirmed.

## Alert / investigation trigger

The portfolio author reported intentionally entering an incorrect password during a local `su - "$USER"` test and identified a PAM authentication failure at 11:35:28. The objective was to interpret the observed records and distinguish them from the author's account of the test. This is a laboratory investigation, not a generated security alert.

## Evidence sources

- The current-boot systemd journal, queried read-only using `journalctl -b --since '2026-11-04 11:34:30' --until '2026-11-04 11:36:30' --no-pager -o short-iso`. The focused window was reviewed for relevant context.
- Two original entries, sanitized to remove the hostname, local username, local UID and terminal identifier, are preserved in [evidence/LAB-01-002-sanitized-log-excerpts.txt](evidence/LAB-01-002-sanitized-log-excerpts.txt). The timestamp, process and PID are retained. No password or raw log file is included.
- The author's statement provides the command, intentional incorrect password, and controlled-lab context. These details are not independently established by the journal entries.

## Timeline

All timestamps are on **2026-11-04**, UTC−03:00. Confidence refers to what the journal records, not the actor's intent.

| Time | Source | Observed event | Confidence |
|---|---|---|---|
| 11:35:28 | `su[21405]`, `pam_unix` | PAM logged an authentication failure for the local account, with a local terminal and effective UID 0 in the record. | High |
| 11:35:29 | `su[21405]` | The same process logged `FAILED SU` for the local account and terminal. | High |

## Analysis

### Confirmed observations

The two messages have the same process name and PID and are one second apart. They are consistent with the same failed `su` attempt; they are not evidence of two separate attempts. In the reviewed two-minute window, these were the only `su` authentication-failure messages observed. This narrow observation does not establish the absence of failures outside that window or in other sources.

The PAM record includes a real UID corresponding to the local user and an effective UID of 0 for the process at the time of the event. An effective UID of 0 in this record does **not** establish that authentication succeeded, that a privileged shell was opened, or that a malicious privilege escalation occurred. The subsequent `FAILED SU` message records a failed `su` operation.

### Author-provided context and interpretation

The author states that they ran `su - "$USER"` on their own Ubuntu system and deliberately supplied an incorrect password as a controlled test. Based on that account and the matching time and failure records, this is classified as benign lab activity. The journal entries alone cannot establish intent, the exact command line, the password entered, or whether the actor was authorized.

A single observed failure is not sufficient evidence of a brute-force attack or compromise. Other explanations for a failure can include an accidental incorrect password or an unauthorized attempt; neither intent nor cause can be determined from these messages alone.

### Missing information

- Independent confirmation of the exact command line, the authentication input, and the actor's intent.
- Complete authentication coverage outside the reviewed window and across other log sources.
- A comprehensive assessment of the workstation; no compromise can be confirmed or ruled out from this narrow review.

## Triage decision

- **Classification:** Benign laboratory activity; controlled simulation, not a real incident. This assessment depends on the author's account of the test.
- **Priority:** Low for this personal lab; no organizational severity policy was applied.
- **Reasoning:** The author reports intentionally producing a failed login test, and the matching journal entries record a failed `su` operation. No evidence of an attack was identified in the reviewed window. The records do not independently prove intent or rule out activity elsewhere.
- **Escalation:** No escalation is recommended for this documented controlled test. Reassess if additional evidence contradicts the author's account or shows a broader pattern; a real SOC should follow its own escalation policy.

## Response / recommendation

The author should review the redacted evidence and validate the interpretation before publication. No further authentication attempts, containment, remediation, installation, or configuration changes were performed for this investigation. Preserve only sanitized evidence and avoid recording authentication secrets.

## Lessons and limitations

- **`su`:** A program used to run a shell or command with another user identity. The requested account and access controls affect its behavior.
- **`pam_unix`:** A PAM module used by Linux services for account and authentication functions. Here, `su-l:auth` identifies the PAM service and authentication stage that logged the failure.
- **`uid` and `euid`:** The real user ID identifies the process's real user; the effective user ID is used for many permission checks. A process may have different real and effective IDs. Their values here do not prove a successful login.
- **`tty`:** The terminal associated with the event. A pseudoterminal such as the one in the original entry is compatible with a terminal session, but does not by itself identify the person at the keyboard.
- **`authentication failure`:** PAM reported that authentication failed. The message alone does not establish exactly which input was supplied or why the failure occurred.

The evidence is limited to a short journal window on one host. Correlation by PID and time supports associating these messages, while the benign intent comes from the author's statement. No claim of professional SOC experience is made for this personal exercise.
