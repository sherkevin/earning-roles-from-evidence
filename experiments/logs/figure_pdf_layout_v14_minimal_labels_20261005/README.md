# v14 layout qualification log

This directory contains both the bounded failed attempt and the clean-head
qualification. The partial `main_v14_layout.pdf` was produced before a wrapper
timeout/termination and must not be read as a PDF result; `abort.json`,
`timeout.json`, and `active_restore.json` preserve that failure and restoration.

The authoritative result is the isolated clean-HEAD worktree run described in
`clean_head_config.json`: commit `ed2011a`, v14 PDF SHA
`5c1abccf79899739df0359879f3329772a755def13b536145dd6ca18085ce6da`, 7 pages,
zero overfull boxes, zero unresolved references. The full receipt is
`clean-head-verification.json`, the PDF is `main_v14_clean_head.pdf`, and the
rendered Figure 1 page is `clean-head-page-3-3.png`.

The main worktree had an unrelated uncommitted method-section addition during
this check. Its page count is therefore not used to accept or reject v14.
