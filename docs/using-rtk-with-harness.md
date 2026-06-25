# Using rtk with mini-swe-agent

Goal: measure token consumption on SWE-bench Lite with and without rtk,
using mini-swe-agent as the harness. This doc covers how rtk integrates
with the harness, the fork in the road for Docker vs local execution,
and the exact mechanics for a fair A/B comparison.

Last updated: 2026-06-25 (post 100-instance fair eval).
Verified against:
- rtk 0.42.4 (installed at /Users/agney/.local/bin/rtk, Mach-O arm64)
- mini-swe-agent `main` branch (v2.x) as of 2026-06-23

---

## 1. What rtk actually is

rtk is a single Rust binary that proxies common dev commands and emits
compact output:

    git status   →  rtk git status   (~2,000 tokens → ~200 tokens)
    cat file.rs  →  rtk read file.rs  (~10,000 tokens → ~500 tokens)
    rg pattern . →  rtk grep pattern  (grouped, deduplicated)
    find *.py .  →  rtk find *.py .   (compact tree)

Two integration surfaces matter for us:

1. `rtk <subcommand> <args>` — run rtk explicitly. The model has to know
   to call it. Not what we want; it biases the model's behavior and
   changes the prompt.

2. `rtk rewrite "<raw command>"` — the hook primitive. Feeds a raw
   command string in, gets back either the rtk-rewritten string (exit 3,
   rewritten command on stdout) or nothing (exit 1, passthrough). This
   is what every rtk agent integration (Claude Code, Hermes, Cursor, …)
   uses under the hood. This is what we use.

### Exit-code contract (verified)

```
$ rtk rewrite "git status"     ; echo "exit=$?"
rtk git status
exit=3

$ rtk rewrite "echo hello"      ; echo "exit=$?"
exit=1
```

