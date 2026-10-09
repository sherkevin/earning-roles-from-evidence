# Independent numerical and text-lock audit

Reviewer: Codex gpt-6-sol (`expected_numeric_review`), read-only.

V1 review found two under-specified statistics: backlog p95 was inserted where the
manuscript said only backlog; max-share and min-propensity were inserted where it
said concentration and propensity. V2 retains xx at those positions.

Final finding: applying the 82-slot replacement map to `before_main.tex`, then the
single authorized Table 5 typography patch, exactly reproduces `source/main.tex`.
No other wording changed. The expected-value JSON snapshot is byte-identical to v5.
The remaining numerical tuples have the intended method ordering and sources.

The reviewer initially compared total pages against the body limit, then explicitly
corrected that concern: 10 total pages comprise 8 body pages and 2 reference pages.
Final verdict: pass for the bounded expected-value backfill and text-lock task.
This is not approval of empirical results or scientific submission readiness.
