"""Exact conditional probability calculations, not generated experiment data."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/paper/aamas2027/guides/v2_20261008/joint_model_spec.json'
OUT = ROOT / 'artifacts/aamas2027/guide_experiment_matrix_v2_20261008'
TEX = ROOT / 'article/aamas2027/guides/v2_20261008/guide_experiment_matrix.tex'
METRICS = ['Quality', 'Brier', 'Sample ECE', 'Cost', 'Utility']


def binom(n, p):
    return np.array([math.comb(n, k)*p**k*(1-p)**(n-k) for k in range(n+1)])


def quantiles(values, weights):
    ix = np.argsort(values)
    cdf = np.cumsum(weights[ix]); cdf /= cdf[-1]
    return [float(values[ix[min(np.searchsorted(cdf, q), len(ix)-1)]]) for q in (.025,.5,.975)]


def calculate_scenario(s, par):
    n=par['episodes_per_conditional_stream'];d=par['candidate_quality_gap_half_d']
    gamma=par['repair_cost_gamma'];lam=par['utility_weight_lambda'];c0=1+.5*gamma
    amplitude=par['normalized_cost_jitter']['values'][1]
    qh=.5+d;ql=.5-d;r=(1+s['kappa'])/2
    if s['forecast']=='constant_half': ph=pl=.5
    else: ph=qh+s['bias_e'];pl=ql+s['bias_e']
    assert 0 <= ph <= 1 and 0 <= pl <= 1
    xs=[];ws=[];route=binom(n,r)
    for nh in range(n+1):
        nl=n-nh;hi=binom(nh,qh);lo=binom(nl,ql)
        for sh in range(nh+1):
            for sl in range(nl+1):
                y=(sh+sl)/n
                loss=(nh*ph*ph+sh*(1-2*ph)+nl*pl*pl+sl*(1-2*pl))/n
                # Same forecast bin merges both types for a constant .5 forecast.
                ece=abs(ph-y) if ph==pl else (abs(nh*ph-sh)+abs(nl*pl-sl))/n
                c=(1+s['overhead_h']+gamma*(1-y))/c0
                xs.append([y,loss,ece,c,y-lam*c]);ws.append(route[nh]*hi[sh]*lo[sl])
    x=np.array(xs);w=np.array(ws);assert abs(w.sum()-1)<1e-10;w/=w.sum()
    mean=w@x;centered=x-mean
    cov=(centered.T*w)@centered
    noise_direction=np.array([0,0,0,1,-lam])
    cov+=amplitude**2/n*np.outer(noise_direction,noise_direction)
    assert np.linalg.eigvalsh(cov).min()>-1e-10
    std=np.sqrt(np.maximum(np.diag(cov),0))
    marginals={}
    for j,k in enumerate(METRICS):
        values=x[:,j];weights=w
        if j in (3,4):
            jitter=amplitude*(2*np.arange(n+1)/n-1)
            if j==4:jitter=-lam*jitter
            values=(values[:,None]+jitter[None,:]).ravel()
            weights=(w[:,None]*binom(n,.5)[None,:]).ravel()
        qs=quantiles(values,weights)
        coverage=float(weights[(values >= qs[0]-1e-12) & (values <= qs[2]+1e-12)].sum())
        assert coverage >= .95-1e-10
        marginals[k]={'mean':float(mean[j]),'sd':float(std[j]),'conditional_central_95_prediction_interval':qs[::2], 'median':qs[1], 'conditional_interval_probability_mass':coverage}
    quality=r*qh+(1-r)*ql
    brier=r*(qh*(1-qh)+(ph-qh)**2)+(1-r)*(ql*(1-ql)+(pl-ql)**2)
    population_ece=abs(ph-quality) if ph==pl else r*abs(ph-qh)+(1-r)*abs(pl-ql)
    assert abs(quality-mean[0])<1e-10 and abs(brier-mean[1])<1e-10
    assert mean[2]+1e-10 >= population_ece
    assert abs(cov[0,0]-quality*(1-quality)/n)<1e-10
    assert abs(mean[4]-(mean[0]-lam*mean[3]))<1e-10
    corr=[]
    for i in range(5):
        corr.append([float(cov[i,j]/(std[i]*std[j])) if std[i]>1e-9 and std[j]>1e-9 else None for j in range(5)])
    return dict(s, population_quality=quality,population_brier=brier,population_ece=population_ece,
                expected_cost=float(mean[3]),expected_utility=float(mean[4]),
                forecast_values=[pl,ph],metric_order=METRICS,marginals=marginals,
                conditional_stream_covariance=cov.tolist(),conditional_stream_correlation=corr,
                confidence_scope='Exact conditional on unestimated model inputs and iid frozen-policy episodes; not an empirical method forecast.')


def f(v,n=3):return f'{v:.{n}f}'


def main():
    spec=json.loads(SPEC.read_text());par=spec['parameters'];scenarios=[calculate_scenario(s,par) for s in spec['scenarios']]
    by={s['id']:s for s in scenarios};pair=spec['paired_sensitivity'];left=by[pair['left_scenario']];right=by[pair['right_scenario']]
    d=par['candidate_quality_gap_half_d'];gamma=par['repair_cost_gamma'];lam=par['utility_weight_lambda'];c0=1+.5*gamma;alpha=1+lam*gamma/c0
    n=par['episodes_per_conditional_stream'];roots=par['root_count_sensitivity_only'];per_root=par['streams_per_root_sensitivity_only']
    mismatch=abs(right['kappa']-left['kappa'])/2;dq=right['population_quality']-left['population_quality'];du=right['expected_utility']-left['expected_utility']
    amp=par['normalized_cost_jitter']['values'][1];jitter_variance=2*lam**2*amp**2*(1-pair['cost_jitter_correlation'])
    coupling=[]
    for u in pair['joint_candidate_success_u']:
        assert max(0,(.5+d)+(.5-d)-1)-1e-10 <= u <= .5-d+1e-10
        vy=mismatch*(1-2*u)-dq*dq;vu=alpha*alpha*vy+jitter_variance
        coupling.append({'u':u,'episode_delta_quality_variance':vy,'episode_delta_utility_variance':vu,'iid_stream_delta_utility_sd':math.sqrt(vu/n)})
    center=next(v for v in coupling if abs(v['u']-.21)<1e-10)
    sensitivity=[]
    for rho in pair['paired_episode_icc_rho']:
        de=1+(n-1)*rho;streamvar=center['episode_delta_utility_variance']*de/n
        for root_sd in pair['root_effect_sd']:
            se=math.sqrt(root_sd**2/roots+streamvar/(roots*per_root))
            sensitivity.append({'paired_difference_icc':rho,'assumed_root_sd':root_sd,'design_effect':de,'stream_sd':math.sqrt(streamvar),'mean_difference_se':se,'conditional_normal_95_planning_band':[du-1.96*se,du+1.96*se]})
    raw=ROOT/spec['source_summary'];observed=json.loads(raw.read_text());anchors=[]
    for r in observed['results']:
        anchors.append({'method':r['arm'],'updates':r['update']['updates'],'single_update_ms':r['update'].get('latency_seconds',0)*1000 if r['update']['updates'] else None,'serialized_state_bytes':r['cost']['state_bytes'],'post_update_executed':False})
    data={'kind':'exact_conditional_joint_law_derivation','not_observed':True,'empirical_forecast':False,'new_api_calls':0,'gpu_jobs':0,
          'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'spec_sha256':hashlib.sha256(SPEC.read_bytes()).hexdigest(),
          'scenario_results':scenarios,'paired_comparison':{'mismatch_probability':mismatch,'delta_quality':dq,'delta_utility':du,'cost_coupling_assumption':'independent Rademacher jitters in main sensitivity','coupling_sensitivity':coupling,'root_correlation_sensitivity':sensitivity},
          'observed_diagnostic_anchors':anchors,'real_method_parameters_identified':False,
          'required_routing_interaction_for_utility_target_0_02_if_overhead_interaction_zero':.02/(alpha*d)}
    replacements={
        '@@SCENARIO_ROWS@@':'\n'.join(f"{s['id']} & {f(s['population_quality'])} & {f(s['population_brier'],4)} & {f(s['population_ece'])} & {f(s['expected_cost'])} & {f(s['expected_utility'])}\\\\" for s in scenarios),
        '@@ERROR_ROWS@@':'\n'.join(f"{k} & {f(v['mean'],4)} & {f(v['sd'],4)} & [{f(v['conditional_central_95_prediction_interval'][0],4)}, {f(v['conditional_central_95_prediction_interval'][1],4)}] & {f(100*v['conditional_interval_probability_mass'],1)}\\\\" for k,v in by['S3']['marginals'].items()),
        '@@CORR_ROWS@@':'\n'.join(k+' & '+' & '.join('--' if v is None else f(v,4) for v in row)+r'\\' for k,row in zip(['Q','Brier','ECE','Cost','Utility'],by['S3']['conditional_stream_correlation'])),
        '@@COUPLING_ROWS@@':'\n'.join(f"{f(v['u'],2)} & {f(v['episode_delta_quality_variance'],4)} & {f(v['iid_stream_delta_utility_sd'],4)}\\\\" for v in coupling),
        '@@SENSITIVITY_ROWS@@':'\n'.join(f"{f(v['paired_difference_icc'],2)} & {f(v['assumed_root_sd'],2)} & {f(v['stream_sd'],4)} & [{f(v['conditional_normal_95_planning_band'][0])}, {f(v['conditional_normal_95_planning_band'][1])}]\\\\" for v in sensitivity),
        '@@DU@@':f(du,4),'@@DQ@@':f(dq,3),'@@INTERACTION_K@@':f(data['required_routing_interaction_for_utility_target_0_02_if_overhead_interaction_zero'],5)}
    text=(ROOT/'article/aamas2027/guides/guide_v2_template.tex').read_text()
    for k,v in replacements.items():text=text.replace(k,v)
    assert '@@' not in text
    OUT.mkdir(parents=True,exist_ok=True);TEX.parent.mkdir(parents=True,exist_ok=True)
    (OUT/'joint_distribution_calculations.json').write_text(json.dumps(data,indent=2)+'\n');(OUT/'joint_model_spec.json').write_bytes(SPEC.read_bytes());TEX.write_text(text)
    print('Exact probability mass, covariance PSD, means, finite-N errors and sensitivities checked. No empirical forecast or new experiment.')
    print(TEX)


if __name__=='__main__':main()
