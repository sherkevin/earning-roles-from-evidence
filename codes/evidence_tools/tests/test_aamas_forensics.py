from pathlib import Path

import pytest

from evidence_tools.aamas_forensics import (
    OFFICIAL_REL, align_rows, audit_acceptance_conflicts, canonicalize_rows, index_rows,
    load_official_hotpot, project_f1, source_comparison, token_fallback_counterexample,
)

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def official():
    return load_official_hotpot(ROOT / OFFICIAL_REL)


@pytest.mark.parametrize("prediction,gold,f1,em", [
    ("The cat!", "cat", 1, True),
    ("the-cat", "cat", 0, False),  # official removes punctuation before articles
    ("yes indeed", "yes", 0, False),
    ("no answer", "noanswer", 0, False),
    ("", "", 0, True),
    ("red red blue", "red blue blue", 2/3, False),
    ("YES", "yes", 1, True),
])
def test_official_adversarial_answer_cases(official, prediction, gold, f1, em):
    assert official["f1_score"](prediction, gold)[0] == pytest.approx(f1)
    assert official["exact_match_score"](prediction, gold) is em


def test_documented_project_scorer_differences(official):
    assert project_f1("the-cat", "cat") == 1
    assert official["f1_score"]("the-cat", "cat")[0] == 0
    assert project_f1("yes indeed", "yes") == pytest.approx(2/3)
    assert official["f1_score"]("yes indeed", "yes")[0] == 0


def test_changed_official_file_is_never_executed(tmp_path):
    path = tmp_path / "scorer.py"
    path.write_text("raise RuntimeError('must not execute')", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_official_hotpot(path)


def row(key, gold="yes", question="question"):
    return {"task_id": key, "gold_answer": gold, "question": question}


def test_pairing_by_id_not_line_order():
    pairs = align_rows([row("a"), row("b")], [row("b"), row("a")])
    assert [(a["task_id"], b["task_id"]) for a,b in pairs] == [("a","a"),("b","b")]


@pytest.mark.parametrize("left,right,message", [
    ([row("a"),row("a")], [row("a")], "duplicate"),
    ([row("a")], [row("a"),row("b")], "unequal"),
    ([row("a")], [row("a", "no")], "gold mismatch"),
    ([row("a")], [row("a", question="different")], "question mismatch"),
])
def test_pairing_refuses_invalid_comparisons(left, right, message):
    with pytest.raises(ValueError, match=message):
        align_rows(left, right)


def test_empty_population_is_not_a_passing_match():
    with pytest.raises(ValueError, match="empty"):
        index_rows([])


def test_explicit_baseline_aliases_preserve_labels_and_answers():
    result = canonicalize_rows([{"task_id":"a", "answer_gold":"yes", "answer_pred":"no"}])
    assert result[0]["gold_answer"] == "yes"
    assert result[0]["final_answer"] == "no"
    align_rows([row("a")], result)


def test_conflicting_aliases_are_rejected():
    with pytest.raises(ValueError, match="conflicting schema aliases"):
        canonicalize_rows([{"gold_answer":"yes", "answer_gold":"no"}])


def test_missing_labels_are_not_inferred_from_other_arm():
    with pytest.raises(ValueError, match="missing/non-string gold"):
        align_rows([row("a")], [{"task_id":"a"}])


def test_source_comparison_separates_formatting_from_code(tmp_path):
    a,b = tmp_path/"a.py", tmp_path/"b.py"
    a.write_bytes(b"def score(x):\n    return x + 1\n")
    b.write_bytes(b"\xef\xbb\xbf# formatting\r\ndef score(x):\r\n    return x + 1\r\n")
    report = source_comparison(a,b)
    assert not report["byte_equal"] and report["normalized_ast_equal"]
    b.write_text("def score(x):\n    return x + 2\n", encoding="utf-8")
    report = source_comparison(a,b)
    assert not report["normalized_ast_equal"]
    assert report["changed_functions"] == ["score"]


def test_changed_docstrings_do_not_become_execution_drift(tmp_path):
    a,b = tmp_path/"a.py", tmp_path/"b.py"
    a.write_text('def score(x):\n    """original docs"""\n    return x\n', encoding="utf-8")
    b.write_text('def score(x):\n    """reworded docs"""\n    return x\n', encoding="utf-8")
    report = source_comparison(a,b)
    assert report["normalized_ast_equal"]
    assert report["normalized_source_diff"] == []


def test_diagnostic_text_difference_is_visible_without_claiming_behavior(tmp_path):
    a,b = tmp_path/"a.py", tmp_path/"b.py"
    a.write_text('def stop():\n    raise RuntimeError("old hint")\n', encoding="utf-8")
    b.write_text('def stop():\n    raise RuntimeError("new hint")\n', encoding="utf-8")
    report = source_comparison(a,b)
    assert not report["normalized_ast_equal"]
    assert any("old hint" in line for line in report["normalized_source_diff"])
    assert "not a proof" in report["boundary"]


def test_token_missing_total_exposes_cumulative_double_count():
    report = token_fallback_counterexample([
        {"prompt_tokens":100,"completion_tokens":20},
        {"prompt_tokens":50,"completion_tokens":10},
    ])
    assert report["legacy_cumulative_fallback"] == 300
    assert report["per_event_sum"] == 180


def test_explicit_token_totals_do_not_trigger_fallback():
    report = token_fallback_counterexample([
        {"prompt_tokens":100,"completion_tokens":20,"total_tokens":120},
        {"prompt_tokens":50,"completion_tokens":10,"total_tokens":60},
    ])
    assert report["legacy_cumulative_fallback"] == report["per_event_sum"] == 180


def test_audit_conflicts_distinguish_forward_from_terminal_accept():
    base = {"task_id":"x","hop_index":1,"chosen_target":"", "routing_features":{"edo_stage2_audit_decision":"REJECT_REROUTE"}}
    assert len(audit_acceptance_conflicts([{**base,"decision":"accept"}])) == 1
    assert audit_acceptance_conflicts([{**base,"decision":"forward","chosen_target":"worker2"}]) == []
    assert audit_acceptance_conflicts([{**base,"decision":"accept","routing_features":{"edo_stage2_audit_decision":"ACCEPT"}}]) == []
