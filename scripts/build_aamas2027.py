"""Build the isolated AAMAS draft and verify its official template and PDF surface."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

from check_aamas_documents import check as check_documents

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'article/aamas2027'
BUILD = SOURCE / 'build'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--submission', action='store_true', help='Require the scientific and metadata gates before building')
    parser.add_argument('--proposal', action='store_true', help='Build only the internal pre-results title/abstract proposal')
    args=parser.parse_args()
    if args.submission and args.proposal:
        raise SystemExit('SUBMISSION BLOCKED: the pre-results proposal is not a submission artifact')
    if args.submission:
        check_documents(check_gate=True)
        gate=json.loads((ROOT/'docs/paper/aamas2027/submission_gate.json').read_text(encoding='utf-8'))
        pending=[k for k,v in gate['requirements'].items() if v != 'verified']
        if pending:
            raise SystemExit('SUBMISSION BLOCKED: ' + ', '.join(pending))
        metadata=(SOURCE/'aamas_metadata.tex').read_text(encoding='utf-8')
        if 'INTERNAL' in metadata or 'Internal revision status.' in (SOURCE/'main.tex').read_text(encoding='utf-8'):
            raise SystemExit('SUBMISSION BLOCKED: internal draft markers or missing submission ID')
    BUILD.mkdir(parents=True,exist_ok=True)
    for name in ['aamas.cls','ACM-Reference-Format.bst','by.pdf']:
        official=ROOT/'references/aamas/template/official'/name
        if sha(official)!=sha(SOURCE/name):
            raise SystemExit('Official template file changed: '+name)
    env=dict(os.environ,LC_ALL='C',LANG='C')
    report={'official_template_files_unchanged':True,'submission_ready':False,'documents':[]}
    for stem in (['research_proposal'] if args.proposal else ['main','supplement']):
        console=BUILD/(stem+'.console.txt')
        with console.open('w',encoding='utf-8') as out:
            proc=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error','-outdir=build',stem+'.tex'],cwd=SOURCE,env=env,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:
            raise SystemExit(f'Build failed: {console}')
        log=(BUILD/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
        unresolved=bool(re.search(r'(?:Citation|Reference).*undefined|There were undefined (?:references|citations)',log))
        overfull=len(re.findall(r'Overfull \\[hv]box',log))
        pdf=BUILD/(stem+'.pdf')
        doc=fitz.open(pdf)
        text='\n'.join(p.get_text() for p in doc)
        if args.proposal and 'INTERNAL PRE-RESULTS PROPOSAL' not in text:
            raise SystemExit('Proposal is missing its visible internal status marker')
        refs=[i+1 for i,p in enumerate(doc) if re.search(r'(?m)^REFERENCES\s*$',p.get_text())]
        content_last_page=refs[0] if refs else len(doc)
        # Conservatively count the reference-start page as a content page.
        if stem=='main' and content_last_page>8:
            raise SystemExit('AAMAS eight-page content limit exceeded')
        if unresolved or overfull:
            raise SystemExit(f'PDF check failed: {stem}, unresolved={unresolved}, overfull={overfull}')
        if any(s in text for s in ['D:\\Codes','C:\\Users','/media/data3','shers@']):
            raise SystemExit('Local identity/path leakage detected')
        doc_report=dict(file=pdf.relative_to(ROOT).as_posix(),pages=len(doc),conservative_content_last_page=content_last_page,
                        unresolved_references=unresolved,overfull_boxes=overfull,sha256=sha(pdf),metadata=doc.metadata,
                        template_compatibility_warning='ifx' if 'was incomplete' in log else None)
        report['documents'].append(doc_report)
        print(f'{stem}: {len(doc)} pages; content <= {content_last_page}; citations resolved; no overfull boxes')
    report['artifact_type'] = 'internal_pre_results_proposal' if args.proposal else 'internal_revision'
    report_name = 'proposal_verification.json' if args.proposal else 'verification.json'
    (BUILD/report_name).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Verified anonymous internal draft; scientific submission gate remains closed.')

if __name__=='__main__':
    main()
