#!/usr/bin/env python3
"""Build a synchronized PDF and GitHub Markdown CV from main.tex."""
import argparse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def group(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != '{':
        raise ValueError(f'Expected brace near {text[pos:pos+60]!r}')
    start = pos + 1
    depth = 1
    pos += 1
    while depth:
        if pos >= len(text):
            raise ValueError('Unbalanced LaTeX braces')
        if text[pos] == '\\' and pos+1 < len(text) and text[pos+1] in '{}%&_$':
            pos += 2
            continue
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    return text[start:pos-1], pos


def inline(text):
    out = []
    pos = 0
    while pos < len(text):
        if text[pos] in '{}':
            pos += 1
            continue
        if text[pos] != '\\':
            out.append(text[pos])
            pos += 1
            continue
        match = re.match(r'\\([A-Za-z]+\*?|.)', text[pos:])
        cmd = match[1]
        pos += len(match[0])
        if cmd in ('%', '&', '_', '#', '$'):
            out.append(cmd)
        elif cmd == 'me':
            out.append('**Giseop KIM**')
        elif cmd == 'first':
            out.append('<sup>*</sup>')
        elif cmd == 'corr':
            out.append('<sup>†</sup>')
        elif cmd == 'leadpub':
            out.append('▶ ')
        elif cmd == 'dag':
            out.append('†')
        elif cmd == 'textbar':
            out.append('|')
            if text[pos:pos+2] == '{}':
                pos += 2
        elif cmd in ('textbf', 'textit', 'emph', 'textsuperscript'):
            value, pos = group(text, pos)
            value = inline(value)
            out.append(f'**{value}**' if cmd == 'textbf' else f'<sup>{value}</sup>' if cmd == 'textsuperscript' else f'*{value}*')
        elif cmd == 'href':
            url, pos = group(text, pos)
            label, pos = group(text, pos)
            out.append(f'[{inline(label)}]({url.replace(chr(92)+"&", "&").replace(chr(92)+"%", "%")})')
        elif cmd == 'input':
            filename, pos = group(text, pos)
            if filename != 'revision.tex':
                raise ValueError(f'Unexpected content input: {filename}')
            out.append((ROOT / filename).read_text().strip())
        elif cmd in ('quad', 'hfill', ' ', '\\'):
            out.append(' ')
            if cmd == '\\':
                bracket = re.match(r'\[[^\]]*\]', text[pos:])
                if bracket:
                    pos += len(bracket[0])
        elif cmd in ('small', 'footnotesize', 'vfill', 'noindent'):
            pass
        else:
            raise ValueError(f'Unsupported content command: \\{cmd}')
    return re.sub(r'\s+', ' ', ''.join(out).replace('~', ' ').replace('``', '“').replace("''", '”').replace('---', '—').replace('--', '–')).strip()


def cells(row):
    values = []
    start = depth = 0
    for i, char in enumerate(row):
        if char in '{}' and (i == 0 or row[i-1] != '\\'):
            depth += (char == '{') - (char == '}')
        if char == '&' and depth == 0 and (i == 0 or row[i-1] != '\\'):
            values.append(inline(row[start:i]))
            start = i+1
    values.append(inline(row[start:]))
    return values


def body_md(source):
    output = []
    depth = 0
    pub_number = 0
    current_section = ''
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        heading = re.match(r'\\(section|subsection)\{([^}]+)\}', line)
        if heading:
            if heading[1] == 'section':
                current_section = heading[2]
            output.append('\n' + ('## ' if heading[1] == 'section' else '### ') + heading[2] + '\n')
        elif line.startswith((r'\begin{tabularx}', r'\begin{longtable}')):
            rows = []
            while not lines[i].strip().startswith((r'\end{tabularx}', r'\end{longtable}')):
                row = lines[i].strip()
                i += 1
                if not row:
                    continue
                if row.startswith((r'\daterow', r'\cvrow')):
                    pos = row.index('{')
                    left, pos = group(row, pos)
                    right, pos = group(row, pos)
                    rows.append([inline(left), inline(right)])
                else:
                    row = re.sub(r'\\\\(?:\[[^\]]*\])?\s*$', '', row)
                    rows.append(cells(row))
            i += 1
            width = len(rows[0])
            if any(len(row) != width for row in rows):
                raise ValueError('Inconsistent table columns')
            headers = ['Date / period', 'Details'] if width == 2 else ['Name', 'Degree', 'Period']
            if current_section == 'Research Directions':
                headers = ['Direction', 'Focus']
            elif current_section == 'Teaching at DGIST':
                headers = ['Term', 'Code', 'Course']
            output.append('| ' + ' | '.join(headers) + ' |')
            output.append('| ' + ' | '.join('---' for _ in headers) + ' |')
            output.extend('| ' + ' | '.join(value.replace('|', '&#124;') for value in row) + ' |' for row in rows)
            output.append('')
        elif line.startswith(r'\begin{itemize}'):
            depth += 1
            if depth == 1:
                output.append('')
        elif line.startswith(r'\end{itemize}'):
            depth -= 1
            if depth < 0:
                raise ValueError('Unbalanced itemize environments')
            if depth == 0:
                output.append('')
        elif line.startswith((r'\begin{enumerate}', r'\end{enumerate}')):
            output.append('')
        elif line.startswith(r'\pub{'):
            value, pos = group(line, len(r'\pub'))
            if line[pos:].strip():
                raise ValueError('Unexpected text after publication')
            pub_number += 1
            output.append(f'{pub_number}. {inline(value)}')
        elif line.startswith(r'\item'):
            output.append('    ' * max(depth-1, 0) + '- ' + inline(line[len(r'\item'):]))
        elif line.startswith(r'\vfill'):
            pass
        else:
            output.append(inline(line))
            output.append('')
    if depth:
        raise ValueError('Unclosed itemize environment')
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(output)).strip() + '\n'


