#!/usr/bin/env python3
"""Bounded native AppWorld acquisition probe using cc-switch's named provider.

Reuses the official AppWorld prompt, parser and sandbox (Apache-2.0).
No mocked API, hidden retries, evaluator-guided task solving or test data.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/experiments/aamas2027/dev_20260922"
APP = Path.home() / "work/AppWorld"
CONTRACT = ROOT / "configs/aamas2027/acquisition_probe_v1.json"


def now():
    # AppWorld freezes the simulated calendar; evidence uses the real clock.
    if "freezegun.api" in sys.modules:
        stamp = sys.modules["freezegun.api"].real_time()
    else:
        stamp = time.time()
    return datetime.datetime.fromtimestamp(stamp, datetime.timezone.utc).isoformat()


def mono():
    if "freezegun.api" in sys.modules:
        return sys.modules["freezegun.api"].real_monotonic()
    return time.monotonic()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def log(path, event, **payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps({"timestamp": now(), "event": event, "payload": payload},
                                ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def load_provider():
    database = Path.home() / ".cc-switch/cc-switch.db"
    con = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    rows = con.execute("select id,app_type,settings_config from providers where name=?",
                       ("内部",)).fetchall()
    con.close()
    if len(rows) != 1:
        raise RuntimeError("Expected exactly one named cc-switch provider 内部")
    identifier, app_type, config = rows[0]
    env = json.loads(config)["env"]
    base = env["ANTHROPIC_BASE_URL"].rstrip("/")
    if base != "https://idealab.alibaba-inc.com/api/code":
        raise RuntimeError("Provider endpoint changed; stop before sending benchmark data")
    return {"id": identifier, "app_type": app_type, "base": base,
            "secret": env["ANTHROPIC_AUTH_TOKEN"]}


class RealAPI:
    def __init__(self, log_path, max_attempts=30):
        self.provider = load_provider()
        self.log_path = Path(log_path)
        self.max_attempts = max_attempts
        self.attempts = 0
        self.usage = {"input_tokens": 0, "output_tokens": 0,
                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
        self.errors = 0
        self.unknown_usage_attempts = 0
        self.returned_models = []
        self.seconds = 0.0

    def generate(self, messages, max_tokens=2048):
        if self.attempts >= self.max_attempts:
            raise RuntimeError("Attempt budget exhausted")
        self.attempts += 1
        request = {"model": "qwen3.8-max", "messages": messages,
                   "max_tokens": max_tokens, "temperature": 0, "stream": False}
        log(self.log_path, "request_start", attempt=self.attempts, request=request)
        started = mono()
        secret = self.provider["secret"]
        usage_observed = False
        try:
            req = urllib.request.Request(
                self.provider["base"] + "/v1/messages",
                data=json.dumps(request).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer " + secret,
                         "anthropic-version": "2023-06-01"})
            with urllib.request.urlopen(req, timeout=120) as response:
                status = response.status
                raw = response.read().decode().replace(secret, "[REDACTED]")
            result = json.loads(raw)
            elapsed = mono() - started
            log(self.log_path, "response", attempt=self.attempts, status=status,
                elapsed_seconds=elapsed, response=result)
            for key in self.usage:
                self.usage[key] += int(result.get("usage", {}).get(key, 0) or 0)
            usage_observed = all(isinstance(result.get("usage", {}).get(key), int)
                                 for key in ['input_tokens','output_tokens'])
            self.returned_models.append(result.get("model"))
            text = "\n".join(block.get("text", "") for block in result.get("content", [])
                             if block.get("type") == "text")
            if not text.strip():
                raise RuntimeError("Successful HTTP response had no executable text")
            return text
        except Exception as error:
            self.errors += 1
            body = error.read().decode(errors="replace") if isinstance(error, urllib.error.HTTPError) else None
            log(self.log_path, "request_error", attempt=self.attempts,
                elapsed_seconds=mono() - started, error_type=type(error).__name__,
                message=str(error).replace(secret, "[REDACTED]"),
                body=body.replace(secret, "[REDACTED]") if body else None)
            raise
        finally:
            if not usage_observed:
                self.unknown_usage_attempts += 1
            self.seconds += mono() - started


def initialize_runtime():
    os.environ["APPWORLD_ROOT"] = str(APP)
    # httpx cannot parse the IPv6 /128 bypass as a URL host. Normalize the exact
    # one-address CIDR to its equivalent address in this subprocess only.
    import urllib.request as _request
    bypass = os.environ.get('NO_PROXY') or os.environ.get('no_proxy') or _request.getproxies().get('no','')
    if bypass:
        normalized=','.join('::1' if part.strip() in ['::1/128','[::1]'] else part.strip() for part in bypass.split(','))
        os.environ['NO_PROXY']=normalized
        os.environ['no_proxy']=normalized
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=APP, text=True).strip() != "42b5bcf3cd334fee33f0c37c02070a9f5807add5":
        raise RuntimeError("AppWorld source pin changed")
    from appworld import AppWorld
    from appworld_agents.code.simplified.react_code_agent import SimplifiedReActCodeAgent
    import appworld
    import inspect
    if not Path(appworld.__file__).resolve().is_relative_to(APP) or not Path(inspect.getfile(SimplifiedReActCodeAgent)).resolve().is_relative_to(APP):
        raise RuntimeError('Imported benchmark/parser does not match pinned checkout')
    # Use the native parser's pure methods without constructing a second API client.
    parser = object.__new__(SimplifiedReActCodeAgent)
    parser.ignore_multiple_calls = True
    parser.full_code_regex = r"```python\n(.*?)```"
    parser.partial_code_regex = r".*```python\n(.*)"
    return AppWorld, parser


def episode(job):
    AppWorld, parser = initialize_runtime()
    from jinja2 import Template
    contract = json.loads(CONTRACT.read_text())
    job_dir = OUT / "episodes" / job["id"]
    if job_dir.exists():
        raise RuntimeError(f"Refuse overwrite: {job_dir}")
    job_dir.mkdir(parents=True)
    raw = job_dir / "raw.jsonl"
    experiment = "aamas_acq_20260922_" + job["id"]
    api = RealAPI(raw, contract["runtime"]["max_attempted_calls"])
    prompt = APP / "experiments/prompts/react_code_agent/instructions.txt"
    log(raw, "episode_config", job=job, contract_sha256=digest(CONTRACT),
        script_sha256=digest(__file__), prompt_sha256=digest(prompt),
        host=platform.node(), python=sys.version, experiment_name=experiment,
        provider={k: v for k, v in api.provider.items() if k != "secret"},
        package_versions={k: importlib.metadata.version(k) for k in
                          ["appworld", "openai", "freezegun", "jinja2"]},
        benchmark_ground_truth_loaded_in_solver=False,
        model_seed=None, environment_seed=100, usd_cost=None)
    started = mono()
    public_trace = []
    failure = None
    completed = False
    stop_reason = "call_budget"
    memory = ""
    if job["arm"] == "memory":
        library_path = OUT / "memory_library.json"
        library = json.loads(library_path.read_text())
        memory = library["text"]
        log(raw, "memory_loaded", sha256=digest(library_path), text=memory)
    try:
        with AppWorld(task_id=job["task_id"], experiment_name=experiment,
                      load_ground_truth=False, random_seed=100,
                      raise_on_extra_parameters=True) as world:
            assert world.task.ground_truth is None
            rendered = Template(prompt.read_text().lstrip()).render(
                instruction=world.task.instruction, main_user=world.task.supervisor,
                app_descriptions=json.dumps([{'name':k,'description':v} for k,v in world.task.app_descriptions.items()],indent=1))
            messages = parser.text_to_messages(rendered + "\n\n")
            # Identical native prompt; an additive train-derived memory is the intervention.
            if memory:
                messages[-1]["content"] += (
                    "\n\nOptional procedural experience from other training tasks follows. "
                    "It may be incomplete or irrelevant. Use only applicable advice and verify "
                    "current entities and API specifications. The actual task and API observations "
                    "take precedence.\n<experience>\n" + memory + "\n</experience>\n")
            save(job_dir / "initial_prompt.json", messages)
            consecutive_errors = 0
            for step in range(contract["runtime"]["max_attempted_calls"]):
                try:
                    answer = api.generate(messages)
                    consecutive_errors = 0
                except Exception:
                    consecutive_errors += 1
                    if consecutive_errors >= 2:
                        stop_reason = "transport_failure"
                        break
                    continue
                code, fixed_text = parser.extract_code_and_fix_content(answer)
                messages.append({"role": "assistant", "content": fixed_text + "\n\n"})
                result = world.execute(code)
                row = {"step": step + 1, "code": code, "observation": result}
                public_trace.append(row)
                log(raw, "environment_observation", **row)
                messages.append({"role": "user", "content": "Output:\n```\n" + result + "\n```\n\n"})
                if world.task_completed():
                    completed = True
                    stop_reason = "supervisor_completed"
                    break
            # Save task state before any official evaluator is loaded.
            world.save()
            log(raw, "policy_stopped", reason=stop_reason, attempted_calls=api.attempts)
            save(job_dir / "public_trace.json", {
                "instruction": world.task.instruction, "steps": public_trace})
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error),
                   "traceback": traceback.format_exc()}
        log(raw, "runtime_error", **failure)
        AppWorld.close_all()
    # Evaluation runs only after policy execution stops; details are never fed back.
    evaluation = None
    try:
        from appworld.evaluator import evaluate_task
        evaluation = evaluate_task(task_id=job["task_id"], experiment_name=experiment,
                                   suppress_errors=True, save_report=True).to_dict(stats_only=False)
        save(job_dir / "evaluator_only.json", evaluation)
    except Exception as error:
        log(raw, "evaluation_error", error_type=type(error).__name__,
            message=str(error), traceback=traceback.format_exc())
    passes = len((evaluation or {}).get("passes", []))
    failures = len((evaluation or {}).get("failures", []))
    result = {**job, "official_success": bool((evaluation or {}).get("success", False)),
              "passed_assertions": passes, "failed_assertions": failures,
              "assertion_fraction": passes / (passes + failures) if passes + failures else None,
              "scorer_available": evaluation is not None, "task_completed": completed,
              "stop_reason": stop_reason, "attempted_calls": api.attempts,
              "usage": api.usage, "api_errors": api.errors,
              "unknown_usage_attempts": api.unknown_usage_attempts,
              "returned_models": sorted(set(api.returned_models), key=str),
              "api_seconds": api.seconds, "wall_seconds": mono() - started,
              "runtime_error": failure, "usd_cost": None,
              "native_output": str(APP / "experiments/outputs" / experiment),
              "memory_sha256": digest(OUT / "memory_library.json") if memory else None}
    save(job_dir / "result.json", result)
    log(raw, "episode_result", **result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


def induce():
    contract = json.loads(CONTRACT.read_text())
    library = []
    for family in contract["selection"]["train_families"]:
        source = OUT / "episodes" / ("acquire_" + family)
        target = OUT / "induction" / family
        target.mkdir(parents=True, exist_ok=False)
        trace = json.loads((source / "public_trace.json").read_text())
        outcome = json.loads((source / "result.json").read_text())
        raw = target / "raw.jsonl"
        log(raw, "induction_config", source_sha256=digest(source / "public_trace.json"),
            available_terminal_feedback=outcome["official_success"],
            evaluator_assertions_visible=False, max_attempts=1,
            max_output_tokens=1536, max_words=220)
        instruction = (
            "Distill at most 220 words of transferable procedural experience from the ACTUAL "
            "task trajectory below. You may see only public actions/observations and the terminal "
            "training success boolean. Do not invent successes or infer hidden evaluator conditions. "
            "Do not copy instance answers, names, phone numbers, IDs, access tokens, passwords or "
            "entity-specific literals. A successful API response only supports its demonstrated use. "
            "Preserve applicability conditions; incorrect or unverified attempts are warnings, not "
            "recommended actions. Prefer reusable search, filtering, pagination and verification "
            "procedures over a list of API names. Return a single JSON object with title (string), "
            "applicability (string), procedure (list of strings), pitfalls (list of strings), "
            "evidence_steps (list of actual step numbers). No markdown fences.\n\n" +
            json.dumps({"trace": trace, "terminal_training_success": outcome["official_success"]}))
        api = RealAPI(raw, 1)
        candidate = None
        error = None
        try:
            if not outcome['scorer_available'] or outcome['runtime_error'] or outcome['api_errors']:
                raise ValueError("Invalid acquisition infrastructure; do not infer a task-failure label")
            text = api.generate([{"role": "user", "content": instruction}], max_tokens=1536)
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
            candidate = json.loads(text)
            required = {"title", "applicability", "procedure", "pitfalls", "evidence_steps"}
            if not isinstance(candidate, dict) or set(candidate) != required:
                raise ValueError("Unexpected artifact schema")
            if not isinstance(candidate['title'],str) or not isinstance(candidate['applicability'],str):
                raise ValueError("Artifact text fields must be strings")
            for key in ['procedure','pitfalls']:
                if not isinstance(candidate[key],list) or not all(isinstance(v,str) for v in candidate[key]):
                    raise ValueError("Artifact procedure/pitfalls must be string lists")
            actual_steps = {step["step"] for step in trace["steps"]}
            if not candidate["evidence_steps"] or any(type(v) is not int or v not in actual_steps for v in candidate["evidence_steps"]):
                raise ValueError("Artifact cited unobserved step")
            encoded = json.dumps(candidate, ensure_ascii=False)
            if len(encoded.split()) > 260 or len(encoded.encode()) > 4096:
                raise ValueError("Artifact exceeds frozen size cap")
            if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\d{7,}", encoded):
                raise ValueError("Artifact contains instance contact/token-like literal")
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            candidate = None
        record = {"family": family, "source_task": family + "_1",
                  "source_trace_sha256": digest(source / "public_trace.json"),
                  "training_success": outcome["official_success"], "candidate": candidate,
                  "error": error, "usage": api.usage, "attempted_calls": api.attempts,
                  "api_errors": api.errors, "api_seconds": api.seconds,
                  "unknown_usage_attempts": api.unknown_usage_attempts}
        save(target / "artifact.json", record)
        log(raw, "artifact_result", **record)
        if candidate:
            library.append(record)
        print(json.dumps({"induction": family, "valid": candidate is not None, "error": error}), flush=True)
    content = "\n\n".join(json.dumps(row["candidate"], ensure_ascii=False) for row in library)
    save(OUT / "memory_library.json", {"entries": library, "text": content,
         "valid_candidate_count": len(library),
         "retention_order": contract["selection"]["train_families"],
         "qualification_status": "CANDIDATE; formatting/source-step checks are not semantic validation"})


def run_jobs(jobs):
    def one(job):
        result_path = OUT / "episodes" / job["id"] / "result.json"
        if result_path.exists():
            raise RuntimeError(f"Refuse silent repeated job {job['id']}")
        control = OUT / "jobs" / (job["id"] + ".json")
        save(control, job)
        command = [sys.executable, str(Path(__file__).resolve()), "episode", "--job", str(control)]
        log(OUT / "controller_raw.jsonl", "job_start", job=job, command=command)
        output = OUT / "jobs" / (job["id"] + ".log")
        with output.open("w") as stream:
            completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        log(OUT / "controller_raw.jsonl", "job_exit", id=job["id"], returncode=completed.returncode)
        if completed.returncode or not result_path.exists():
            raise RuntimeError(f"Child failed: {job['id']}; preserved log {output}")
        result = json.loads(result_path.read_text())
        print(json.dumps({k: result[k] for k in ['id','official_success','attempted_calls','api_errors','wall_seconds']}, ensure_ascii=False), flush=True)
        return result
    # Separate processes are essential: AppWorld freezes process-global time/state.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        return list(pool.map(one, jobs))


def stage(name):
    contract = json.loads(CONTRACT.read_text())
    stages = contract["jobs"]
    log(OUT / "controller_raw.jsonl", "stage_config", stage=name,
        contract_sha256=digest(CONTRACT), script_sha256=digest(__file__),
        git_base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=sys.argv, host=platform.node(), python=sys.version)
    if name == "acquire":
        run_jobs(stages["acquire"])
        induce()
    elif name == "validate":
        library=json.loads((OUT/'memory_library.json').read_text())
        if not library['entries'] or not library['text'].strip():
            raise RuntimeError("No valid acquired artifact; stop before memory/empty comparison")
        run_jobs(stages["validate"])
    elif name == "dev":
        gate = analyze()
        if not gate['dev_gate_pass']:
            raise RuntimeError("Prospective dev gate did not pass; no dev inference launched")
        run_jobs(stages["dev"])
    else:
        raise ValueError(name)
    analyze()


def analyze():
    contract = json.loads(CONTRACT.read_text())
    rows = [json.loads(p.read_text()) for p in sorted((OUT / 'episodes').glob('*/result.json'))]
    by_id = {r['id']: r for r in rows}
    pairs = []
    for family in contract['selection']['train_families']:
        empty = by_id.get('validate_empty_' + family)
        memory = by_id.get('validate_memory_' + family)
        if empty and memory:
            pairs.append({'family':family,'empty':empty['official_success'],'memory':memory['official_success'],
                          'difference':int(memory['official_success'])-int(empty['official_success']),
                          'assertion_difference':(memory['assertion_fraction'] or 0)-(empty['assertion_fraction'] or 0),
                          'runtime_valid':empty['scorer_available'] and memory['scorer_available'] and not empty['runtime_error'] and not memory['runtime_error'] and not empty['api_errors'] and not memory['api_errors']})
    nulls=[]
    for family in contract['selection']['null_families']:
        first=by_id.get('validate_empty_'+family); second=by_id.get('null_empty_'+family)
        if first and second:
            nulls.append({'family':family,'success_flip':first['official_success']!=second['official_success'],
                          'runtime_valid':first['scorer_available'] and second['scorer_available'] and not first['api_errors'] and not second['api_errors'] and not first['runtime_error'] and not second['runtime_error']})
    wins=sum(p['difference']>0 for p in pairs);losses=sum(p['difference']<0 for p in pairs)
    acquisition_valid=all((r:=by_id.get('acquire_'+f)) is not None and r['scorer_available'] and not r['runtime_error'] and not r['api_errors'] for f in contract['selection']['train_families'])
    induction=[json.loads(p.read_text()) for p in sorted((OUT/'induction').glob('*/artifact.json'))]
    library_path=OUT/'memory_library.json'
    library=json.loads(library_path.read_text()) if library_path.exists() else {}
    expected_memory_hash=digest(library_path) if library.get('text','').strip() and library.get('entries') else None
    package_valid=bool(expected_memory_hash and all(r['memory_sha256']==expected_memory_hash for r in rows if r['arm']=='memory'))
    all_cost_rows=rows+induction
    complete=len(pairs)==6 and len(nulls)==2
    gate=bool(complete and acquisition_valid and package_valid and len(induction)==6 and all(p['runtime_valid'] for p in pairs+nulls) and wins>=2 and losses==0
              and sum(p['assertion_difference'] for p in pairs)>=0 and not any(p['success_flip'] for p in nulls))
    results={'timestamp':now(),'contract_sha256':digest(CONTRACT),'episodes_completed':len(rows),
             'train_validation_complete':complete,'validation_pairs':pairs,'unchanged_package_controls':nulls,
             'validation_wins':wins,'validation_losses':losses,'dev_gate_pass':gate,
             'acquisition_infrastructure_valid':acquisition_valid,
             'memory_package_valid':package_valid,
             'attempted_episode_calls':sum(r['attempted_calls'] for r in rows),
             'episode_api_errors':sum(r['api_errors'] for r in rows),
             'episode_usage':{k:sum(r['usage'].get(k,0) for r in rows) for k in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']},
             'total_attempted_calls_including_induction':sum(r['attempted_calls'] for r in all_cost_rows),
             'total_known_usage_including_induction':{k:sum(r['usage'].get(k,0) for r in all_cost_rows) for k in ['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens']},
             'total_api_seconds_including_failed_attempts':sum(r['api_seconds'] for r in all_cost_rows),
             'total_unknown_usage_attempts':sum(r.get('unknown_usage_attempts',0) for r in all_cost_rows),
             'induction_results':induction,
             'per_episode_results':rows,'boundary':'Small fixed development acquisition probe; not Q1 interaction, role emergence, transfer qualification or confirmatory evidence.'}
    save(OUT/'summary.json',results)
    return results


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['episode','acquire','validate','dev','analyze'])
    parser.add_argument('--job')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.command=='episode':episode(json.loads(Path(args.job).read_text()))
    elif args.command=='analyze':print(json.dumps(analyze(),ensure_ascii=False,indent=2))
    else:stage(args.command)


if __name__=='__main__':
    main()
