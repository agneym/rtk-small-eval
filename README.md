# RTK evaluation harness

This repo measures mini-swe-agent SWE-bench Lite runs with and without RTK command rewriting.

## What we learned

Across 18 paired instances from four slices of SWE-bench Lite, RTK-on consistently used **more** tokens, not fewer:

- 15 paired instances resolved in both arms. 3 unresolved in both arms. No resolution changes.
- RTK-off: **9,171,502** total tokens, **573** calls.
- RTK-on: **12,158,250** total tokens, **723** calls.
- Delta: **+2,986,748 tokens (+32.6%)** and **+150 calls (+26.2%)**.
- Resolved-only: **6,370,506 → 8,888,228 tokens (+39.5%)**, **440 → 575 calls (+30.7%)**.

The main lesson is that RTK's per-command output savings can be overwhelmed if rewriting changes behavior enough to create extra agent turns. The biggest outlier was `astropy__astropy-14995`: RTK-on spent **+1.94M tokens** and **+70 calls**, mostly because pytest commands were rewritten to `rtk pytest ...`, which produced repeated `Pytest: No tests collected` observations and sent the agent into a debugging loop.

Read these first:

- `logs/run_evaluation_summary_resolved_only_20260624.md` — headline resolved-only token/call comparison.
- `logs/run_evaluation_summary_20260624.md` — full comparison including unresolved pairs.
- `logs/rtk_token_overuse_diagnosis_20260623.md` — diagnosis of why RTK consumed more tokens.

```mermaid
xyChart-beta
    title "Total tokens spent (all 18 pairs)"
    x-axis ["rtk-off", "rtk-on"]
    y-axis "tokens" 0 --> 13000000
    bar [9171502, 12158250]
```

```mermaid
xyChart-beta
    title "Total tool/API calls (all 18 pairs)"
    x-axis ["rtk-off", "rtk-on"]
    y-axis "calls" 0 --> 800
    bar [573, 723]
```

Important interpretation: this is not caused by merely installing RTK. It is caused by putting RTK in the command path via our transparent `rtk rewrite` harness, which is similar to RTK's auto-rewrite hook behavior. Test-runner rewrites should be treated carefully or excluded.

## Repo contents

- `rtk_env.py` provides `RtkDockerEnvironment`, a mini-swe-agent Docker environment that runs `rtk rewrite` on each bash command and injects a Linux RTK binary into the SWE-bench container.
- `runs/measure_paired.py` compares token usage from paired `.traj.json` files.
- `logs/` contains evaluation summaries and diagnosis notes.

## Prerequisites

- Docker running locally.
- `mise` available, or equivalent Python 3.13 + `uv` setup.
- API credentials for the model provider you plan to use, configured for LiteLLM / mini-swe-agent.
- Host RTK installed on PATH (`rtk --version`). `mise install` installs `rtk 0.42.4` as configured in `mise.toml`.

## Setup

```bash
mise install
mise run install
```

Fetch/verify the Linux x86_64 RTK binary used inside SWE-bench Docker containers:

```bash
bash scripts/fetch-rtk-linux.sh
```

This should create:

```text
vendor/rtk-x86_64-unknown-linux-musl
```

## Run an A/B pair

Run from the repo root so `rtk_env.py` is importable and the relative `vendor/` RTK binary path resolves correctly.

### RTK off

```bash
python -m minisweagent.run.benchmarks.swebench \
  --subset lite --split test --slice 0:5 \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --environment-class docker \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -o runs/example/rtk-off
```

### RTK on

```bash
python -m minisweagent.run.benchmarks.swebench \
  --subset lite --split test --slice 0:5 \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --environment-class rtk_env.RtkDockerEnvironment \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -c environment.rtk_rewrite_log_path=runs/example/rtk-on/rtk_rewrite.log \
  -o runs/example/rtk-on
```

Swap `--model` as needed, for example `deepseek/deepseek-v4-flash` if your LiteLLM config supports it.

## Measure token usage

After both arms finish:

```bash
python runs/measure_paired.py \
  --off runs/example/rtk-off \
  --on runs/example/rtk-on
```

The script reads each trajectory's LiteLLM `usage` records and prints per-instance token/call deltas plus aggregate means/medians.

## Optional: grade with SWE-bench harness

mini-swe-agent writes predictions to each output dir. To evaluate resolved status locally:

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --predictions_path runs/example/rtk-off/preds.json \
  --run_id example-rtk-off \
  --report_dir logs/run_evaluation/example-rtk-off

python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --predictions_path runs/example/rtk-on/preds.json \
  --run_id example-rtk-on \
  --report_dir logs/run_evaluation/example-rtk-on
```

## Important caveat

Current RTK rewrite rules rewrite pytest commands, e.g. `python -m pytest ...` to `rtk pytest ...`. In our logs this caused some RTK-on runs, especially `astropy__astropy-14995`, to spend many extra turns debugging `Pytest: No tests collected`.

See:

- `logs/rtk_token_overuse_diagnosis_20260623.md`
- `logs/run_evaluation_summary_resolved_only_20260624.md`

For more implementation detail, read `docs/using-rtk-with-harness.md`.
