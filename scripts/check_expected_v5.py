#!/usr/bin/env python3
"""Read-only audit of manually authored v5 assumptions; never generates values."""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/paper/aamas2027/expected_experiment_matrix_v5_20261009'
TEX = ROOT / 'article/aamas2027/expected_experiment_matrix_v5_20261009/expected_experiment_matrix.tex'
d = json.loads((DOCS / 'expected_results.json').read_text())
checks = []
def check(name, ok, detail=None):
    checks.append({'name':name,'passed':bool(ok),'detail':detail})
def close(a,b):
    return math.isclose(a,b,abs_tol=1e-8)
p = {r['id']:r for r in d['primary']}
check('expected_not_empirical', not d['scientific_result'] and d['benchmark_runs']==0 and d['gpu_jobs']==0)
check('primary_exact_row_labels', [r['label'] for r in d['primary']]==['Future quality','Complete cost','Quality--cost utility','Assignment change','Judgment Brier','Update p95 / state bytes','Old-root forgetting','UNKNOWN / false attribution'])
for arm in ['rare','baseline']:
    check('primary_utility_'+arm,close(p['utility'][arm],p['future_quality'][arm]-.1*p['complete_cost'][arm]))
for row in d['primary']:
    if isinstance(row['rare'],list):
        check('paired_delta_'+row['id'], all(close(a-b,c) for a,b,c in zip(row['rare'],row['baseline'],row['delta'])))
    else:
        check('paired_delta_'+row['id'],close(row['rare']-row['baseline'],row['delta']))
        lo,hi=row['plausible_delta_range']; check('range_contains_center_'+row['id'],lo<=row['delta']<=hi)
qy=p['future_quality']['plausible_delta_range'];cc=p['complete_cost']['plausible_delta_range']
check('utility_range_conservative_joint',all(close(a,b) for a,b in zip(p['utility']['plausible_delta_range'],[qy[0]-.1*cc[1],qy[1]-.1*cc[0]])))
for section in ['factorial','locality','ablations']:
    for row in d[section]:
        check('utility_'+section+'_'+row.get('arm',row.get('evidence',''))+'_'+row.get('update',row.get('regime','')),close(row['utility'],row['quality']-.1*row['cost']))
f=d['factorial'];check('factorial_order',[(r['evidence'],r['update']) for r in f]==[('Masked','Off'),('Visible','Off'),('Masked','On'),('Visible','On')])
check('full_arm_cross_table',all(close(f[-1][k],p[pk]['rare']) for k,pk in [('quality','future_quality'),('cost','complete_cost'),('utility','utility'),('change','assignment_change')]))
fc=d['factorial_contrasts']
for k,out in [('quality','quality_interaction'),('cost','cost_interaction'),('utility','utility_interaction')]:
    check(out,close(f[3][k]-f[1][k]-f[2][k]+f[0][k],fc[out]))
check('interaction_joint_identity',close(fc['utility_interaction'],fc['quality_interaction']-.1*fc['cost_interaction']))
lo=f[3]['plausible_utility_range'][0]-f[1]['plausible_utility_range'][1]-f[2]['plausible_utility_range'][1]+f[0]['plausible_utility_range'][0]
hi=f[3]['plausible_utility_range'][1]-f[1]['plausible_utility_range'][0]-f[2]['plausible_utility_range'][0]+f[0]['plausible_utility_range'][1]
check('factorial_interval_from_marginals',all(close(a,b) for a,b in zip([lo,hi],fc['utility_interaction_range_from_marginals'])))
s=d['attribution_strata'];a=d['attribution_aggregate']
check('mutation_weights_sum',close(sum(r['weight'] for r in s),1))
check('mutation_complements',all(close(r['claim_coverage']+r['unknown'],1) for r in s))
check('mutation_risk_bounded_by_claims',all(0<=r['false_attribution_all']<=r['claim_coverage'] for r in s))
for key in ['claim_coverage','unknown','false_attribution_all']:
    check('mutation_aggregate_'+key,close(sum(r['weight']*r[key] for r in s),a[key]))
check('unknown_precision_weighting',close(sum(r['weight']*r['unknown']*r['unknown_precision'] for r in s)/a['unknown'],a['unknown_precision']))
check('conditional_risk_same_denominator',close(a['false_attribution_all']/a['claim_coverage'],a['false_attribution_claimed']))
check('primary_safety_from_weighted_mixture',p['unknown_fa']['rare']==[a['unknown'],a['false_attribution_all']])
check('shared_gate_equality',p['unknown_fa']['rare']==p['unknown_fa']['baseline'])
svc={(r['regime'],r['arm']):r for r in d['service']}
for arm,pk in [('RARE','rare'),('Contextual-trust-linear','baseline')]:
    row=svc[('Normal',arm)];check('service_cross_table_'+pk,p['update_p95_state'][pk]==[row['update_p95_ms'],row['state_bytes']])
check('latency_order',all(r['update_p50_ms']<=r['update_p95_ms'] for r in d['service'] if r['update_p95_ms'] is not None))
check('zero_online_model_calls',all(r['new_model_calls']==0 for r in d['service']))
check('high_load_loss',svc[('High load','RARE')]['payoff']<svc[('High load','Contextual-trust-linear')]['payoff'] and svc[('High load','RARE')]['update_p95_ms']>svc[('High load','Contextual-trust-linear')]['update_p95_ms'])
loc={(r['regime'],r['arm']):r for r in d['locality']}
check('sparse_loss',loc[('Sparse','RARE')]['utility']<loc[('Sparse','Pooled')]['utility'])
check('three_neighbor_max_share_feasible',all(r['max_share']>=1/3 for r in d['locality']))
check('frozen_prior_no_parameter_forgetting',d['drift'][0]['forgetting']==0)
check('same_gate_ablations_equal_safety',all(r['safety_common_corpus_fa']==a['false_attribution_all'] for r in d['ablations'] if r['arm']!='Without ownership gate'))
text=TEX.read_text()
check('three_displayed_tables',text.count('\\begin{table}[')==3)
check('nine_matrix_rows',re.findall(r'^(RQ\d-[IV]+) &',text,re.M)==['RQ1-I','RQ1-II','RQ2-I','RQ2-II','RQ2-III','RQ3-I','RQ3-II','RQ4-I','RQ4-II'])
check('no_result_placeholders',not re.search(r'\b(xx|TBD|NO-GO)\b|\\blank|\\na\b',text))
check('watermark', 'EXPECTED -- NOT OBSERVED' in text)
# Every displayed JSON result is hand typeset: check primary arithmetic; review covers source layout.
report={'artifact':'handwritten expected v5','checks':checks,'passed':all(c['passed'] for c in checks),'count':len(checks),'scope':'Arithmetic and table contract only; not empirical validity or forecast calibration','values_sha256':hashlib.sha256((DOCS/'expected_results.json').read_bytes()).hexdigest(),'tex_sha256':hashlib.sha256(TEX.read_bytes()).hexdigest()}
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
