# SOC L1 Investigation Report | Privileged update-notifier execution

## Case metadata

- **Case ID:** LAB-01-001
- **Analyst:** Portfolio author, with AI assistance for log queries, analysis, and drafting.
- **Environment / scope:** Personal Ubuntu 24.04.5 LTS workstation; current boot. Focused review of 2026-11-04 06:17:30–06:20:00 (UTC−03:00).
- **Investigation date and timezone:** 2026-11-04, UTC−03:00.
- **Status:** Draft for author review; no incident confirmed.

## Alert / investigation trigger

During a baseline review of authentication events, a `pkexec` entry at 06:18:45 recorded a privileged session associated with the local user. The investigation asked which program ran, what surrounding activity might explain it, and whether the available evidence supported escalation. This was an analyst observation, not a generated security alert.

## Evidence sources

- The systemd journal for the current boot, queried read-only using `journalctl -b` with `--since '2026-11-04 06:17:30'` and `--until '2026-11-04 06:20:00'`, `--no-pager`, and `-o short-iso`. The window was also reviewed in JSON format to identify log sources.
- Earlier read-only current-boot journal searches for PAM, login, session, `sudo`, and authentication-failure messages provided the initial observation. Searches were based on selected text patterns and do not establish that every authentication event was captured.
- Sanitized original journal excerpts are in [evidence/sanitized-log-excerpts.txt](evidence/sanitized-log-excerpts.txt). The timeline paraphrases verified messages. Hostname, local username, local UID, and home directory are redacted in the excerpts; system account names and standard program paths are retained for technical context.
- `dpkg-query -S /usr/lib/update-notifier/package-system-locked` attributed the file to `update-notifier-common`; `dpkg-query -W` reported that package installed, version `3.192.68.2`. Package ownership does not verify the file's integrity or origin.
- Visible journal files were readable in the investigation environment. Completeness across every possible log source was not established. A prior `journalctl --verify` attempt failed when it could not create a temporary data file in the read-only environment; its output is inconclusive and is not evidence of journal corruption. It was not repeated.

## Timeline

All timestamps are on **2026-11-04**, UTC−03:00. Confidence refers to the observation in the journal, not to its cause or legitimacy.

| Time | Source | Observed event | Confidence |
|---|---|---|---|
| 06:18:20 | `systemd` | Reported `Starting apt-daily-upgrade.service`, described as daily APT upgrade and clean activities. | High |
| 06:18:33 | `systemd`, `PackageKit` | PackageKit service was started. | High |
| 06:18:35 | `polkitd` | Reloaded rules and reported loading, compiling and executing 16 rules. | High |
| 06:18:45 | `pkexec`, PAM | `pam_unix(polkit-1:session)` reported a session opened for `root` by the local user. | High |
| 06:18:45 | `pkexec` | The same `pkexec` process logged execution as `root` of `/usr/lib/update-notifier/package-system-locked`. | High |
| 06:18:45 | `update-notifier.desktop` | Logged a reference to `/var/cache/apt/archives/lock`. | High |
| 06:18:47 | `systemd` | Reported `apt-daily-upgrade.service` deactivated successfully and finished. | High |

## Analysis

### Confirmed facts

The `pkexec` session-opening message and command-execution message share the same process identifier and timestamp. They associate a privileged session with execution of the update-notifier helper as `root`. The command was logged between systemd's `Starting` and `Finished` messages for the APT daily upgrade service. The `Starting` message alone does not establish that systemd had already reported the service as started. A separate update-notifier message referred to an APT archive lock in the same second. The installed package database attributes the helper path to `update-notifier-common`; this does not establish file integrity.

The journal also recorded a polkit rules reload ten seconds earlier. It did not identify that reload as the cause of the execution or record a specific authorization decision in the reviewed window. PackageKit activity was present, but its causal relationship to `pkexec` was not established.

### Hypothesis and alternatives

The helper path, APT lock reference, and overlapping upgrade activity are consistent with a package-management operation related to Ubuntu updates. A plausible explanation is that update-notifier checked a package-system lock while updates were running. The timing and naming alone do not prove that `update-notifier.desktop` launched `pkexec` or establish exactly what the helper did.

Other origins or user actions cannot be excluded without additional context. No indicator of compromise was identified in the evidence examined; that is not proof that the host was uncompromised.

### Missing information

- The requesting process or parent process and the precise action that initiated `pkexec`.
- The polkit decision and authentication method, including whether a prompt was shown or an existing authorization was used.
- The helper's completion status and detailed behavior.
- Whether the local user expected an update-related interaction at that time.
- Complete coverage of all authentication events and other potentially relevant evidence sources.

## Triage decision

- **Classification:** Probably legitimate activity; no incident confirmed. This is a provisional assessment of the observed activity, not a verified false-positive alert.
- **Priority:** Low for this personal lab review, based on the evidence currently available; no formal organizational severity policy was applied.
- **Reasoning:** The installed package database attributes the logged privileged program to `update-notifier-common`; its execution fell between the daily APT upgrade service's starting and finished messages; and a contemporaneous update-notifier message referenced an APT lock. These observations support a benign administrative explanation, but do not establish file integrity, the requesting process, authorization method, or user intent.
- **Escalation:** No escalation is recommended on the evidence reviewed: there is a plausible routine explanation and no identified indicator of compromise. Reassess if the user does not recognize the activity or if additional evidence identifies an unexpected requester, authorization, or behavior. A real SOC should follow its own escalation policy.

## Response / recommendation

The author should review the timeline and, if possible, recall whether an update-related action was expected. If further investigation is chosen, use read-only sources to look for the requester and helper outcome, while protecting personal data. Preserve only sanitized, relevant excerpts for the portfolio and distinguish new observations from assumptions.

No containment, remediation, configuration changes, simulated activity, or privileged commands were performed as part of this focused investigation. No incident was declared.

## Lessons and limitations

PAM session messages show session lifecycle events; an open session alone does not reveal which authentication method was used. `pkexec` provides the executed command, while nearby timestamps can supply context but do not establish causation. A narrow journal window, text filters, and incomplete knowledge of the requester limit the conclusion. The assessment should be revisited if new evidence changes the context.