def make_readme(updated):
    text = re.sub(r'(?<!\\)%[^\n]*', '', (ROOT / 'main.tex').read_text(encoding='utf-8'))
    body = text.split(r'\begin{document}', 1)[1].split(r'\end{document}', 1)[0]
    start = body.index(r'\section{')
    profile = body[body.index(r'\textbf{Research mission.}'):start]
    sections = re.findall(r'\\section\{([^}]+)\}', body)
    toc = ' · '.join(f'[{name}](#{name.lower().replace(" ", "-")})' for name in sections)
    header = f'''<!-- Generated from main.tex by scripts/build.py. Edit the TeX source. -->
# Giseop KIM

**Assistant Professor · Principal Investigator**

Department of Robotics and Mechatronics Engineering, DGIST

Autonomy and Perceptual Robotics Lab (APRL)

[**Download the PDF CV →**](main.pdf) · [Personal Website](https://gisbi-kim.github.io/) · [APRL](https://aprl.dgist.ac.kr) · [Google Scholar](https://scholar.google.com/citations?user=9mKOLX8AAAAJ) · [GitHub](https://github.com/gisbi-kim) · [Email](mailto:gsk@dgist.ac.kr)

> **Last updated: {updated} (Asia/Seoul)**
>
> PDF and Markdown share one source and revision date. Publications include journal articles, regular conference papers, book chapters, and archival domestic papers. Preprints and non-archival papers are excluded; workshop awards and organizing roles remain in their respective sections.

{toc}

---

'''
    header += inline(profile).replace(' **Research profile.**', '\n\n**Research profile.**') + '\n\n'
    header += body_md(body[start:])
    return header + '''
---

## Build & synchronization

[main.tex](main.tex) is the active CV source. It preserves the black-and-white July 23, 2026 design recovered from the author's Dropbox CV folder and matching Google Drive PDF. Edit this source, then regenerate the PDF and README together:

```sh
python3 scripts/build.py
```

Requirements: Python 3.9+, XeLaTeX, latexmk, Bitstream Charter, and DejaVu Sans / Sans Mono. On Ubuntu / WSL:

```sh
sudo apt-get install texlive-xetex texlive-latex-extra texlive-fonts-recommended fonts-dejavu-core latexmk
python3 scripts/build.py
```

On Windows, install the same fonts and TeX tools, then use `python scripts/build.py`. An OpenType Charter font may be used when Bitstream Charter is unavailable. Add `--date YYYY-MM-DD` to reproduce a specific revision date. XeLaTeX runs until references and page counts settle; an unknown content command or unresolved reference stops the build.

Review `main.pdf` and `README.md`, then commit them together with any source changes. `revision.tex` carries their shared date. `main.pdf` is versioned; only build intermediates are ignored. README is generated and should not be edited independently. Website updates must first be incorporated into the TeX source; this build does not scrape or reverify biographical facts.

| File | Purpose |
| --- | --- |
| [main.pdf](main.pdf) | Published PDF CV |
| [main.tex](main.tex) | Active CV content and design |
| [revision.tex](revision.tex) | Shared revision date |
| [scripts/build.py](scripts/build.py) | PDF and Markdown generation |
| [CHANGELOG.md](CHANGELOG.md) | Source provenance and update record |

## Sources & versions

The current update uses the author's supplied APRL publications and project records, supplied personal-site records, and the public personal-site data. Sources: [APRL publications](https://team-aprl.github.io/publications.html), [APRL projects](https://team-aprl.github.io/projects.html), and [Giseop KIM](https://gisbi-kim.github.io/). A Korean KIRIA talk title is translated into English for this CV; the original title is recorded in the changelog. Review dates describe the CV revision, while future accepted publications retain “to appear.”

| Version | Status / change |
| --- | --- |
| [March 25, 2026](https://github.com/gisbi-kim/cv-giseopkim/blob/8d8762413870dde628d96ff8b99b268a4a610c3c/main.tex) | Historical `cv.cls` / BibTeX source, available in Git history |
| [July 23, 2026](https://github.com/gisbi-kim/cv-giseopkim/blob/25abd06c2aa670b5dc46db1c6d97ea9737518651/legacy/giseop_kim_cv_20260723.tex) | Recovered XeLaTeX design source in Git history, matching the author's [Drive CV archive](https://drive.google.com/drive/folders/1_0XFI8jedwYIr4QIIQ17cvAXhwOPRSrd) |
| [Current source](main.tex) | July design with updated archival publications, funded projects, talks, awards, and service; synchronized PDF and README |

Previous source snapshots are retained in Git history; the current tree contains only the active source and outputs.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', default=datetime.now(timezone(timedelta(hours=9))).date().isoformat())
    args = parser.parse_args()
    updated = date.fromisoformat(args.date).isoformat()
    (ROOT / 'revision.tex').write_text(updated + '\n', encoding='utf-8')
    subprocess.run(['latexmk', '-g', '-xelatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'], cwd=ROOT, check=True)
    log = (ROOT / 'main.log').read_text(encoding='utf-8', errors='replace')
    if re.search(r'undefined references|Reference .* undefined|Missing character:', log):
        raise ValueError('Unresolved references or missing glyphs in PDF')
    content = make_readme(updated)
    (ROOT / 'README.md').write_text(content, encoding='utf-8')
    print(f'Synchronized main.pdf and README.md: {updated}')


if __name__ == '__main__':
    main()
