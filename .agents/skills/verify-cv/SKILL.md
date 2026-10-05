---
name: verify-cv
description: Verify and update this CV against public APRL and personal-site records, including team membership, archival publication status, and synchronized TeX, README, and PDF artifacts.
---

# Verify this CV

## Sources and evidence

- Team and degree status: https://team-aprl.github.io/team.html
- Archival publication venues/status and paper links: https://team-aprl.github.io/publications.html
- Funding roles and dates: https://team-aprl.github.io/projects.html
- Courses/materials: https://team-aprl.github.io/teaching.html
- Talks, slides, awards, and service: https://gisbi-kim.github.io/ and its `/data/profile-sections.json` dataset.
- Explicit user corrections outrank older web records. Preserve a discrepancy in the changelog/evidence if the public source has not caught up. Never infer presentation language from the venue or location.

Record the review date, source URL, named entries, and counting rules in `verification/team-roster.json`. It is a dated evidence snapshot, not a live database. Refresh only after inspecting current source content; the PDF revision date is not proof that every biographical fact was rechecked.

## Team counting

Count named members in Current Lab Members / Full-time Researchers. Exclude the PI, incoming/prospective placeholders, open positions, interns, UGRP participants, alumni, and collaborators from this total. Count integrated M.S./Ph.D. students once within doctoral researchers, not again as M.S. students. The advising table contains graduate students, not the postdoc.

Run from the repository root:

```sh
python scripts/verify_cv.py
python scripts/verify_cv.py --live
```

The first command checks the saved roster against the TeX summary and advising table. The second also compares the named roster with the current public team page. A mismatch requires source review; do not overwrite the CV automatically. A network or parser failure means current membership remains unverified, not that the roster is empty. `--html path` checks a saved page for offline review.

## CV conventions

- Exclude preprints and non-archival workshop papers from Publications. An accepted archival paper may link to its arXiv version. Retain workshop awards and organizer roles in their appropriate sections.
- Use full conference/journal names and journal abbreviations. Retain latest-first display and stable category identifiers with the oldest entry numbered 1: J, C, B, DJ, DC.
- Keep `Giseop KIM`, `Leader/Director`, `Funded Projects`, approved links, and the approved section order. Update members and aggregate counts together.
- Add links only where the source supplies a corresponding public resource. TeX URLs must escape `&`, `%`, and `#`; verify the decoded PDF/README destinations. GitHub strips new-tab targets and PDF URI behavior depends on the viewer; do not claim to force new tabs.

## Build and publication

Update `main.tex` and any dated evidence/changelog, then run `python scripts/build.py` (or `--date YYYY-MM-DD` for a specified revision). README is generated from the source, including navigation. Keep the existing XeLaTeX/font workflow; use an available toolchain without installing a new one unnecessarily.

Inspect changed PDF pages for clipped text, broken links, orphaned headings, unexpected blank space, and page-spanning entries. Resolve material build warnings and confirm README headings, tables, and links. Stage only intended paths; after an authorized push, verify the branch SHA and PDF blob SHA against the remote. Report verification and publication as separate results.
