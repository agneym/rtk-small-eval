# Using rtk with mini-swe-agent

Goal: measure token consumption on SWE-bench Lite with and without rtk,
using mini-swe-agent as the harness. This doc covers how rtk integrates
with the harness, the fork in the road for Docker vs local execution,
and the exact mechanics for a fair A/B comparison.

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
   uses under the hood. This is what we'll use.

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

This is fine and important: rtk only touches commands where it can
losslessly compress. `cd /path` must stay `cd /path` or the model's
mental model breaks. See rtk issue #2508 for the failure mode when
this invariant is violated.

### Platform caveat (Phase 0, 2026-06-23)

The rtk binary at `/Users/agney/.local/bin/rtk` is Mach-O arm64 and
**cannot run inside a Linux container** (`Exec format error`). For the
Docker/SWE-bench path (§3 Path A) you need a separate Linux x86_64
musl rtk binary — `rtk-x86_64-unknown-linux-musl.tar.gz` from the
v0.42.4 GitHub release. It is static-pie, zero-dep, and runs in
SWE-bench x86_64 eval images under Rosetta emulation on arm64 macs.
`rtk rewrite` still runs on the host against the Mach-O binary; only
the *rewritten* command (`rtk git status`) runs inside the container
against the Linux binary. Both are v0.42.4 — exit-code contract
verified identical on both (Phase 0 finding 3).

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
  our ground-truth token source (see §6). Caveat (Phase 0, 2026-06-23):
  the per-step `finally` fires on Python-level exceptions and limits,
  but `process_instance`'s per-instance `finally` is guarded by
  `if agent is not None` — if env startup fails (container pull,
  startup-command error), no `.traj.json` is written, only a
  `preds.json` entry with `exit_status=<ExceptionType>`. And no
  `finally` fires on process-level kill (OOM, SIGKILL). `run.log`
  (Logging invariant #3) covers those gaps and cannot be skipped.

---

## 3. The fork: Docker vs local

SWE-bench Lite is officially scored inside per-instance Docker images
(`swebench/sweb.eval.x86_64.<instance_id>:latest`). mini-swe-agent's
`swebench.yaml` defaults to `environment_class: docker`, `cwd: /testbed`,
`interpreter: ["bash", "-c"]`.

That creates two distinct integration paths:

### Path A — Host-side rewrite (recommended for the eval)

Subclass `DockerEnvironment`, override `execute()` so that the command
string is passed through `rtk rewrite` *on the host* before being
forwarded to `docker exec`. The rtk binary lives on the host; the
container never sees rtk.

Why this works:
- `docker exec ... bash -c "rtk git status"` requires rtk inside the
  image. `docker exec ... bash -c "git status"` (with rtk having
  rewritten "git status" → already-executed compact output) is impossible
  because the rewrite needs to change *which binary runs*. So we have
  to run rtk on the host, let it produce the compact stdout, and inject
  that stdout as the command's output.
- The clean way: keep rtk on the host, run `rtk <subcmd> <args>` on the
  host, but with `--cwd`/`chdir` pointed at the *container's* working
  directory bind-mounted or via `docker cp`. This is fragile.

The actually-clean way: rewrite on the host, then run the rewritten
command *inside* the container. I.e.
"`rtk git status`" → rewrite yields "`rtk git status`" → but rtk isn't
in the container. So we install a tiny rtk binary into the container at
startup, OR we run rtk on the host against a bind-mount of `/testbed`.

The simplest robust variant of Path A that preserves full SWE-bench
semantics:

  1. Launch the stock SWE-bench container as normal.
  2. `docker cp` a **Linux x86_64 musl rtk binary** (from the v0.42.4
     GitHub release — NOT the host Mach-O binary, which fails with
     `Exec format error`) into the container at `/usr/local/bin/rtk`
     in the subclass's `_start_container` hook. (Phase 0 finding 5:
     `env_startup_command` can't do this — no `{container_name}` var,
     `StrictUndefined`, and it runs inside the container where
     `docker cp` can't reach the host daemon.)
  3. Override `DockerEnvironment.execute()` to call
     `rtk rewrite "<command>"` on the host; if exit 3, run the
     rewritten string inside the container; if exit 1, run the original.

This keeps the agent's command history unchanged (it still says
`git status`), keeps the SWE-bench validation images unmodified at
checkout time (we only inject a binary at runtime), and lets rtk do its
job on the real `/testbed` contents.

### Path B — In-container alias / wrapper (simpler, slightly less clean)

