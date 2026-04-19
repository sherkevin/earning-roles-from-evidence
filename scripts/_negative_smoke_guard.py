"""Negative smoke: verify ModelDriftError fires before any HTTP request.

Run: python scripts/_negative_smoke_guard.py
Expected: prints PASS - guard fires with ModelDriftError pre-send.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "workspace"))

from idea04_core.llm_client import configure_runtime, call_llm, ModelDriftError

# Configure runtime to gpt-4.1-mini (or GLM-5.1 — either works for this test).
# We use GLM-5.1 since it has a valid local key and we don't need a live HTTP call.
# The guard must fire BEFORE the HTTP request is attempted.
configure_runtime("GLM-5.1", enforce_model=True)

print(f"Runtime configured: GLM-5.1, enforce_model=True")

# Now deliberately pass a different model string — simulating a stale DEFAULT_MODEL
# value that no longer matches the contract.
bad_model = "gpt-5.1"
try:
    call_llm(
        messages=[{"role": "user", "content": "hello"}],
        model=bad_model,   # explicit override that violates the contract
        max_tokens=1,
    )
    print("FAIL - guard did NOT fire; a request was made with the wrong model.")
    sys.exit(1)
except ModelDriftError as e:
    print(f"PASS - ModelDriftError raised before HTTP call:")
    print(f"  {e}")
    sys.exit(0)
except Exception as e:
    # If an HTTP error is raised instead of ModelDriftError, the guard failed to
    # intercept pre-send — that would also be a failure.
    print(f"FAIL - unexpected exception (guard did not fire pre-send): {type(e).__name__}: {e}")
    sys.exit(1)
