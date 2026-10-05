"""Check dated team evidence, CV counts/advising, and optionally the live public roster."""
import argparse
from collections import Counter
from datetime import date
from html import unescape
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NUMBERS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight'}
DEGREES = {'integrated': 'Integrated M.S./Ph.D.', 'phd': 'Ph.D.', 'ms': 'M.S.'}


def plain(text):
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', text)).split())


def public_roster(html):
    section = html.split('Current Lab Members', 1)[1].split('team-open-positions-heading', 1)[0]
    entries = []
    for attrs, card in re.findall(r'<article\b([^>]*)>(.*?)</article>', section, re.S):
        if 'team-member-placeholder-card' in attrs:
            continue
        if not re.search(r'\bid="team-member-[^"]+"', attrs):
            raise ValueError('Unexpected named-member card structure; review the source')
        name = plain(re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.S)[1])
        labels = [plain(p) for p in re.findall(r'<p\b[^>]*>(.*?)</p>', card, re.S)]
        if len(labels) != 1:
            raise ValueError(f'Unexpected role fields for {name}')
        label = labels[0]
        match = re.fullmatch(r'(Integrated MS/PhD student|PhD student|MS student|Postdoc) \((\d{4})([FS])-\)', label)
        if not match:
            raise ValueError(f'Unrecognized role/start term: {name}: {label}')
        roles = {'Integrated MS/PhD student': 'integrated', 'PhD student': 'phd', 'MS student': 'ms', 'Postdoc': 'postdoc'}
        entries.append({'name': name, 'category': roles[match[1]], 'start': ('Fall' if match[3] == 'F' else 'Spring') + ' ' + match[2]})
    if not entries:
        raise ValueError('No named members parsed; review the source')
    return sorted(entries, key=lambda entry: entry['name'])


def verify(snapshot, tex):
    date.fromisoformat(snapshot['reviewed_on'])
    entries = snapshot['members']
    names = [entry['name'] for entry in entries]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate roster names')
    counts = Counter(entry['category'] for entry in entries)
    if set(counts) - {'postdoc', 'phd', 'integrated', 'ms'}:
        raise ValueError('Unknown member categories')
    expected = (f"{NUMBERS[counts['postdoc']]} postdoctoral researcher, "
                f"{NUMBERS[counts['phd'] + counts['integrated']]} doctoral researchers "
                f"(including {NUMBERS[counts['integrated']]} integrated M.S./Ph.D. students), "
                f"and {NUMBERS[counts['ms']]} M.S. students")
    summary = tex.split('Current full-time group:', 1)[1].split('\n', 1)[0]
    if expected not in summary:
        raise ValueError('CV group summary disagrees with evidence: expected ' + expected)
    advising = tex.split(r'\section{Graduate Student Advising}', 1)[1].split(r'\end{tabularx}', 1)[0]
    actual = {}
    for line in advising.splitlines():
        match = re.match(r'\\talkbadge\{DGIST\}\s*&\s*\\textbf\{(?:\\href\{[^}]+\}\{([^}]+)\}|([^}]+))\}\s*&\s*([^&]+)&\s*(.*?)\s*\\\\', line)
        if match:
            name = match[1] or match[2]
            actual[name] = (match[3].strip(), match[4].strip())
    expected_students = {entry['name']: (DEGREES[entry['category']], entry['start'] + '--present')
                         for entry in entries if entry['category'] in DEGREES}
    if actual != expected_students:
        raise ValueError('Graduate advising names, degrees, or terms disagree with evidence')
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--live', action='store_true', help='Compare with the current public APRL team page')
    source.add_argument('--html', type=Path, help='Compare with a saved public team page')
    args = parser.parse_args()
    snapshot = json.loads((ROOT / 'verification/team-roster.json').read_text(encoding='utf-8'))
    counts = verify(snapshot, (ROOT / 'main.tex').read_text(encoding='utf-8'))
    print(f"CV matches evidence reviewed {snapshot['reviewed_on']}: {dict(counts)}; {sum(counts.values())} full-time members excluding the PI")
    if args.live or args.html:
        if args.live:
            request = Request(snapshot['source_url'], headers={'User-Agent': 'CV-roster-verification/1.0'})
            with urlopen(request, timeout=30) as response:
                html = response.read().decode('utf-8')
        else:
            html = args.html.read_text(encoding='utf-8')
        current = public_roster(html)
        if current != sorted(snapshot['members'], key=lambda entry: entry['name']):
            raise ValueError('Public roster differs from saved evidence; review source before updating:\n' + json.dumps(current, indent=2))
        print('Public named roster matches saved evidence; incoming/prospective placeholders excluded')


if __name__ == '__main__':
    main()
