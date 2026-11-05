# LAB-02-003 | Author-reported controlled Hydra exercise

**Status:** Partial; the author confirms the exercise time, while independent event-to-alert correlation remains unavailable. **Classification:** Author-reported authorized lab activity; no real incident established.

## Reported exercise

The author reports a controlled SSH password-testing exercise using Hydra and the RockYou wordlist against their own Ubuntu SSH server from their Kali laboratory, and confirmed that the exercise occurred at approximately 22:36 on 2026-11-04. The author also reports that the monitor detected the activity and that a Telegram alert was received at approximately 22:36. The alert time and its association with this exercise are author testimony, not independently corroborated facts. The exact command, wordlist entries, target account, successful credentials and full logs are intentionally not reproduced. The available records reviewed here do not independently identify Hydra or RockYou or independently confirm which alert belongs to the exercise. No such activity was generated during this review.

## Observations in the available records

- On 2026-11-04 between **22:36:16 and 22:37:22 UTC−03:00**, a read-only journal query found **23** OpenSSH `Failed password` messages from one source, across four `sshd` process IDs. The query window was 22:36:10–22:37:30, and the count refers to those messages only; PAM summaries were not added as separate attempts. Three messages were recorded at 22:36:16, 22:36:19 and 22:36:22. A [sanitized excerpt](evidence/LAB-02-003-journal-sanitized.txt) preserves those three lines and their process ID.
- These three observed failures would meet the documented detector threshold of three in an inclusive 60-second window. This is an offline inference from the timestamps, **not proof that the live monitor was running or sent an alert for this burst**.
- The available local background-monitor log records a Telegram connection failure with uncertain delivery and a monitor exit at **22:15:38**, before that burst. It contains no entries for the 22:36–22:37 interval. This log alone cannot rule out a separate monitor instance, other logs, or a different exercise time. The [sanitized operational excerpt](evidence/LAB-02-003-monitor-sanitized.txt) records the failure and exit.
- The reported 22:36 Telegram alert has **no independent technical correlation** with the monitor record reviewed here: that record has no 22:36 event, delivery confirmation, or correlation identifier linking an alert to the journal burst.
- A different earlier controlled test, [LAB-02-002](LAB-02-002-end-to-end-ssh-monitor.md), has journal failures at 20:51–20:52 and an operational message recording Telegram API acceptance at 20:52:12. The author confirmed receiving the matching alert for that test. API acceptance is not independent evidence of a phone display. These records do not establish that the earlier test used Hydra or RockYou.

## Assessment and limitations

The evidence supports three distinct categories:

- **Confirmed in the available records:** 23 OpenSSH `Failed password` messages were present in the queried window; the three preserved entries meet the detector's threshold when evaluated offline; and the reviewed monitor log records a delivery-uncertain connection failure and exit at 22:15:38, with no entries for the burst.
- **Author testimony:** the exercise took place at approximately 22:36, used Hydra and RockYou in the authorized lab, and a Telegram alert was received at approximately that time. The journal and monitor excerpt do not independently establish those details or link the reported alert to the burst.
- **Hypotheses, not established findings:** another monitor instance or unreviewed log might contain relevant activity, or the reported alert may not correspond to this burst. The available evidence neither confirms nor excludes these possibilities.

The specific Hydra-to-Telegram chain remains unverified, and the reported 22:36 alert has no independent technical correlation with the monitor record reviewed here. A successful authentication, compromise, real intrusion, or production-grade detection performance is not claimed. The earlier independently observed monitor acceptance and author-confirmed phone receipt are documented separately in LAB-02-002.

The journal and operational log are limited to visible records and the queries described. Counts may not represent all activity; multiple journal lines associated with one SSH connection or PAM summary must not be confused with distinct sessions. Hostname, user, private IP and port are redacted; no passwords, wordlist contents or credentials are retained. AI assisted with read-only investigation, anonymization and drafting; the human author supplied the controlled-lab context.
