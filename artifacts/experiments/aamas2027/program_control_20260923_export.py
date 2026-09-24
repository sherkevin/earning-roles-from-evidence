"""Export only completed R3 evidence; preserve active Git index and branch."""
import json, os, subprocess, urllib.request
from pathlib import Path
ROOT = Path('/Users/jingwu/work/earning-roles')
REL = 'artifacts/experiments/aamas2027/program_control_20260923'
API = 'https://api.github.com/repos/sherkevin/earning-roles-from-evidence'
REF = 'heads/iteration/r3-program-control-20260923'
env = os.environ.copy(); env['GIT_TERMINAL_PROMPT'] = '0'
cred = subprocess.run(['git','credential','fill'], cwd=ROOT, env=env,
    input='protocol=https\nhost=github.com\n\n', text=True,
    capture_output=True, timeout=10, check=True)
fields = dict(line.split('=',1) for line in cred.stdout.splitlines() if '=' in line)
token = fields['password']
def request(path, body=None, method=None):
    req = urllib.request.Request(API+path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
                 'Content-Type':'application/json','User-Agent':'R3-evidence-export'}, method=method)
    with urllib.request.urlopen(req,timeout=30) as res: return json.load(res)
old = request('/git/ref/'+REF)['object']['sha']
if old != '102de990ac9087a9b80f16a38bfbf06e514b0fa2':
    raise RuntimeError('R3 branch advanced; do not overwrite')
base_tree = request('/git/commits/'+old)['tree']['sha']
files = [p for p in sorted((ROOT/REL).rglob('*')) if p.is_file()]
files.append(ROOT/'scripts/r3_program_control.py')
entries = [{'path':str(p.relative_to(ROOT)), 'mode':'100644', 'type':'blob',
            'content':p.read_bytes().decode('utf-8')} for p in files]
assert all(token not in entry['content'] for entry in entries)
tree = request('/git/trees', {'base_tree':base_tree,'tree':entries})['sha']
commit = request('/git/commits', {'message':'R3: archive completed native control and exact evidence',
    'tree':tree,'parents':[old]})['sha']
# Never force a branch update; concurrent advances fail instead of being discarded.
request('/git/refs/'+REF, {'sha':commit,'force':False}, method='PATCH')
verified = request('/git/ref/'+REF)['object']['sha']
receipt = {'commit':commit,'verified':verified==commit,'file_count':len(files),
           'branch':REF,'transport':'GitHub REST; existing OS credential; not stored'}
print(json.dumps(receipt))
(ROOT/'artifacts/experiments/aamas2027/r3_export_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
