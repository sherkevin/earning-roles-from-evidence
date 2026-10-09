"""Derive a watermarked planning document; never writes paper results or main.pdf."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/paper/aamas2027/guides/v1_20261008/target_spec.json'
OUT = ROOT / 'artifacts/aamas2027/guide_experiment_matrix_v1_20261008'
TEX = ROOT / 'article/aamas2027/guides/v1_20261008/guide_experiment_matrix.tex'


def fmt(x, digits=3):
    return f'{x:.{digits}f}'


def main():
    spec = json.loads(SPEC.read_text())
    raw = ROOT / spec['source_summary']
    observed = json.loads(raw.read_text())
    weight = spec['utility_cost_weight']
    q = spec['brier_two_bins']['true_rates']
    w = spec['brier_two_bins']['weights']
    n = spec['planned_streams_per_arm']
    main_rows, ablation_rows, stress_rows, service_rows, scenario_rows = [], [], [], [], []
    calculations = {'artifact_type': 'prospective_guide_calculations', 'not_observed': True,
                    'not_preregistered': True, 'main': [], 'ablations': [], 'stress': [],
                    'scenarios': [], 'new_api_calls': 0, 'gpu_jobs': 0}
    base_quality = spec['artifact_rows'][0]['quality']
    for r in spec['artifact_rows']:
        p = r['predictions']
        brier = sum(wi * (qi * (1-qi) + (pi-qi)**2) for wi, qi, pi in zip(w, q, p))
        # Fixed forecast bins [0,.5), [.5,1]. A constant .5 forecast has one occupied bin.
        calibration = 0.0
        for upper in (False, True):
            ix = [i for i, pi in enumerate(p) if (pi >= .5) == upper]
            mass = sum(w[i] for i in ix)
            if mass:
                calibration += abs(sum(w[i] * (p[i]-q[i]) for i in ix))
        if abs(calibration) < 1e-12:
            calibration = 0.0
        u = r['quality'] - weight * r['normalized_cost']
        assert 0 <= brier <= 1 and 0 <= calibration <= 1
        assert abs(r['quality']-base_quality) <= r['assignment_change'] + 1e-12
        label = r['method'] + (r'$^{\dagger}$' if r.get('conditional_proxy') else '')
        main_rows.append(f"{label} & {fmt(brier)} & {fmt(calibration)} & {fmt(u)} & {fmt(r['assignment_change'],2)} & {fmt(r['normalized_cost'],2)} & {n}\\\\")
        calculations['main'].append(dict(r, brier=brier, calibration=calibration, utility=u))
    for r in spec['ablation_rows']:
        if r.get('invalid_under_current_feedback_contract'):
            ablation_rows.append(r['variant'] + r' & \multicolumn{4}{l}{\textit{N/A: feedback contract not defined}}\\')
            calculations['ablations'].append(r)
            continue
        u = r['quality'] - weight * r['normalized_cost']
        assert abs(r['quality']-base_quality) <= r['assignment_change'] + 1e-12
        ablation_rows.append(f"{r['variant']} & {fmt(u)} & {fmt(r['assignment_change'],2)} & {fmt(r['false_attribution'])} & {fmt(r['normalized_cost'],2)}\\\\")
        calculations['ablations'].append(dict(r, utility=u))
    for r in spec['stress_rows']:
        stress_rows.append(r['variant'] + ' & ' + ' & '.join(fmt(v) for v in r['false_attribution_rates']) + r'\\')
        calculations['stress'].append(dict(r, equal_weight_rate=sum(r['false_attribution_rates'])/4))
    no_gate = next(r for r in calculations['ablations'] if r['variant']=='No ownership gate')
    assert math.isclose(no_gate['false_attribution'], calculations['stress'][1]['equal_weight_rate'])
    for r in spec['peerselect_rows']:
        cap = r['update_p95_budget_ms']
        update = '--' if cap is None else r'$\leq$' + str(cap)
        backlog = str(r['backlog_envelope']) if cap is None else r'$\leq$' + str(r['backlog_envelope'])
        recovery = r'$>50$' if r['recovery_target_steps'] is None else r'$\leq$' + str(r['recovery_target_steps'])
        label = r['method'] + (r'$^{\dagger}$' if r.get('conditional_proxy') else '')
        service_rows.append(f"{label} & {update} & {backlog} & $\\leq${r['state_budget_kib']} & {fmt(r['normalized_payoff'],2)} & $\\leq${fmt(r['forgetting_budget'],2)} & {recovery} & {n}\\\\")
    for r in spec['sensitivity_scenarios']:
        ru = r['rare_quality'] - weight*r['rare_cost']
        cu = r['control_quality'] - weight*r['control_cost']
        scenario_rows.append(f"{r['name']} & {fmt(r['rare_quality'],2)} & {fmt(r['rare_cost'],2)} & {fmt(ru)} & {fmt(cu)} & {fmt(ru-cu)}\\\\")
        calculations['scenarios'].append(dict(r, rare_utility=ru, control_utility=cu, difference=ru-cu))
    a = {r['variant']: r for r in calculations['ablations']}
    u00=a['Neither evidence nor credit']['utility'];u10=a['No delayed credit']['utility']
    u01=a['No public evidence']['utility'];u11=a['Full RARE']['utility']
    interaction=u11-u10-u01+u00
    assert math.isclose(interaction,.020)
    assert math.isclose(u11-u00,(u10-u00)+(u01-u00)+interaction)
    ps=spec['peerselect_assumptions']
    memory_bytes=ps['fixed_bytes_allowance']+ps['head_float64_vectors']*ps['cached_feature_dimension']*8+ps['retained_event_cap']*ps['event_bytes_allowance']
    assert memory_bytes/1024 <= 64
    burst_service=ps['burst_events']*ps['service_envelope_ms']
    assert burst_service < ps['burst_period_ms']
    target_count=n*len(spec['artifact_rows'])*spec['target_assignments_per_stream']
    # Planning skeleton: 3 calls per fresh target + 3 initial-source calls per arm/stream.
    request_count=3*target_count+3*n*len(spec['artifact_rows'])
    usage_input=usage_output=0; api_seconds=0.0
    # Source objects repeat in each arm; count provider receipts by stage directory.
    receipts={}
    for r in observed['results']:
        for phase in ('source','target'):
            for k,v in r[phase].items():
                if k.endswith('_api'):
                    key=(phase, v['directory']) if phase=='source' else (r['arm'],v['directory'])
                    receipts[key]=v
    assert len(receipts)==observed['real_api_calls']
    for v in receipts.values():
        usage_input+=v['usage']['input_tokens'];usage_output+=v['usage']['output_tokens'];api_seconds+=v['elapsed_seconds']
    token_mean=(usage_input+usage_output)/len(receipts)
    projected_tokens=request_count*token_mean
    delta=calculations['scenarios'][2]['difference']
    sd=spec['paired_stream_sd_assumption']
    normal_n=math.ceil(((1.96+.8416)*sd/delta)**2)
    half_width=2.1098*sd/math.sqrt(n) # illustrative t(17) planning critical value
    calculations.update({'utility_interaction':interaction,'memory_budget_calculation_bytes':memory_bytes,
        'burst_service_ms':burst_service,'requests_lower_bound_skeleton':request_count,
        'future_target_assignments':target_count,'observed_source_calls':len(receipts),
        'observed_input_tokens':usage_input,'observed_output_tokens':usage_output,
        'observed_summed_api_seconds':api_seconds,'source_mean_tokens_per_call':token_mean,
        'projected_token_skeleton':projected_tokens,'projected_api_hours_skeleton':request_count*api_seconds/len(receipts)/3600,
        'normal_approx_stream_count':normal_n,'assumed_sd_planning_half_width':half_width,
        'independent_zero_error_upper_95_at_300':1-.05**(1/300),
        'source_summary_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
        'target_spec_sha256':hashlib.sha256(SPEC.read_bytes()).hexdigest()})
    replacements={
        '@@MAIN_ROWS@@':'\n'.join(main_rows),'@@ABLATION_ROWS@@':'\n'.join(ablation_rows),
        '@@STRESS_ROWS@@':'\n'.join(stress_rows),'@@SERVICE_ROWS@@':'\n'.join(service_rows),
        '@@SCENARIO_ROWS@@':'\n'.join(scenario_rows),'@@REQUESTS@@':f'{request_count:,}',
        '@@TARGETS@@':f'{target_count:,}','@@TOKENS@@':f'{projected_tokens/1e6:.2f}',
        '@@APIHOURS@@':f"{calculations['projected_api_hours_skeleton']:.1f}",
        '@@POWER_N@@':str(normal_n),'@@HALFWIDTH@@':fmt(half_width),
        '@@MEMORY@@':fmt(memory_bytes/1024,1)}
    template=(ROOT/'article/aamas2027/guides/guide_template.tex').read_text()
    for key,value in replacements.items():
        template=template.replace(key,value)
    assert '@@' not in template
    OUT.mkdir(parents=True,exist_ok=True);TEX.parent.mkdir(parents=True,exist_ok=True)
    TEX.write_text(template)
    (OUT/'calculations.json').write_text(json.dumps(calculations,indent=2)+'\n')
    (OUT/'target_spec.json').write_bytes(SPEC.read_bytes())
    print(TEX)
    print('Arithmetic checks passed; prospective only; 0 API/GPU.')


if __name__=='__main__':
    main()
