# RTK evaluation harness

This repo measures mini-swe-agent SWE-bench Lite runs with and without RTK command rewriting.

## Results (100 instances, June 2026)

100 paired SWE-bench Lite instances across 20 slices (0:100), DeepSeek V4 Flash, step limit 100. The model is aware of RTK via the system prompt and has access to `RTK_DISABLED=1` as a bypass.

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Instances | 100 | 100 | — |
| Total cost | $11.73 | $12.25 | +$0.52 (+4.5%) |
| Total tokens | 82,515,762 | 86,178,284 | +3,662,522 (+4.4%) |
| Total calls | 3,995 | 4,063 | +68 (+1.7%) |
| Median cost/instance | $0.057 | $0.059 | +$0.003 (+3.9%) |
| Median calls/instance | 32 | 32 | 0 |
| RTK-on cheaper | — | 43 | 43.9% win rate |
| RTK-off cheaper | 55 | — | — |

**RTK_DISABLED=1 uses: 0** across all 100 instances (4,361 command decisions, 1,681 rewrites).

### Interpretation

- **Compression works**: RTK reduced tool output by 3.0% (4.92M → 4.77M chars), 1,681 successful rewrites.
- **No systematic failure**: No instance shows an RTK-induced debugging loop. The model accepted rtk's compact output as normal behavior.
- **Net effect is unmeasurable**: The +4.5% cost delta is indistinguishable from model path variance — the model picking different exploration routes on different runs. The two worst rtk-on losers diverged from the rtk-off arm at step 0, before any RTK-rewritten output could influence them.

### Conclusion

RTK is neutral on SWE-bench Lite when the model is aware of it. SWE-bench Lite's short, output-light tasks don't give RTK's compression enough room to compound into measurable savings. RTK's value proposition (60-90% per-command compression) would need to be evaluated on longer workloads with more verbose tool output.

Full analysis: `logs/fair-eval-summary-20260625.md` · Per-instance table: `logs/fair-eval-per-instance-20260625.md`

## Repo contents

- `rtk_env.py` provides `RtkDockerEnvironment`, a mini-swe-agent Docker environment that runs `rtk rewrite` on each bash command and injects a Linux RTK binary into the SWE-bench container. Supports `RTK_DISABLED=1` bypass and `exclude_commands` config.
- `runs/measure_paired.py` compares token usage and cost from paired `.traj.json` files.
- `swebench_rtk.yaml` injects RTK awareness into the system prompt (equivalent to the `RTK.md` file from `rtk init -g`).
- `logs/` contains the fair eval summary and per-instance breakdown.

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

### RTK off (control arm)

```bash
python -m minisweagent.run.benchmarks.swebench \
  --subset lite --split test --slice 0:5 \
  --model deepseek/deepseek-v4-flash \
  --environment-class docker \
  -c swebench.yaml \
  -c agent.step_limit=100 \
  -c model.cost_tracking=ignore_errors \
  -o runs/rtk-off
```

### RTK on (with awareness + bypass)

```bash
python -m minisweagent.run.benchmarks.swebench \
  --subset lite --split test --slice 0:5 \
  --model deepseek/deepseek-v4-flash \
  --environment-class rtk_env.RtkDockerEnvironment \
  -c swebench.yaml \
  -c swebench_rtk.yaml \
  -c model.cost_tracking=ignore_errors \
  -c environment.rtk_rewrite_log_path=runs/rtk-on/rtk_rewrite.log \
  -o runs/rtk-on
```

`swebench_rtk.yaml` is loaded after `swebench.yaml` — it overrides `system_template` (RTK awareness) and `step_limit` (100). The model is told about RTK's behavior and `RTK_DISABLED=1`. Optionally add `-c environment.exclude_commands='["pytest"]'` to preemptively exclude test runners.

## Measure

```bash
python runs/measure_paired.py --off runs/rtk-off --on runs/rtk-on
```

The script reads each trajectory's LiteLLM `usage` records and prints per-instance token/call/cost deltas plus aggregate totals.

## Grade with SWE-bench harness

mini-swe-agent writes predictions to each output dir. To evaluate resolved status locally:

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --predictions_path runs/rtk-off/preds.json \
  --run_id rtk-off \
  --report_dir logs/run_evaluation/rtk-off

python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --predictions_path runs/rtk-on/preds.json \
  --run_id rtk-on \
  --report_dir logs/run_evaluation/rtk-on
```

## Further reading

- `logs/fair-eval-summary-20260625.md` — full analysis of the 100-instance evaluation.
- `logs/fair-eval-per-instance-20260625.md` — per-instance cost/token/call table.
- `docs/using-rtk-with-harness.md` — implementation detail on how the harness integrates with mini-swe-agent.
