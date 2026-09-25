"""Diagnostics for why the associative smoke is nearly uniform.

This does not change the method. It replays the same hidden worlds and logs
oracle headroom, score spread/entropy, kernel similarity, and post-switch
behavior using selected-only arrivals.
"""
from __future__ import annotations
import json, math, platform, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.selected_only_rls import make_world
from experiments.linear_associative_smoke import AssociativeKernelUpdater


def main():
    seeds=[20260925+i*17 for i in range(5)]; horizon=100
    out=ROOT/'experiments'/'logs'; out.mkdir(parents=True,exist_ok=True)
    eid='linear_associative_diagnostics_20260925'
    rows=[]; summaries=[]
    for seed in seeds:
        w=make_world(seed,horizon=horizon); d=int(w['feature_dim'])
        a=AssociativeKernelUpdater(feature_dim=d,forgetting=.985,ridge=.1,prior=.5,max_weight=8.,uncertainty_scale=.30,temperature=1.0)
        pending=defaultdict(list)
        selected=[]; score_ranges=[]; entropies=[]; kernel_spreads=[]; rank_acc=[]
        oracle=[]; static_expected=[]; assoc_expected=[]; post_switch=[]
        for t,e in enumerate(w['events']):
            arrivals=pending.pop(t,[])
            if arrivals: a.update_batch(t,arrivals)
            menu=e['menu']; feats=e['features']
            probs,_=a.score({c:feats[c] for c in menu})
            scores=[]
            # recover pre-softmax means by scoring with same state directly
            for c in menu:
                q=a.phi(feats[c]); mass=float(q@a.Z); scores.append(float(np.clip(q@a.S/max(mass,1e-12),0,1)))
            truth=np.asarray([e['truth'][c] for c in menu],float)
            # ranking ties count as 1/k among tied maxima
            best_pred=np.flatnonzero(np.isclose(scores,max(scores),atol=1e-12)); best_true=np.flatnonzero(np.isclose(truth,max(truth),atol=1e-12))
            rank_acc.append(float(len(set(best_pred)&set(best_true))/max(1,len(best_pred))))
            score_ranges.append(float(max(scores)-min(scores)))
            entropies.append(float(-np.sum(probs*np.log(np.maximum(probs,1e-12)))))
            # candidate-specific kernel mass spread for this current menu
            qmat=np.asarray([a.phi(feats[c]) for c in menu]);
            # pairwise similarity among menu candidates; off-diagonal spread
            K=qmat@qmat.T; off=K[~np.eye(len(menu),dtype=bool)]
            kernel_spreads.append(float(np.std(off)))
            oracle.append(float(max(truth))); static_expected.append(float(np.mean(truth)))
            idx=int(np.random.default_rng(seed+100003).choice(len(menu),p=probs)) if False else 0
            # Use deterministic replay-compatible sampling via a persistent RNG below is not needed for diagnostic expectation.
            assoc_expected.append(float(np.dot(probs,truth)))
            # selected-only update: use action drawn by same policy RNG
            if 'rng' not in locals(): rng=np.random.default_rng(seed+100003)
            idx=int(rng.choice(len(menu),p=probs)); cid=menu[idx]
            pending[t+int(e['delay'])].append({'feedback_id':f'assoc:{seed}:{t}','feature':list(feats[cid]),'label':int(e['labels'][cid]),'propensity':float(probs[idx]),'source_t':t,'candidate_id':cid,'delay':int(e['delay'])})
            if int(e['regime'])>0: post_switch.append(float(np.dot(probs,truth)))
            rows.append({'seed':seed,'t':t,'score_range':score_ranges[-1],'entropy':entropies[-1], 'kernel_offdiag_std':kernel_spreads[-1], 'oracle_expected':oracle[-1], 'uniform_expected':static_expected[-1], 'assoc_policy_expected':assoc_expected[-1], 'truth_best':float(max(truth)), 'rank_hit_fraction':rank_acc[-1], 'regime':int(e['regime'])})
        for t in sorted(pending): a.update_batch(t,pending[t])
        summaries.append({'seed':seed,'mean_oracle_best':float(np.mean(oracle)),'mean_uniform_menu':float(np.mean(static_expected)), 'mean_assoc_policy_expected':float(np.mean(assoc_expected)), 'headroom_oracle_minus_uniform':float(np.mean(oracle)-np.mean(static_expected)), 'mean_score_range':float(np.mean(score_ranges)), 'p95_score_range':float(np.percentile(score_ranges,95)), 'mean_entropy':float(np.mean(entropies)), 'uniform_entropy':float(math.log(4)), 'mean_kernel_offdiag_std':float(np.mean(kernel_spreads)), 'rank_hit_fraction':float(np.mean(rank_acc)), 'post_switch_assoc_policy_expected':float(np.mean(post_switch)) if post_switch else None})
    try: commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    except Exception: commit='unknown'
    payload={'experiment_id':eid,'config':{'seeds':seeds,'horizon':horizon,'world':'selected_only_rls.make_world','selected_only':True,'truth_evaluation_only':True,'python':platform.python_version(),'numpy':np.__version__,'git_commit':commit},'per_seed':summaries,'raw_file':str(out/f'{eid}_raw.jsonl'),'finished_at_utc':datetime.now(timezone.utc).isoformat()}
    (out/f'{eid}_config.json').write_text(json.dumps(payload['config'],indent=2)+'\n')
    with (out/f'{eid}_raw.jsonl').open('w') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    # aggregate over seeds
    keys=[k for k in summaries[0] if k!='seed']
    payload['aggregate']={k:{'mean':float(np.mean([s[k] for s in summaries if s[k] is not None])),'sd':float(np.std([s[k] for s in summaries if s[k] is not None],ddof=1))} for k in keys}
    (out/f'{eid}_results.json').write_text(json.dumps(payload,indent=2)+'\n')
    a=payload['aggregate']
    md=['# Associative failure diagnostics (2026-09-25)','', 'This replay quantifies why the associative smoke was nearly uniform. It uses the same five hidden worlds and selected-only feedback; truth fields are evaluation-only.','', '| quantity | mean ± sd |', '|---|---:|']
    for k in ['mean_oracle_best','mean_uniform_menu','mean_assoc_policy_expected','headroom_oracle_minus_uniform','mean_score_range','p95_score_range','mean_entropy','mean_kernel_offdiag_std','rank_hit_fraction','post_switch_assoc_policy_expected']:
        x=a[k]; md.append(f"| {k} | {x['mean']:.6f} ± {x['sd']:.6f} |" if x['mean'] is not None else f'| {k} | n/a |')
    md += ['', 'Interpretation:', '', '- The oracle headroom shows that the menu contains better choices than uniform selection, so the environment is not intrinsically unlearnable.', '- Associative scores have a small range and entropy close to $\\log 4$, so the policy remains nearly uniform.', '- The split non-negative map yields a dot-product kernel and a scalar kernel smoother; it does not recover the signed linear direction or cross-coordinate interactions used by the world.', '- The shared context coordinates and intercept are present in every candidate in a menu, so they contribute common kernel mass and shrink candidate-specific differences.', '- Random regime switches and only 100 selected labels leave little data per regime; forgetting mixes old regimes while the fixed feature map cannot relearn a new representation.', '- This is a mechanism diagnosis, not a claim that every associative kernel would fail.']
    (out/f'{eid}_summary.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(payload,indent=2))

if __name__=='__main__': main()
