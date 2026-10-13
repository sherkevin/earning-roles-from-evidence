# Research database snapshot

Consistent SQLite backup captured on 2026-10-13 for the user-requested GitHub synchronization.
The live database and its WAL/SHM files remain local; this backup contains the committed database state.
Open research.sqlite3 directly with SQLite or copy it to a fresh work/research.db while the research application is closed. Do not overwrite an active database or reuse its old WAL/SHM files.

The manifest records integrity, table row counts, and source hashes. Nested benchmark changes are already preserved under references/benchmark_sources/LOCAL_CHANGES_20261009/; the manifest verifies equivalence without changing upstream repositories.