Install rtk into the container, then set `BASH_ENV` to a script that
defines a shell function for every rtk-supported command:
`git() { rtk git "$@"; }`, `cat() { rtk read "$@"; }`, etc.

This rewrites transparently with zero Python changes. Downside: shell
functions don't compose with pipes/`&&` the way `rtk rewrite` does, and
some SWE-bench tasks invoke commands in ways that bypass the function
table (e.g. `command git`, `/usr/bin/git`, `env git`). Path A is strictly
more correct.

### Path C — LocalEnvironment (not for SWE-bench Lite scoring)

For quick iteration on a local repo (the `mini` CLI path), subclass
`LocalEnvironment` and rewrite before `subprocess.run`. This skips
Docker entirely and is great for validating the integration mechanics,
but gives results that are not comparable to published SWE-bench Lite
numbers. Use as a sanity check, not as the eval.

---

## 4. The integration: an rtk-aware environment subclass

The smallest change to mini-swe-agent that gives us a clean A/B toggle:

```python
# rtk_env.py — ship as rtk_env (on PYTHONPATH or in site-packages)
import shutil
import subprocess
from minisweagent.environments.docker import (
    DockerEnvironment, DockerEnvironmentConfig,
)

class RtkDockerEnvironmentConfig(DockerEnvironmentConfig):
    rtk_enabled: bool = True
    rtk_path: str = shutil.which("rtk") or "rtk"
    # Path to the Linux x86_64 musl rtk binary to inject into the
    # container. NOT the host Mach-O binary (Phase 0 finding 3).
    rtk_linux_binary: str = "vendor/rtk-x86_64-unknown-linux-musl"

class RtkDockerEnvironment(DockerEnvironment):
    def __init__(self, *, config_class=RtkDockerEnvironmentConfig, **kw):
        super().__init__(config_class=config_class, **kw)
        self.instance_id = ""  # tagged per-instance by the harness hook

    def _start_container(self):
        # Let the base class launch the container and set self.container_id.
        super()._start_container()
        if not self.config.rtk_enabled:
            return
        # Inject the Linux rtk binary from the host into the running
        # container. env_startup_command can't do this (Phase 0 finding 5).
        # Fail fast if cp/chmod/version-check fails — a broken injection
        # silently turns every rewrite into "command not found" (pitfall #1).
        cid = self.container_id
        subprocess.run(["docker", "cp", self.config.rtk_linux_binary,
                        f"{cid}:/usr/local/bin/rtk"], check=True)
        subprocess.run(["docker", "exec", cid, "chmod", "+x",
                        "/usr/local/bin/rtk"], check=True)
        subprocess.run(["docker", "exec", cid, "/usr/local/bin/rtk",
                        "--version"], check=True)

    def _rewrite(self, command: str) -> tuple[str, int, str]:
        if not self.config.rtk_enabled:
            return command, -1, ""
        try:
            r = subprocess.run(
                [self.config.rtk_path, "rewrite", command],
                capture_output=True, text=True, timeout=5,
            )
        except Exception:
            return command, -1, ""
        # exit 3 + stdout = rewritten; anything else = passthrough
        if r.returncode == 3 and r.stdout and r.stdout.strip():
            return r.stdout.strip(), r.returncode, r.stdout.strip()
        return command, r.returncode, ""

    def execute(self, action, cwd="", *, timeout=None):
        if not self.config.rtk_enabled:
            return super().execute(action, cwd=cwd, timeout=timeout)
        original = action.get("command", "")
        effective, exit_code, rewritten = self._rewrite(original)
        if effective is not original:
            action = {**action, "command": effective}
        # Append one CSV line per rewrite decision (Logging invariant #2):
        # timestamp, instance_id, exit_code, original, rewritten
        self._append_rewrite_log(exit_code, original, rewritten)
        return super().execute(action, cwd=cwd, timeout=timeout)
```

Register it so mini-swe-agent can find it by name. **Note (Phase 0,
2026-06-23):** `minisweagent.environments.ENV_CLASSES` does not exist.
The registry is a private dict `_ENVIRONMENT_MAPPING` resolved by
`get_environment_class(spec)`, which falls back to treating `spec` as a
full dotted import path when the name is not in the mapping. The clean
path: ship `rtk_env.py` as an importable module
(`rtk_env.RtkDockerEnvironment`) and pass the full dotted
path on the CLI. No registration, no mutating private internals:

