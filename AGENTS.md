# CV maintenance

For factual CV updates, read [.agents/skills/verify-cv/SKILL.md](.agents/skills/verify-cv/SKILL.md). Explicit user corrections take precedence over older website records; record any unresolved discrepancy rather than silently choosing one.

- Edit `main.tex`; regenerate `main.pdf` and `README.md` with `scripts/build.py`. Do not edit generated README content independently.
- Keep the PDF tracked. Keep historical source versions in Git history, without duplicate legacy folders.
- Run `python scripts/verify_cv.py` after content changes. For team changes or a request to verify current membership, also run `python scripts/verify_cv.py --live` and refresh the dated evidence only after reviewing the result.
- Verify changed PDF pages visually, check build warnings and link destinations, and run `git diff --check` before publishing. Mechanical documentation edits need no full PDF rebuild unless they affect the generated README.
- Preserve the user's approved labels, author order, publication identifiers, links, and section order. Publish only within the user's existing authorization; stage explicit files and verify the remote commit and PDF after a push.

The repository skill does not install packages, publish changes, or create scheduled checks automatically.
