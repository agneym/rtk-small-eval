# Phases: rtk × mini-swe-agent A/B run

Companion to `docs/using-rtk-with-harness.md`. Section numbers below
refer to that doc. Each phase has a goal and an exit criterion; do
not start the next phase until the previous one's exit criteria pass.

---

## Logging invariants (all phases)

If a run goes wrong we need to reconstruct what happened from disk
alone. Three log streams, written per-run under `runs/<arm>/`:

1. **Trajectories** (`<instance_id>.traj.json`) — mini-swe-agent saves
   these in a `finally` block on every step, so they survive a crash
   mid-instance. Primary forensic source: full message history,
   `extra.response.usage`, and every `action.command` +
   `observation.output` pair. Already produced by the harness; do not
   disable it. Confirm the `finally` write fires on abort, not just on
   clean exit (Phase 0).

2. **rtk rewrite log** (`runs/<arm>/rtk_rewrite.log`) — the
   `RtkDockerEnvironment._rewrite` method (Phase 1) must append one
   line per rewrite decision:
   `timestamp, instance_id, exit_code, original, rewritten`.
   This is the *only* place that records which commands rtk touched
   and what it turned them into. The trajectory can't answer this on
   its own — by design (pitfall #4) it shows the original command and
   the compact output, not the rewrite decision. Without this log,
   "rtk-on arm behaves weirdly" is un-debuggable. Does not exist yet;
   add it in Phase 1.

3. **Process log** (`runs/<arm>/run.log`) — tee `mini-extra swebench`
   stdout+stderr to this file. Catches model errors, env exceptions,
   and harness-level failures that never reach a trajectory
   (container pull failure, OOM kill, litellm auth error).

Per-phase additions:

- **Phase 3 / 4**: save `env_startup_command` stdout/stderr per
  instance to `runs/<arm>/startup/<instance_id>.log`. If the `docker
  cp` of the rtk binary fails, this is how you'd see it without
  diffing 20 trajectories for `command not found`.
- **Phase 4**: after the first instance, verify rtk is actually
  executable in the container (`docker exec <container> rtk
  --version`) before launching the remaining 19. A broken injection
  silently turns every rewritten command into `command not found` and
  wastes the whole arm. Fail fast.
- **Phase 5**: write sb-cli's JSON output to
  `runs/<arm>/sb_result.json` alongside the token table.

---

## Phase 0 — Verify bottoms

Confirm the doc's claims on this machine before writing code.

- **Toolchain pinned.** `mise install`
  ran clean (no error tail). `mise exec -- rtk --version` == 0.42.4.
  `mise exec -- python --version` and `mise exec -- node --version`
  return the versions pinned in `mise.toml`. mini-swe-agent's
  `requires-python` (from its `pyproject.toml`) contains the pinned
  Python; if not, re-pin and re-run before continuing.
- `rtk --version` == 0.42.4, `which rtk` resolves to
  `/Users/agney/.local/bin/rtk` (host).
- Run the two exit-code probes from §1 on the host *and* inside one
  SWE-bench container after `docker cp`:
  - `rtk rewrite "git status"` → stdout `rtk git status`, exit 3
  - `rtk rewrite "echo hello"` → empty stdout, exit 1
- Confirm `DockerEnvironment`, `DockerEnvironmentConfig`, and
  `ENV_CLASSES` exist at the import paths in §4.
- Confirm `env_startup_command` is Jinja2-templated with
  `{container_name}`. Doc flags this as uncertain — resolve it now
  so §4 doesn't need a mid-run fallback.
- Confirm the trajectory-write `finally` block fires on abort, not
  just on clean exit (see Logging invariants #1). Walk the source and
  check the write isn't inside a conditional that a mid-instance
  crash would skip. This is the forensic floor — cannot be deferred.

Exit criteria: concrete answers to all six items above. Any "no"
here changes §4 before you write a line of Python.

### Results (2026-06-23)

1. **Toolchain pinned — PASS.** `mise install` clean. `mise exec --
   rtk --version` == 0.42.4, `mise exec -- python --version` ==
   3.13.14, `mise exec -- node --version` == v25.9.0 — all match
   `mise.toml`. mini-swe-agent dist metadata: Version 2.4.2,
   Requires-Python `>=3.10`, satisfied by pinned 3.13.14.
2. **Host rtk — PASS.** `which rtk` → `/Users/agney/.local/bin/rtk`,
   `rtk --version` → 0.42.4. The binary is Mach-O arm64 (hard link
   into `~/.local/share/mise/installs/aqua-rtk-ai-rtk/0.42.4/rtk`).
3. **Exit-code probes — PASS on host and in a Linux container.**
   Host: `rtk rewrite "git status"` → stdout `rtk git status`, exit 3;
   `rtk rewrite "echo hello"` → empty stdout, exit 1; compound
   `"git status && git diff"` → `rtk git status && rtk git diff`,
   exit 3. Ran the same three probes inside a `debian:bookworm-slim`
   (linux/amd64 under Rosetta) container after `docker cp` — identical
   results.
   - ⚠️ **BLOCKER not in §3/§4:** the host rtk is Mach-O arm64 and
     **cannot run inside a Linux container** (`Exec format error`).
     `docker cp /usr/local/bin/rtk ...` from the host copies the
     Mach-O binary and fails. A **Linux x86_64 musl rtk binary** is
     required — `rtk-x86_64-unknown-linux-musl.tar.gz` from the
     v0.42.4 GitHub release (exists, verified; static-pie, zero deps,
     runs in SWE-bench x86_64 images under emulation). Check this
     binary into the repo (or download via a setup script) and `docker
     cp` *that*. rtk `rewrite` still runs on the host against the
     Mach-O binary; only the rewritten command (`rtk git status`)
     runs inside the container against the Linux binary. Version 0.42.4
     is consistent across both.
4. **import paths — PARTIAL PASS, doc divergence.**
   `DockerEnvironment` and `DockerEnvironmentConfig` exist at
   `minisweagent.environments.docker` (both confirmed; Config is a
   pydantic BaseModel; `execute(self, action, cwd="", *, timeout=None)`
   signature matches §4's override).
   `ENV_CLASSES` **does not exist** at `minisweagent.environments`.
   The real registry is a private dict `_ENVIRONMENT_MAPPING` in
   `environments/__init__.py`, resolved by `get_environment_class(spec)`.
   It falls back to treating `spec` as a full dotted import path when
   the name is not in the mapping. So `--environment-class
   rtk_env.RtkDockerEnvironment` works **without any
   registration**. Do not mutate `_ENVIRONMENT_MAPPING` for a short
   alias — pass the full dotted path on the CLI.
5. **`env_startup_command` templating — ✗ DIVERGENCE (resolves the
   doc's uncertainty; negates the §4 example).** Source
   (`swebench.py:89-91`):
   ```
   if startup_command := config.get("run", {}).get("env_startup_command"):
       startup_command = Template(startup_command, undefined=StrictUndefined).render(**instance)
       out = env.execute(startup_command)
   ```
   - Render vars are `**instance` only (the SWE-bench instance dict).
     There is **no `{container_name}`** in the var set, and
     `StrictUndefined` means the §4 example
     `... {container_name}:/usr/local/bin/rtk` raises
     `jinja2.exceptions.UndefinedError` at startup — it does not fall
     back gracefully.
   - Second flaw: `env.execute(startup_command)` runs **inside** the
     container via `docker exec <container> bash -lc "<cmd>"`. A
     `docker cp` issued from inside the target container cannot reach
     the host docker daemon (no socket mounted). The §4
     `env_startup_command` approach is doubly broken.
   - The doc's "noted fallback" (a `_start_container` hook in the
     subclass) is **required**, not optional. `DockerEnvironment`
     generates its own container name (`f"minisweagent-{uuid…}"`) in
     `_start_container` and stores it on `self.container_id` (not
     `container_name`). The subclass can read `self.container_id`
     after `super().__init__()` and `docker cp` the Linux rtk binary
     in from the host.
6. **Trajectory `finally` on abort — PARTIAL PASS (more nuanced than
   the doc's claim).** Two save sites:
   - Per-step: `DefaultAgent.run()` does `try: step() except… finally:
     self.save(self.config.output_path)` (default.py:118-119). Fires on
     every step and after `FormatError` / `InterruptAgentFlow` /
     `LimitsExceeded` / `TimeExceeded` / uncaught `Exception` (the
     `except Exception: handle_uncaught_exception(e); raise` still
     runs `finally` before propagating). Python-level exceptions
     mid-instance produce a trajectory.
   - Per-instance: `process_instance` (`swebench.py:161-174`) has its
     own `finally` that calls `agent.save(traj_path, …)` — **guarded
     by `if agent is not None`**. `agent` is assigned inside the
     `try` at line 147. If `get_sb_environment` (line 146) throws —
     container pull failure, startup `RuntimeError` (line 93) —
     `agent` stays `None` and **no `.traj.json` is written** for that
     instance; only `preds.json` gets an `exit_status=<ExceptionType>`
     entry.
   - Neither `finally` fires on **process-level kill** (OOM, SIGKILL,
     power loss). No trajectory survives those.

   Net: the "survives a crash mid-instance" claim holds for Python
   exceptions and limits, but **not** for (a) env-startup failures (no
   trajectory, only a `preds.json` entry) or (b) hard process kills.
   `run.log` (Logging invariant #3) is what covers the gap — it
   cannot be skipped.

## Phase 1 — Build the integration

- Write `rtk_env.py` (the subclass from §4, updated per Phase 0
  results) and ship it as an importable module
  (`rtk_env.RtkDockerEnvironment` — the full dotted
  path is what `--environment-class` takes; there is no `ENV_CLASSES`
  to register into).
- Inject rtk via an overridden `_start_container` in the subclass,
  **not** via `env_startup_command`. `env_startup_command` (a) has no
  `{container_name}` var and uses `StrictUndefined` (raises), and (b)
  runs inside the container where `docker cp` can't reach the host
  daemon. The subclass calls `super()._start_container()`, then
  `docker cp <linux-rtk> <self.container_id>:/usr/local/bin/rtk` from
  the host.
- `<linux-rtk>` is a Linux x86_64 musl rtk binary (v0.42.4, from the
  GitHub release) — *not* the host Mach-O binary, which fails with
  `Exec format error` in the container. Check it into the repo or
  fetch via a setup script.
- One class with `rtk_enabled: bool` flag, not two classes.
- Add the rtk rewrite log append in `_rewrite` (Logging invariants
  #2). One line per decision: `timestamp, instance_id, exit_code,
  original, rewritten`. Pass `instance_id` in via the action or the
  env's current-instance attribute — whichever the base class exposes.

Exit criteria: `python -c "from minisweagent.environments import get_environment_class; print(get_environment_class('rtk_env.RtkDockerEnvironment'))"` resolves to the subclass (not
`ENV_CLASSES` — it doesn't exist), and a manual call to
`_rewrite("git status")` produces one line in `rtk_rewrite.log`.

## Phase 2 — Smoke test (local, Path C)

Before touching Docker/SWE-bench: run the subclass on a single local
instance against your own repo.

- `rtk_enabled=True`: a `git status` action gets rewritten to
  `rtk git status` and the rewritten command actually executes.
- `rtk_enabled=False`: passthrough confirmed.
- This is the cheap version of pitfalls #1 and #4.

Exit criteria: two trajectories locally whose `actions[].command`
strings are identical between arms, and no `command not found` in any
observation. `rtk_rewrite.log` exists and has one line per rtk-fired
decision (sanity-check the schema, not just existence).

## Phase 3 — rtk-off control arm

Full SWE-bench Lite, `--slice 0:20`, `--environment-class docker`
(stock), model/seed/limits frozen. Run first so any harness-side
surprise is caught without rtk in the loop.

Saves to `runs/rtk-off/`.

Exit criteria: 20 `preds.json` entries. `.traj.json` present for
every instance where env startup succeeded — instances that fail at
startup (`get_sb_environment` throws before `agent` is assigned) write
no `.traj.json`, only a `preds.json` entry with
`exit_status=<ExceptionType>` (Phase 0 finding 6). `runs/rtk-off/run.log`
exists with no uncaught tracebacks at the tail. Per-instance
`runs/rtk-off/startup/<id>.log` files exist (even if empty — absence
is a wiring bug).

## Phase 4 — rtk-on arm

Same model, seed, limits, slice. `--environment-class rtk_docker`.
Saves to `runs/rtk-on/`. Diff one paired instance's trajectory against
its rtk-off twin to confirm pitfall #4 specifically:
`actions[].command` identical between arms, `output` differs.

Exit criteria: 20 paired trajectories. No `command not found` in any
observation. `runs/rtk-on/rtk_rewrite.log` has one entry per rtk-fired
rewrite across all 20 instances (count matches the trajectory
`action.command` strings rtk would handle). `runs/rtk-on/run.log` and
per-instance `runs/rtk-on/startup/<id>.log` exist with no uncaught
tracebacks. For one paired instance, diffed against its rtk-off twin:
`actions[].command` identical, `observation.output` differs where rtk
fired.

## Phase 5 — Measure

- Run `trajectory_tokens` (§6) over both dirs.
- Produce per-instance deltas, medians/means.
- Submit both `preds.json` to sb-cli for resolved / submitted.
- Write sb-cli's JSON output to `runs/<arm>/sb_result.json` (Logging
  invariants per-phase #3).
- Fill the §6 table.

Exit criteria: the §6 table with real numbers, sb_result.json present
on both arms, and a one-paragraph read.