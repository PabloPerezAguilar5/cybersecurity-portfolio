# LAB-02-001 | Controlled SSH authentication failure

**Status:** Reviewed. **Classification:** Benign controlled lab activity, based on the author's account; no incident confirmed.

## Context and evidence

The author reports generating one deliberate failed SSH authentication from their Kali VM to their Ubuntu host on 2026-11-04. A read-only journal query independently found an OpenSSH `Failed password` entry at 18:05:31 UTC−03:00 and a subsequent connection-close entry for the same process. The [sanitized excerpt](evidence/LAB-02-001-sanitized-log-excerpt.txt) retains the failure message, timestamp, and PID while redacting identifying fields.

The journal also contained a PAM authentication-failure message for that process two seconds earlier. These records are consistent with one authentication attempt; they must not be counted as separate failures. The reported intent and Kali-to-Ubuntu topology come from the author; this one message alone does not establish intent or independently prove the client's operating system. One failed password does not establish a brute-force attack or compromise.

## Scope and limitations

The review covered the brief time window around the reported event, not a comprehensive security assessment. No further authentication attempts or configuration changes were performed for this documentation. A [parser-compatible copy](evidence/LAB-02-001-parseable-anonymized.txt) substitutes fictitious host, username, documentation-range IP and port while retaining the timestamp and failure text. On this transformed real entry, the detector matched one failure and produced zero detections at its default threshold of three. The repeated-failure examples use separate **synthetic** data. A successful SSH login baseline was not verified. AI assisted with the journal query and drafting.
