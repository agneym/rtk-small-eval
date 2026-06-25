"""Phase 2 smoke test: RtkLocalEnvironment, rtk-on vs rtk-off, single repo.

Exercises the full mini-swe-agent stack (LitellmModel + DefaultAgent +
RtkLocalEnvironment) against THIS repo, with rtk_enabled=True and
rtk_enabled=False on the same task. Asserts the Phase 2 exit criteria
from docs/rtk-harness-phases.md:

  1. Both arms' serialized `actions[].command` strings are the model's
     original commands (the env must not mutate the caller's action
     dict — only the command actually executed).
  2. No `command not found` in any observation.
  3. runs/phase2-smoke/rtk-on/rtk_rewrite.log exists and has one line
     per non-empty command rtk inspected (including passthrough
     exit-code-1 decisions), with the documented CSV schema.

Uses OPENCODE_API_KEY from the environment (per user direction), aliased
to ANTHROPIC_API_KEY, with ANTHROPIC_API_BASE pointed at opencode-go so
litellm's anthropic/ provider routes Minimax M3 through the opencode-go
Anthropic-format endpoint.

Run:  mise exec -- python runs/phase2-smoke/run_smoke.py
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

from minisweagent.agents.default import DefaultAgent
from minisweagent.config import get_config_from_spec
from minisweagent.models.litellm_model import LitellmModel

# Make rtk_env importable from the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from rtk_env import RtkLocalEnvironment  # noqa: E402

MODEL = "anthropic/minimax-m3"
STEP_LIMIT = 8
RUN_DIR = Path(__file__).resolve().parent

# Single task used for BOTH arms. The commands `git status`, `ls`, and
# `echo` are deliberately picked so that:
#   - `git status` and `ls` are rtk-rewriteable (exit 3 → `rtk git status`,
#     `rtk ls`); we expect different observation output between arms only
#     for these.
#   - `echo` is passthrough (exit 1) on both arms.
TASK = (
    "You are in a git repository. Use the bash tool to run, in this order, "
    "each as its own tool call:\n"
    "  1. git status\n"
    "  2. ls\n"
    "  3. echo done_phase2_smoke\n"
    "Then print an exit message."
)


def _setup_env() -> str:
    key = os.environ.get("OPENCODE_API_KEY")
    if not key:
        print("OPENCODE_API_KEY not set", file=sys.stderr)
        sys.exit(2)
    # litellm's anthropic/ provider reads ANTHROPIC_API_KEY + ANTHROPIC_API_BASE.
    os.environ["ANTHROPIC_API_KEY"] = key
    os.environ["ANTHROPIC_API_BASE"] = "https://opencode.ai/zen/go"
    return key


def _new_env(*, rtk_enabled: bool, rewrite_log: Path):
    # `RtkLocalEnvironment.__init__` forwards kwargs to
    # `RtkLocalEnvironmentConfig(**kwargs)`, so we pass the config fields
    # directly rather than pre-building a config (avoids a double-model_dump
    # round-trip that would drop any non-serializable defaults).
    return RtkLocalEnvironment(
        cwd=str(REPO_ROOT),
        rtk_enabled=rtk_enabled,
        rtk_rewrite_log_path=str(rewrite_log),
    )


def _run_arm(arm: str) -> dict:
    arm_dir = RUN_DIR / arm
    arm_dir.mkdir(parents=True, exist_ok=True)
    rewrite_log = arm_dir / "rtk_rewrite.log"
    # Start each arm with a clean rewrite log so assertions are scoped.
    if rewrite_log.exists():
        rewrite_log.unlink()

    agent_cfg = get_config_from_spec("mini")["agent"]
    agent_cfg["step_limit"] = STEP_LIMIT
    agent_cfg["output_path"] = arm_dir / "trajectory.traj.json"

    env = _new_env(rtk_enabled=(arm == "rtk-on"), rewrite_log=rewrite_log)
    agent = DefaultAgent(
        LitellmModel(model_name=MODEL, cost_tracking="ignore_errors"),
        env,
        **agent_cfg,
    )
    run_result = agent.run(TASK)
    data = agent.save(agent_cfg["output_path"])
    data["exit_status"] = run_result.get("exit_status")
    data["submission"] = run_result.get("submission", "")
    return data


def _actions(data: dict) -> list[str]:
    out = []
    for m in data.get("messages", []):
        for a in m.get("extra", {}).get("actions") or []:
            if a.get("command") is not None:
                out.append(a["command"])
    return out


def _observations(data: dict) -> list[str]:
    out = []
    for m in data.get("messages", []):
        if m.get("role") == "tool":
            raw = m.get("extra", {}).get("raw_output", "")
            if raw is not None:
                out.append(str(raw))
            continue
        # non-tool user observations (e.g. format-error feedback) — skip
    return out


def _assert_exit_criteria(off: dict, on: dict) -> list[str]:
    failures: list[str] = []

    off_actions = _actions(off)
    on_actions = _actions(on)
    if off_actions != on_actions:
        failures.append(
            f"actions differ between arms:\n  off={off_actions}\n  on ={on_actions}"
        )
    # All actions must be the ORIGINAL model command, not an `rtk …` rewrite.
    for arm, acts in [("rtk-off", off_actions), ("rtk-on", on_actions)]:
        for c in acts:
            if c.startswith("rtk "):
                failures.append(
                    f"{arm}: serialized action is a rewrite, not the original: {c!r}"
                )

    # No `command not found` in any observation on either arm.
    for arm, data in [("rtk-off", off), ("rtk-on", on)]:
        for obs in _observations(data):
            if "command not found" in obs:
                failures.append(f"{arm}: observation contains 'command not found': {obs[:160]!r}")

    # rtk_rewrite.log: schema + one line per non-empty inspected command.
    log_path = RUN_DIR / "rtk-on" / "rtk_rewrite.log"
    if not log_path.exists():
        failures.append("rtk-on/rtk_rewrite.log missing")
    else:
        rows = list(csv.DictReader(log_path.open()))
        cols = {"timestamp", "run_id", "exit_code", "original", "rewritten"}
        if not rows:
            failures.append("rtk-on/rtk_rewrite.log has no data rows")
        else:
            got = set(rows[0].keys())
            if got != cols:
                failures.append(
                    f"rtk_rewrite.log schema mismatch: got {got}, want {cols}"
                )
            n_inspected = sum(1 for r in rows if r["original"].strip())
            if n_inspected == 0:
                failures.append("rtk_rewrite.log has no non-empty inspected commands")
            # Sanity: at least one rewrite (exit_code 3, non-empty rewritten)
            # and at least one passthrough (exit_code 1, empty rewritten).
            n_rewritten = sum(
                1 for r in rows if r["exit_code"] == "3" and r["rewritten"].strip()
            )
            n_passthrough = sum(
                1 for r in rows if r["exit_code"] == "1" and not r["rewritten"].strip()
            )
            if n_rewritten == 0:
                failures.append(
                    f"rtk_rewrite.log has no rewrite decisions (exit 3); rows={rows}"
                )
            if n_passthrough == 0:
                failures.append(
                    f"rtk_rewrite.log has no passthrough decisions (exit 1); rows={rows}"
                )

    return failures


def main() -> int:
    _setup_env()
    print(f"== Phase 2 smoke: {MODEL} against {REPO_ROOT}")
    print("== rtk-off arm")
    off = _run_arm("rtk-off")
    print(f"   exit_status={off['exit_status']}  actions={_actions(off)}")
    print("== rtk-on arm")
    on = _run_arm("rtk-on")
    print(f"   exit_status={on['exit_status']}  actions={_actions(on)}")

    failures = _assert_exit_criteria(off, on)
    print("\n== Phase 2 exit-criteria check")
    if failures:
        for f in failures:
            print("  FAIL:", f)
        return 1
    print("  PASS: actions identical between arms and all original (no `rtk …`)")
    print("  PASS: no 'command not found' in any observation")
    log = (RUN_DIR / "rtk-on" / "rtk_rewrite.log").read_text()
    print(f"  PASS: rtk_rewrite.log schema OK; rows:\n{log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())