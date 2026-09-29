# Orca process record

- **Orca executable**：`/Applications/Orca.app/Contents/Resources/bin/orca`
- **Runtime**：app 1.4.215; connected; local runtime ready
- **Run**：`run_dc94677d093d`
- **Run objective**：审查 active storyline/method 是否形成 sharp、可识别、可运行贡献；read-only

## Worker outcomes

1. `ctx_69f2712cb043` (`opencode`)：worker terminal was created and task input accepted, but the terminal displayed `invalid api key`; the terminal identified its provider as MiniMax rather than Codex, and `worker-read` reported provider unsupported. It supplied no scientific output. Status remains process failure, not evidence.
2. `ctx_53d16f97208a` (`zcode`)：agent readiness timed out before task execution. The residual terminal was released using the exact Orca recovery command; no scientific output.

These failures are retained because the user asked to preserve debate process. They do not reduce or increase any research claim. The substantive Round 0 reports below came from independent local research agents with structured outputs, not from the failed Orca workers.

## Manager interpretation

Orca orchestration is currently useful for recording a supervised debate run and exposing provider/credential failures, but this run did not provide a verified external worker opinion. The project provider rule is now explicit: scientific sub-agents use Codex `gpt-6-sol` with the same AK/permissions as the coordinator. Non-Codex Orca providers are process-only and cannot enter the evidence ledger. Codex collaboration agents are being used for the remaining Round 1 challenge.
