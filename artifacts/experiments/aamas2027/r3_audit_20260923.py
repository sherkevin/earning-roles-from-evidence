"""Read-only independent R3 audit, no native-world or LLM invocation."""
import hashlib, json, datetime
from pathlib import Path
ROOT=Path('/Users/jingwu/work/earning-roles')
R3=ROOT/'artifacts/experiments/aamas2027/program_control_20260923'
R2=ROOT/'artifacts/experiments/aamas2027/handoff_effect_20260922'
def read(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(R3/'native_manifest.json'); s=read(R3/'summary.json')
assert [r['task_id'] for r in s['results']]==[t['task_id'] for t in m['tasks']]
assert all(digest(ROOT/p)==h for p,h in m['code_sha256'].items())
assert digest(R2/'native_summary.json')==m['r2_summary_sha256']
refs={r['task_id']:r for r in read(R2/'native_summary.json')['results'] if r['arm']=='semantic_guard'}
rows=[]
for row in s['results']:
 tid=row['task_id']; d=R3/'runs'/tid; ev=read(d/'evaluator_only.json')
 a={p.name:digest(p) for p in (d/'native/dbs').glob('*.jsonl')}
 b={p.name:digest(p) for p in (R2/'native'/(tid+'_semantic_guard')/'dbs').glob('*.jsonl')}
 count=len((d/'native/logs/api_calls.jsonl').read_text().splitlines())
 assert len(a)==12 and a==b
 assert ev['success'] and len(ev['passes'])==6 and not ev['failures']
 assert row['handoff']['selected']==refs[tid]['handoff']['selected']
 assert count==row['native_api_calls']==refs[tid]['native_api_calls']
 assert row['manifest_sha256']==digest(R3/'native_manifest.json')
 rows.append({'task':tid,'assertions':'6/6','database_files_equal':12,'api_calls':count,'selected_equal':True})
inv=read(R3/'source_inventory.json')
assert all(digest(R3/f['path'])==f['sha256'] for f in inv['files'])
receipt={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'VERIFIED_ON_MAC_PENDING_SHERVIN','decision':'PROGRAM_EXPLAINS_R2',
 'source_export_commit':'e873d70160086f49332ebf66211311cd8719578c',
 'manifest_sha256':digest(R3/'native_manifest.json'),'source_hashes_verified':len(inv['files']),
 'new_benchmark_calls':0,'new_model_calls':0,'rows':rows,
 'total_prior_native_api_calls':sum(r['api_calls'] for r in rows),
 'scope':'Independent recomputation from saved native states, official evaluator JSON and API logs. Not universal equivalence or an ASI reproduction.'}
out=ROOT/'artifacts/experiments/aamas2027/r3_audit_receipt_20260923.json'
out.write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps(receipt,indent=2))