The `--help` text says exit 0 on rewrite — that is stale. The real
contract (confirmed by issue #2508 and live testing) is:

| stdout       | exit code | meaning                          |
|--------------|-----------|----------------------------------|
| rewritten cmd| 3         | rtk handled it; run the rewrite   |
| (empty)      | 1         | passthrough; run the original    |

Any integration must treat exit 0 and empty stdout as passthrough too
(defensive), but the discriminating signal is **non-empty stdout**.

`rtk rewrite` also handles compound commands:

```
$ rtk rewrite "git status && git diff"
rtk git status && rtk git diff
```

So we can feed it the entire command string and it'll rewrite each
segment. No need to parse `&&`/`||`/`;` ourselves.

### Commands rtk rewrites (verified on this machine)

`git status`, `git diff`, `git log`, `ls`, `cat`→`read`,
`find`, `rg`/`grep`→`grep`, `pytest`, `cargo build`, and ~90 more.

Things rtk does NOT rewrite (passthrough, exit 1):
`echo`, `cd`, `pwd`, `npm test` (at least no rule for it here),
most bare shell builtins and arbitrary scripts.

### Platform caveat

The rtk binary at `/Users/agney/.local/bin/rtk` is Mach-O arm64 and
**cannot run inside a Linux container** (`Exec format error`). For the
Docker/SWE-bench path (§3 Path A) you need a separate Linux x86_64
musl rtk binary — `rtk-x86_64-unknown-linux-musl.tar.gz` from the
v0.42.4 GitHub release. It is static-pie, zero-dep, and runs in
SWE-bench x86_64 eval images under Rosetta emulation on arm64 macs.
`rtk rewrite` still runs on the host against the Mach-O binary; only
the *rewritten* command (`rtk git status`) runs inside the container
against the Linux binary. Both are v0.42.4 — exit-code contract
verified identical on both.

---

## 2. What mini-swe-agent actually is

A ~100-line Python agent loop. Three pluggable pieces:

- **Model** (`minisweagent.models.litellm_model.LitellmModel`) — wraps
  litellm, returns a message dict with `extra.actions` (list of
  `{"command": "..."}` bash actions) and `extra.response` (the raw
  litellm response, which includes `usage`).
- **Environment** (`minisweagent.environments.local.LocalEnvironment`
  or `minisweagent.environments.docker.DockerEnvironment`) — takes a
  command string, runs it, returns `{"output", "returncode",
  "exception_info"}`.
- **Agent** (`minisweagent.agents.default.DefaultAgent`) — the loop:
  query model → `execute_actions` → `env.execute(action)` per action →
  `model.format_observation_messages` → append to messages → repeat
  until an "exit" role message appears or a limit fires.

Critical control-flow facts (verified from source):

- The agent only has one tool: bash. Every action is
  `{"command": "<string>"}`. No Read/Grep/Glob builtins like Claude
  Code — so the "hook only sees Bash" caveat that limits rtk on Claude
  Code does NOT apply here. 100% of the agent's tool calls pass through
  `env.execute()`.

- `env.execute()` is the single chokepoint. `LocalEnvironment` calls
  `subprocess.run(command, shell=True, cwd=cwd, env=env, ...)`.
  `DockerEnvironment` calls
  `docker exec -w <cwd> [container] bash -c "<command>"`.  In both
  cases the command string is the raw thing the model produced.

- The agent never sees the command string it ran reflected back — only
  the `output` field. So rewriting the command before execution is
  transparent to the model's context in the same way the Claude Code
  PreToolUse hook is: the model asked for `git status`, it got compact
  git-status output, and its message history still says `git status`.
  This is exactly the semantics rtk is designed for.

- Trajectories are saved to `<instance_id>.traj.json` on every step
  (`finally` block in `DefaultAgent.run`). The full message list is
  there, including `extra.response` with `usage` per model call. That's
  our ground-truth token source (see §6).

---

## 3. The fork: Docker vs local

SWE-bench Lite is officially scored inside per-instance Docker images
(`swebench/sweb.eval.x86_64.<instance_id>:latest`). mini-swe-agent's
`swebench.yaml` defaults to `environment_class: docker`, `cwd: /testbed`,
`interpreter: ["bash", "-c"]`.

### Path A — Host-side rewrite (the evaluation uses this)

Subclass `DockerEnvironment`, override `execute()` so that the command
string is passed through `rtk rewrite` *on the host* before being
forwarded to `docker exec`.

  1. Launch the stock SWE-bench container as normal.
  2. `docker cp` a **Linux x86_64 musl rtk binary** into the container
     at `/usr/local/bin/rtk` in the subclass's `_start_container` hook.
  3. Override `DockerEnvironment.execute()` to call
     `rtk rewrite "<command>"` on the host; if exit 3, run the
     rewritten string inside the container; if exit 1, run the original.

### Path C — LocalEnvironment (not for SWE-bench Lite scoring)

For quick iteration on a local repo, subclass `LocalEnvironment` and
rewrite before `subprocess.run`. Not comparable to published SWE-bench
Lite numbers. Use as a sanity check, not as the eval.

---

## 4. The integration: rtk_env.py

`rtk_env.py` provides `RtkDockerEnvironment` with these features:

- **Rewrite chokepoint**: `_rewrite()` calls `rtk rewrite <command>` on
  the host before every bash command. Exit 3 → run rewritten command;
  anything else → passthrough.
- **RTK_DISABLED=1 bypass**: If the command is prefixed with
  `RTK_DISABLED=1`, the prefix is stripped and the original command runs
  without rewriting (exit code -2 in the rewrite log). Mirrors the real
  auto-rewrite hook's escape hatch.
- **exclude_commands**: Configurable list of command patterns that
  should never be rewritten (exit code -3). Mirrors the real hook's
  `[hooks] exclude_commands` in config.toml.
- **Rewrite log**: Every rewrite decision is appended as CSV to
  `rtk_rewrite.log` — timestamp, run_id, exit_code, original, rewritten.
- **Linux binary injection**: On container startup, `docker cp` the
  Linux x86_64 musl rtk binary into the container and verify it runs.

The same `RtkDockerEnvironment` with `rtk_enabled=False` is
behaviorally identical to `DockerEnvironment`.

Launch:

```bash
# Control arm (stock Docker, no rtk)
python -m minisweagent.run.benchmarks.swebench \
  --subset lite --split test --slice 0:5 \
  --model deepseek/deepseek-v4-flash \
  --environment-class docker \
  -c swebench.yaml \
  -c agent.step_limit=100 \
  -c model.cost_tracking=ignore_errors \
  -o runs/rtk-off

# RTK arm (RtkDockerEnvironment + RTK awareness)
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

`swebench_rtk.yaml` injects RTK awareness into the system prompt
(equivalent to the `RTK.md` file from `rtk init -g`). The model is told:
- What rtk rewrites
- That `rtk pytest` may produce different output than bare pytest
- How to bypass with `RTK_DISABLED=1`

---

## 5. Pitfalls and invariants

1. **Don't rewrite to a binary that isn't there.** The rewritten command
   (`rtk git status`) must run *inside the container*. `rtk_env.py`
   injects the Linux binary at container startup and fails fast if
   injection fails.

2. **`rtk rewrite` exit codes are 3/1, not 0/1.** The `--help` is wrong.
   Treat non-empty stdout as the rewrite signal, not exit 0.

3. **Don't rewrite shell builtins.** `cd /path`, `export FOO=bar`,
   `source`, `alias` — rtk passes these through (exit 1), and so must
   we. `rtk rewrite` already does this.

4. **Tell the model about rtk.** If the model doesn't know rtk exists,
   unexpected output (e.g., `Pytest: No tests collected`) causes
   panic-looping. Our original eval made this mistake and got +33.7%
   cost. The fair eval with `swebench_rtk.yaml` awareness eliminated
   this failure mode entirely.

5. **Fairness: identical limits on both arms.** `step_limit: 100`,
   `model`, temperature, seed — all identical between arms. The only
   variable is `rtk_enabled`.

6. **rtk overhead is ~10ms per call, negligible compared to LLM
   latency and the 60s command timeout.** Don't factor it out.

7. **Paired A/B may not isolate RTK's effect.** On short workloads like
   SWE-bench Lite (median 32 calls), the model takes completely different
   exploration paths on each run. Across 100 instances, zero had
   meaningful trajectory overlap (max LCS similarity: 27%). This means
   you're comparing different trajectories, not the same trajectory
   with/without compression. See §7 for discussion.

---

## 6. Measuring tokens and cost

The authoritative source is the litellm `usage` object on every model
response. mini-swe-agent stores the full response in each assistant
message's `extra.response`. `runs/measure_paired.py` computes:

- Per-instance: prompt_tokens, completion_tokens, total_tokens, n_calls
- Cost: from a built-in pricing table ($0.14/1M input, $0.28/1M output
  for DeepSeek V4 Flash direct API) or custom `--pricing` JSON.
- Aggregates: total, median, mean for each metric.

```bash
python runs/measure_paired.py --off runs/fair/rtk-off --on runs/fair/rtk-on
```

The rewrite log (`rtk_rewrite.log`) provides per-command detail: which
commands were rewritten, bypassed, or passed through.

---

## 7. Results and methodology (post 100-instance eval)

### What we ran

100 paired SWE-bench Lite instances across 20 slices (0:100), DeepSeek
V4 Flash, step limit 100. Model is aware of rtk via system prompt,
has `RTK_DISABLED=1` bypass available. No commands preemptively excluded.

### Results

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Total cost | $11.73 | $12.25 | +$0.52 (+4.5%) |
| Total calls | 3,995 | 4,063 | +68 (+1.7%) |
| Median cost/instance | $0.057 | $0.059 | +$0.003 (+3.9%) |
| Median calls/instance | 32 | 32 | 0 |

43.9% win rate for rtk-on — essentially a coin flip.
**RTK_DISABLED=1 uses: 0** across all 100 instances.

### What we learned

**Compression works.** 1,681 successful rewrites, 3.0% tool output
reduction (4.92M → 4.77M chars). The rewrite mechanism is functioning
correctly.

**No systematic failure.** Unlike our original eval (which hid rtk from
the model and got +33.7% cost from pytest panic-looping), the fair eval
shows no rtk-induced debugging loops. System prompt awareness alone
prevented the panic — the model accepted `rtk pytest`'s compact
output as normal.

**Net effect is unmeasurable.** The +4.5% cost delta is indistinguishable
from model path variance. Across all 100 instances, zero had meaningful
trajectory overlap between arms (max LCS similarity: 27%). The model
takes a different path every run — you're comparing apples to oranges,
not the same trajectory with/without compression.

### Why paired A/B fails for this workload

RTK evaluation has three effects tangled together:
1. **Compression** (measurable) — rtk shortens command output
2. **Model path variance** (unmeasurable without repeats) — the model
   picks different routes on different runs
3. **Behavioral drift** (unmeasurable without counterfactual) — rtk's
   output might nudge the model to a different next step

On SWE-bench Lite (median 32 calls, short output), the compression
effect is ~3% of tool output — too small relative to model path
variance to produce a clean signal. RTK's value proposition (60-90%
per-command compression) requires longer workloads with verbose tool
output to compound into measurable savings.

### What would be a better eval

- **Longer sessions**: 200+ tool calls, large repos, verbose test output,
  broad grep results. Compression compounds across many commands.
- **Within-trajectory measurement**: Instead of comparing two arms,
  measure per-command compression ratios on the rtk-on arm alone.
  Aggregate "tokens saved on identical work" directly from rewrite
  logs + trajectories — no model variance confound.
- **Wider workloads**: SWE-bench Lite is a specific, narrow task type.
  Real-world Claude Code sessions have much more diverse and verbose
  tool output.
