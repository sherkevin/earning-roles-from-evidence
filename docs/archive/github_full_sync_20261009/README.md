# macOS full working-tree upload — 2026-10-09

This archive records the user-requested completion of the GitHub upload from the local earning-roles working tree. It is an archival operation, not an experiment, scientific qualification, or change to the active research plan.

## Scope and coverage

Code, documents, configurations, PDFs, build products, raw experiment outputs, and local benchmark overlays were inventoried. Previously ignored non-cache project artifacts are included. Unchanged benchmark sources remain pinned by the nine existing Git submodule commits in `.gitmodules`; their upstream histories are not duplicated or rewritten.

`file_manifest.json` maps every newly considered main-repository file to its uploaded path, byte hash, sanitized copy, or explicit exclusion. It also records child-repository overlays and exact pinned commits. The existing `LOCAL_CHANGES_20261009` patch and EntCollabBench datasets were verified byte-for-byte against the local copies.

## Credential handling

JWT-shaped authentication strings in 131 previously ignored JSON/JSONL logs were replaced only in public copies by deterministic `__REDACTED_JWT_<fingerprint>__` placeholders. They include historical benchmark tokens; validity was not tested. The raw originals are unchanged, remain local and ignored, and are not included in this public commit. The public copies preserve other content and record original and uploaded SHA-256 values; they are not byte-identical raw originals and must not be used as authentication credentials.

Public copies are under `artifacts/github_full_sync_20261009/sanitized/`, retaining each original relative path. No local research results were recomputed, corrected, or relabelled.

Remote-control pairing images, installed dependency trees, Python/test caches, OS metadata, and generated test-directory symlinks remain local. Git administrative data is not a repository payload. Credential files already present in third-party upstream sources are not newly copied into this archive; their existing submodule pins are unchanged.

## Restore benchmark local overlays in a new clone

Initialize first-level submodules without `--recursive` (MARBLE has historical nested gitlinks without complete URL metadata):

```sh
git submodule update --init
mkdir -p references/benchmark_sources/EntCollabBench/scripts/dataset
cp references/benchmark_sources/LOCAL_CHANGES_20261009/EntCollabBench_scripts_dataset/*.json references/benchmark_sources/EntCollabBench/scripts/dataset/
git -C references/benchmark_sources/graph-ipd apply ../LOCAL_CHANGES_20261009/graph-ipd.patch
mkdir -p references/benchmark_sources/graph-ipd/results
cp -R references/benchmark_sources/LOCAL_CHANGES_20261009/graph-ipd_results/. references/benchmark_sources/graph-ipd/results/
```

Apply the patch only to the pinned clean graph-ipd checkout. The source machine intentionally keeps its original dirty submodule state; the parent archive captures that state without committing to or pushing third-party repositories. Recreate installed dependencies using the existing package manifests rather than copying local caches.

## Verification boundary

`content_verification.json` records staged-content, JSON syntax, overlay, and coverage checks. It does not claim experimental tests passed. Successful network push and local/remote commit equality are verified separately at completion. The GitLab `origin`, branch tracking, branch name, and prior history are retained; GitHub is addressed via `github-archive` without force push.

A stale, empty `.git/index.lock` with no open-file owner was preserved locally as `.git/index.lock.stale-full-sync-20261009` before staging. No other running Git process was terminated.
