# CV revision history

## 2026-10-06

The active CV now uses the author's July 23, 2026 XeLaTeX design recovered from `giseop_kim_cv.tex`, rather than the repository's March `cv.cls` design. The recovered source's accompanying PDF was byte-identical to `giseop_kim_cv_archival_v3.pdf` in the author's [Drive CV folder](https://drive.google.com/drive/folders/1_0XFI8jedwYIr4QIIQ17cvAXhwOPRSrd). Historical sources remain in `legacy/`; the original external files were not changed.

- Added the two accepted iSpaRo 2026 papers, **MarsLab** and **Simulation for Planetary Robotic Perception and Autonomy**. Both retain “accepted, to appear” because the conference is November 3–6, 2026.
- Removed “to appear” from the IROS 2026 and ECCV 2026 papers after the listed conference dates. Added LT-Mem's IROS 2026 **Best Paper Award**.
- Excluded preprints, non-archival workshop papers, and non-archival domestic conference entries. Workshop papers without established archival proceedings were also left out of the publication list. Workshop organizing roles and awards remain in their own sections. The active publication list contains 31 entries.
- Corrected HeLiPR's journal year to **2024**, matching volume 43(12), pages 1867–1883, and the original repository bibliography. The supplied website groups it under 2023; the formal journal volume/year is used here.
- Added **Spatial-RFM**, July 2026–December 2029, with the published Co-PI role. Updated **Basic Research Laboratory** to July 2026–June 2029, Co-PI, with its program and full topic. Matched AIMS's name/program to the supplied project record. Kept 8 ongoing and 2 completed projects, using only publicly supplied industry-project information.
- Added the September 30, 2026 IROS Best Paper Award with all three recipients. Retained the ICROS and KRoC researcher awards and the IROS 2025 workshop poster award.
- Added the September 4, 2026 KARI seminar. Filled the July 24 KAIST, July 30 ETRI, and August 19 KIRIA talk titles and removed their obsolete forthcoming labels. Retained all 23 public talks/tutorials from the personal-site records.
- Kept all five academic service roles; ICRA 2027 remains forthcoming. Existing teaching, advising, appointments, research profile, and group sections retain the recovered template's records.
- Added `scripts/build.py` to regenerate PDF and Markdown from the same TeX source and explicit revision date. `main.pdf` is committed; build intermediates are ignored. README includes the complete CV body, navigation, PDF access, sources, and build instructions.

Sources: the author-supplied APRL publications, projects, and personal-site text; [personal-site data](https://github.com/gisbi-kim/gisbi-kim.github.io/blob/master/static/data/profile-sections.json); [APRL publications](https://team-aprl.github.io/publications.html); [APRL projects](https://team-aprl.github.io/projects.html).

The KIRIA title `지도에서 기억으로: 장기 자율주행을 위한 인지와 추론의 연결` is rendered in English as “From Maps to Memory: Bridging Perception and Reasoning for Long-Term Autonomous Navigation.” A missing space in the supplied KAIST title (“Gapfor”) is repaired. These are editorial presentation changes, not changes to the event or its date.

Validation: XeLaTeX compilation with resolved page counts; all PDF fonts embedded; PDF text and every rendered page inspected; generated Markdown checked for publication numbering, section coverage, tables, and nested project lists.

## Historical sources

- **2026-03-25:** existing repository `main.tex`, `cv.cls`, and `ref.bib`, archived under `legacy/` at their original committed contents.
- **2026-07-23:** recovered `giseop_kim_cv.tex`, preserved as `legacy/giseop_kim_cv_20260723.tex`. This is the design baseline for the current revision.
