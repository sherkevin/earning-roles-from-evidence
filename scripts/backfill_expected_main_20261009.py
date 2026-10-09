"""Build an explicitly expected-only PDF by replacing audited xx tokens only.

The empirical manuscript source is retained. This script authors no new expected
values and does not convert subjective planning ranges into confidence intervals.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/aamas2027/expected_backfill_20261009_v1'
SOURCE = ROOT / 'article/aamas2027'
VALUES = ROOT / 'docs/paper/aamas2027/expected_experiment_matrix_v5_20261009/expected_results.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUT.exists():
        raise SystemExit('Preserve the existing version; do not overwrite it.')
    OUT.mkdir(parents=True)
    src = OUT / 'source'
    src.mkdir()
    before = (SOURCE / 'main.tex').read_text()
    original_pdf = ROOT / 'artifacts/aamas2027/main.pdf'
    master = ROOT / 'artifacts/aamas2027/main_pdf_master.json'
    prior = json.loads(master.read_text())
    assert sha(original_pdf) == prior['master_sha256']
    assert sha(SOURCE / 'main.tex') == prior['source_inputs']['article/aamas2027/main.tex']
    for name in ['main.tex','aamas.cls','ACM-Reference-Format.bst','by.pdf','references.bib','aamas_metadata.tex']:
        shutil.copy2(SOURCE/name, src/name)
    shutil.copytree(SOURCE/'figures', src/'figures')
    shutil.copy2(original_pdf, OUT/'before_main.pdf')
    shutil.copy2(master, OUT/'before_main_pdf_master.json')
    shutil.copy2(SOURCE/'main.tex', OUT/'before_main.tex')
    shutil.copy2(VALUES, OUT/'expected_values_snapshot.json')

    # Each tuple is (line prefix, token replacements, provenance/restriction).
    # None deliberately retains xx because the corresponding value is not identified.
    mapping = [
      ('In human collaboration,', ['0.474','+0.008',None,'0.203',None,'68'],
       'primary.utility / primary.brier / primary.update_p95_state; no measured CI or unqualified FA'),
      ('RQ1-I &', ['(.225, .220, .203); (.637, .625, .584); (.073, .068, .055)'],
       'information: raw/terminal/RARE, respectively Brier/log loss/ECE'),
      ('RQ1-II &', [None], 'incremental prediction/transfer estimands unspecified in unchanged wording'),
      ('RQ2-I &', ['(.04, .12); (.532, .566); (.48, .54); (.30, .24)'],
       'factorial masked-off/visible-off: change/quality/adoption/rework'),
      ('RQ2-II &', ['(.455, .474); (1.15, 1.34)'],
       'factorial masked-on/visible-on: utility/cost'),
      ('RQ2-III &', ['(.474, .472); (.38, .40); (.08, .06)'],
       'locality stable: RARE/pooled utility/max share/min propensity'),
      ('RQ3-I &', [None], 'updater group not one named arm; full comparison not represented in unchanged cell'),
      ('RQ3-II &', ['(6.5, 9.0); (.025, .048); (1.4, .9)'],
       'drift with/without correction-replay: recovery/forgetting/backlog'),
      ('RQ4-I &', [None], 'attribution and no-op estimands not named sufficiently in unchanged cell'),
      ('RQ4-II &', [None], 'separate delay-handling intervention has no expected value'),
      ('Future quality &', ['0.608','0.588','+0.020'], 'primary.future_quality; difference only, no CI'),
      ('Complete cost &', ['1.34','1.22','+0.12'], 'primary.complete_cost; difference only'),
      ('Quality--cost utility &', ['0.474','0.466','+0.008'], 'primary.utility; difference only'),
      ('Assignment change &', ['0.20','0.16','+0.04'], 'primary.assignment_change; difference only'),
      ('Judgment Brier &', ['0.203','0.211','-0.008'], 'primary.brier; difference only'),
      ('Update p95 / state bytes &', ['68 / 36,864','52 / 28,672','+16 / +8,192'],
       'primary.update_p95_state: ms / bytes, unchanged header'),
      ('Old-root forgetting &', ['0.025','0.041','-0.016'], 'primary.forgetting; difference only'),
      ('UNKNOWN / false attribution &', [None,None,None],
       'unchanged table does not distinguish fixed-mutation UNKNOWN from outcome missingness'),
      ('\\paragraph{RQ1: information value.}',
       ['-0.022','-0.017','-0.008',None,None,None,'0.584','0.055',None,None,None,None],
       'information RARE-raw/terminal/context, log loss/ECE; no CIs/counts/missingness/service cost; transfer ambiguous'),
      ('\\paragraph{RQ2: assignment change.}', ['0.20','0.608','0.21','0.474',None],
       'factorial visible-on / primary: change/quality/rework/utility; no CI'),
      ('\\paragraph{RQ3: service behavior.}',
       [None,None,'37/68','1.0','36,864','0',None,None,None,None],
       'service Normal RARE: update p50/p95, backlog p95, state bytes, new model calls; other endpoints unspecified'),
      ('\\paragraph{RQ4: responsibility and drift.}',
       [None,None,None,None,'6.5','0.025',None,None],
       'drift RARE correction/replay only; mutation-wide unspecified rates and CI remain unfilled'),
      ('Masked & Off &', ['0.430','1.02'], 'factorial masked/off utility/cost; no CI supplied'),
      ('Visible & Off &', ['0.448','1.18'], 'factorial visible/off utility/cost; no CI supplied'),
      ('Masked & On &', ['0.455','1.15'], 'factorial masked/on utility/cost; no CI supplied'),
      ('Visible & On &', ['0.474','1.34'], 'factorial visible/on utility/cost; no CI supplied'),
    ]
    lookup = {prefix:(values,note) for prefix,values,note in mapping}
    records = []
    output = []
    seen = set()
    for lineno,line in enumerate(before.splitlines(keepends=True),1):
        matches = [prefix for prefix in lookup if line.startswith(prefix)]
        if not matches:
            assert not re.search(r'\bxx\b',line), (lineno,line)
            output.append(line)
            continue
        assert len(matches)==1
        prefix=matches[0]
        assert prefix not in seen
        seen.add(prefix)
        repls,note=lookup[prefix]
        tokens=list(re.finditer(r'\bxx\b',line))
        assert len(tokens)==len(repls),(prefix,len(tokens),len(repls))
        chunks=[];last=0
        for i,(match,value) in enumerate(zip(tokens,repls)):
            if value is not None:
                assert re.fullmatch(r'[0-9+.,;()/\- ]+',value),value
            chunks.extend([line[last:match.start()],value if value is not None else 'xx'])
            records.append({'line':lineno,'occurrence':i+1,'prefix':prefix,
                            'before':'xx','after':value if value is not None else 'xx',
                            'filled':value is not None,'provenance':note})
            last=match.end()
        chunks.append(line[last:]);output.append(''.join(chunks))
    assert seen==set(lookup)
    after=''.join(output)
    # Reconstruct the edited source from immutable original slices and explicit token map.
    original_spans=list(re.finditer(r'\bxx\b',before))
    assert len(original_spans)==len(records)
    expected=[];last=0
    for span,rec in zip(original_spans,records):
        expected.extend([before[last:span.start()],rec['after']]);last=span.end()
    expected.append(before[last:])
    assert after==''.join(expected), 'Text outside placeholder spans changed'
    (src/'main.tex').write_text(after)
    (OUT/'replacement_map.json').write_text(json.dumps(records,indent=2)+'\n')
    config={'created_at':datetime.datetime.now().astimezone().isoformat(),
            'kind':'expected_only_numeric_backfill_not_experiment','input_main_sha256':sha(original_pdf),
            'input_tex_sha256':sha(SOURCE/'main.tex'),'expected_values_sha256':sha(VALUES),
            'filled':sum(x['filled'] for x in records),'remaining':sum(not x['filled'] for x in records),
            'outside_xx_spans_unchanged':True,'literal_numeric_replacements_only':True,
            'scientific_result':False,'submission_ready':False,
            'empirical_source_unchanged':True,'watermark':'EXPECTED -- NOT OBSERVED'}
    env=dict(os.environ,LC_ALL='C',LANG='C',
       TEXMFDBS='/Users/jingwu/Library/texmf:/usr/local/texlive/2026basic/texmf-local:/usr/local/texlive/2026basic/texmf-config:/usr/local/texlive/2026basic/texmf-var:/usr/local/texlive/2026basic/texmf-dist',
       TEXMFHOME='!!/Users/jingwu/Library/texmf')
    command=['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','-file-line-error',
             '-outdir='+str(OUT),'main.tex']
    config['command']=command
    (OUT/'build_config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (OUT/'main.console.txt').open('w') as log:
        result=subprocess.run(command,cwd=src,env=env,stdout=log,stderr=subprocess.STDOUT)
    config['build_return_code']=result.returncode
    (OUT/'build_result.json').write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps(config,indent=2))
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