```python
# rtk_env.py lives on the Python path as rtk_env
# (e.g. site-packages/minisweagent/rtk_env.py, or a drop-in added via
# PYTHONPATH). Launch with:
#   --environment-class rtk_env.RtkDockerEnvironment
```

Then launch with — note the `env_startup_command` line is **gone**
(Phase 0 finding 5: `{container_name}` is not a render var and uses
`StrictUndefined`; and `env.execute` runs inside the container where
`docker cp` can't reach the host daemon). rtk injection happens in the
subclass's `_start_container` instead, and uses a **Linux x86_64 musl
rtk binary**, not the host Mach-O one (Phase 0 finding 3: Mach-O fails
with `Exec format error` in the container):

```bash
# Run from the repo root: `vendor/rtk-x86_64-unknown-linux-musl` is a
# relative path resolved against the process CWD. Override with an
# absolute `-c environment.rtk_linux_binary=...` if launching elsewhere.
mini-extra swebench \
  --subset lite --split test --slice 0:20 \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --environment-class rtk_env.RtkDockerEnvironment \
  -c swebench.yaml \
  -c environment.rtk_rewrite_log_path=runs/rtk-on/rtk_rewrite.log \
  -o runs/rtk-on
```

…and the control arm with stock `docker`, same slice and seed:

```bash
mini-extra swebench \
  --subset lite --split test --slice 0:20 \
  --model anthropic/claude-sonnet-4-5-20250929 \
  --environment-class docker \
  -c swebench.yaml \
  -o runs/rtk-off
```

Notes (updated by Phase 0, 2026-06-23):
- `env_startup_command` is Jinja2-templated with `**instance` only (the
  SWE-bench instance dict) and uses `StrictUndefined`. There is no
  `{container_name}` var — the §4 example using it raises
  `jinja2.exceptions.UndefinedError`. And `env.execute(startup_command)`
  runs inside the container, where `docker cp` can't reach the host
  daemon. The subclass `_start_container` hook is **required**, not the
  cleaner option. The base class stores the container name on
  `self.container_id` (not `container_name`).
- The host rtk binary is Mach-O arm64 and cannot run in a Linux
  container. Inject a Linux x86_64 musl rtk binary (v0.42.4, from the
  GitHub release) via `docker cp`. `rtk rewrite` still runs on the host
  against the Mach-O binary; only the rewritten command runs inside the
  container against the Linux binary. Both are v0.42.4.
- The same `RtkDockerEnvironment` with `rtk_enabled=False` is
  behaviorally identical to `DockerEnvironment`, so a single class with
  a config flag is enough — you don't even need two environment classes.

---

## 5. Pitfalls and invariants

1. **Don't rewrite to a binary that isn't there.** The rewritten command
   (`rtk git status`) must run *inside the container*. Either install
   rtk in the container (Path A startup step) or run rtk on the host
   against a bind-mounted `/testbed`. If `rtk` is missing in the
   container, `docker exec ... bash -c "rtk git status"` returns
   `command not found` and the agent sees garbage. Always verify with a
   smoke test: `echo 'FROM swebench/sweb.eval.x86_64.django_1776_django-11099:latest' | ...`

2. **`rtk rewrite` exit codes are 3/1, not 0/1.** The `--help` is wrong.
   Treat non-empty stdout as the rewrite signal, not exit 0.

3. **Don't rewrite shell builtins.** `cd /path`, `export FOO=bar`,
   `source`, `alias` — rtk passes these through (exit 1), and so must
   we. `rtk rewrite` already does this; our subclass inherits it for
   free. See rtk issue #2508 for what happens when this breaks.

4. **Command history fidelity.** The model's message history must still
   say `git status`, not `rtk git status`. Our subclass rewrites only
   the `command` field passed to `docker exec`; it does NOT mutate the
   action dict that gets serialized into the trajectory. Verify this by
   diffing `runs/rtk-on/<id>.traj.json` and `runs/rtk-off/<id>.traj.json`:
   the `actions[].command` strings should be identical; only the
   observation `output` strings should differ.

5. **The 10,000-char observation truncation is independent.**
   mini-swe-agent's `observation_template` truncates long outputs to
   head+tail 5k. rtk reduces output *before* it hits that template, so
   for many commands the truncation never fires in the rtk-on arm. This
   is a real effect, not a bug — it's part of the token savings. Don't
   "fix" it.

6. **Fairness: identical limits on both arms.** `step_limit: 250`,
   `cost_limit: 3.0`, `wall_time_limit_seconds` if used, token budget,
   model temperature, seed — all identical between arms. The only
   variable is `rtk_enabled`. Randomize instance order identically
   (`--shuffle` uses seed 42; don't re-seed differently per arm).

7. **rtk overhead is ~10ms per call, negligible compared to LLM
   latency and the 60s command timeout.** Don't factor it out.

8. **`rtk gain` and `rtk discover` are analytics, not measurement.**
   They read rtk's own SQLite log of past runs. They will not report
   anything useful for an A/B eval. Use the trajectory token counts
   (§6).

---

## 6. Measuring tokens

The authoritative source is the litellm `usage` object on every model
response. mini-swe-agent stores the full response in each assistant
message's `extra.response`. So per-trajectory token totals are:

```python
import json
from pathlib import Path

def trajectory_tokens(traj_path: Path) -> dict:
    data = json.loads(traj_path.read_text())
    prompt_tokens = 0
    completion_tokens = 0
    n_calls = 0
    for msg in data["messages"]:
        resp = msg.get("extra", {}).get("response")
        if not resp or "usage" not in resp:
            continue
        u = resp["usage"]
        prompt_tokens += u.get("prompt_tokens", 0)
        completion_tokens += u.get("completion_tokens", 0)
        n_calls += 1
    return {
        "instance_id": data["info"]["instance_id"],
        "exit_status": data.get("exit_status"),
        "n_calls": n_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
```

Run that over every `.traj.json` in both `runs/rtk-on/` and
`runs/rtk-off/`, keyed by `instance_id`. The comparison is:

    tokens(on, instance)  vs  tokens(off, instance)   for the same instance

Report per-instance deltas and aggregate (median + mean, since the
distribution is heavy-tailed). The resolution-rate number
(`exit_status == "Submitted"` and ultimately `resolved` from sb-cli)
must be reported alongside — token savings that tank resolution is a
regression, not a win.

For the resolved/not-resolved verdict, submit both arms' `preds.json`
to sb-cli:

```bash
sb-cli submit swe-bench_lite test \
  --predictions_path runs/rtk-on/preds.json --run_id rtk-on-$(date +%s)
sb-cli submit swe-bench_lite test \
  --predictions_path runs/rtk-off/preds.json --run_id rtk-off-$(date +%s)
```

Final table per arm:

| metric                  | rtk-off | rtk-on | delta |
|-------------------------|---------|--------|-------|
| resolved                |    ?    |   ?    |       |
| submitted               |    ?    |   ?    |       |
| median prompt tokens    |    ?    |   ?    |       |
| median completion tokens|    ?    |   ?    |       |
| median total tokens     |    ?    |   ?    |       |
| median steps            |    ?    |   ?    |       |

---

## 7. Dataset scope

- **Dataset:** SWE-bench Lite (`princeton-nlp/SWE-bench_Lite`, split
  `test`, 300 instances). Public leaderboard tops out ~62.7% (Claude
  Opus 4.6 Thinking, mid-2026). That's "saturated enough" for our
  purposes — resolution rate is high enough that token cost, not
  correctness, is the interesting axis, and the dataset is
  well-characterized so variance is understood.

- **Run size: 20 instances.** Full 300-instance sweep isn't needed;
  20 paired observations is enough to see the rtk token delta clearly
  (rtk's claimed effect is 60-90% per command, far larger than
  per-instance variance). Use `--slice 0:20` on both arms with the same
  seed so the two arms see the same 20 instances.

  Variance note: with n=20 paired samples, the standard error of the
  mean token delta is σ/√20 ≈ σ/4.5. If the true mean savings is ~50%
  and σ is ~15% of the off-arm mean (typical for SWE-bench token
  distributions), the 95% CI on the mean is roughly ±13% — wide enough
  to confirm "rtk saves a lot" but not to nail the exact percentage.
  That's an acceptable trade for not spending 300×2×$3 of model budget.
  If a tighter number is wanted later, run the same 20 again with a
  different slice and pool.

---

## 8. TL;DR

- rtk integrates with mini-swe-agent at the `Environment.execute()`
  chokepoint via `rtk rewrite`, not via prompt changes.
- Write a `RtkDockerEnvironment` subclass that rewrites the command
  string before delegating to the stock `DockerEnvironment.execute()`.
  Install rtk into the container at startup so the rewritten commands
  can actually run there.
- Run two arms: `rtk_enabled=True` and `rtk_enabled=False` (or stock
  `docker` env), same model, same limits, same seed, same instance set.
- Measure tokens from `extra.response.usage` in the trajectories;
  measure resolution from sb-cli. Report both.