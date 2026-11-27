# Portfolio Publication Checklist

[← Portfolio overview](../README.md)

This repository is **private** and remains a personal learning environment until its owner explicitly changes visibility. This checklist describes work to perform **before** making it public; checking it off requires actual verification.

## 1. Security and privacy

- [ ] Review **all tracked files** and the full Git history, including reachable branches and tags, for tokens, credentials, usernames, real hostnames, personal information, screenshots, and raw logs. `.gitignore` does not protect previously committed content.
- [ ] Review any evidence files and screenshots manually. Use documentation-range addresses for samples; label transformed real records and entirely synthetic data separately.
- [ ] Inspect external links, author information, commit metadata and configuration examples for information the owner does not wish to publish.
- [ ] If a real secret was ever committed, revoke or rotate it and address the Git history before publication. Simply deleting the current file is not sufficient.
- [ ] Keep local Telegram credentials under `~/.config/soc-monitor/`; do not copy them into the repository.

## 2. Evidence and technical reproducibility

- [ ] From `02-ssh-detection/`, run `python3 -m unittest -v` and record the actual result. The repository includes 30 test functions; their presence alone does not prove the latest run passes.
- [ ] Run the offline detector with `python3 detect_ssh_failures.py synthetic/ssh-sample.txt` and confirm the documented output.
- [ ] Verify that links between the main README, lab overviews, reports, technical guide and sanitized evidence resolve.
- [ ] Check all claims against reports. Distinguish observed events, author-reported actions and unverified assumptions.
- [ ] Document the remaining SSH successful-login baseline and Hydra-event-to-alert correlation gap accurately.
- [ ] Add only owner-reviewed, anonymized screenshots or diagrams. A screenshot must not imply that an unverified test was successful.

## 3. Recruiter experience

- [ ] Confirm the repository's first screen explains **what was built, what was observed and what remains incomplete**.
- [ ] Keep short summaries in each lab README and in-depth procedures in linked technical reports or guides.
- [ ] Explain clearly that this is personal learning, with AI assistance disclosed, not professional SOC employment.
- [ ] Verify that the work can be described and defended independently in an interview.

## 4. Publication decision

- [ ] Owner explicitly decides to make this repository public, after security review.
- [ ] Only after publication, add the public repository link to LinkedIn or a CV.

**Current status:** Checklist is a plan, not evidence that any of these checks have passed. The repository has not been made public by these documentation changes.
