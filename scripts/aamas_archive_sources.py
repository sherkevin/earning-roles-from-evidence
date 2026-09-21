"""Archive explicitly selected public conference sources with hashes.

No credentials, browser profiles, or project data are sent to these sources.
Run from the project root; optional arguments are URL and relative filename pairs.
"""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'references' / 'aamas'
DEFAULT = [
    ('https://warwick.ac.uk/fac/sci/dcs/aamas2027/', 'official/2027_home.html'),
    ('https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/', 'official/2027_main_track.html'),
    ('https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/', 'official/2027_instructions.html'),
    ('https://cyprusconferences.org/aamas2026/awards/', 'official/2026_awards.html'),
    ('https://www.ifaamas.org/Proceedings/aamas2026/forms/contents.htm', 'official/2026_contents.html'),
    ('https://www.ifaamas.org/Proceedings/aamas2025/forms/contents.htm', 'official/2025_contents.html'),
    ('https://www.ifaamas.org/Proceedings/aamas2024/forms/contents.htm', 'official/2024_contents.html'),
    ('https://warwick.ac.uk/fac/sci/dcs/aamas2027/flyer_aamas_2027.pdf', 'official/2027_flyer.pdf'),
]

def fetch(item):
    url, rel = item
    path = (DEST / rel).resolve()
    if not path.is_relative_to(DEST.resolve()):
        raise ValueError(rel)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.content
    if path.suffix.lower() == '.pdf' and not data.startswith(b'%PDF'):
        raise ValueError(f'Not a PDF: {url}')
    if path.suffix.lower() == '.zip' and not data.startswith(b'PK'):
        raise ValueError(f'Not a ZIP: {url}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    entry = dict(url=url, resolved_url=response.url, file=str(path.relative_to(ROOT)).replace('\\', '/'),
                 retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), status='downloaded')
    if path.suffix == '.html':
        soup = BeautifulSoup(data, 'html.parser')
        main = soup.find('main') or soup
        path.with_suffix('.txt').write_text(main.get_text('\n', strip=True), encoding='utf-8')
        links = [{'title': a.get_text(' ', strip=True), 'url': urljoin(response.url, a['href'])}
                 for a in soup.find_all('a', href=True)]
        path.with_suffix('.links.json').write_text(json.dumps(links, indent=2, ensure_ascii=False), encoding='utf-8')
    return entry

def main():
    args = sys.argv[1:]
    if len(args) % 2:
        raise SystemExit('Arguments must be URL filename pairs')
    jobs = list(zip(args[::2], args[1::2])) if args else DEFAULT
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = DEST / 'sources.json'
    entries = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    by_file = {e['file']: e for e in entries}
    failed = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            job = futures[future]
            try:
                entry = future.result()
                by_file[entry['file']] = entry
                print(f"OK {entry['bytes']} {entry['file']}")
            except Exception as exc:
                failed = True
                print(f'FAILED {job[0]}: {exc}')
    manifest.write_text(json.dumps(list(by_file.values()), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return int(failed)

if __name__ == '__main__':
    raise SystemExit(main())
