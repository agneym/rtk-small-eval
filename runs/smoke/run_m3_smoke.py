"""Headless mini-swe-agent smoke run: Minimax M3 via opencode-go.

Exercises the full mini stack (LitellmModel + DefaultAgent + LocalEnvironment)
against the Anthropic-format opencode-go endpoint, with a hard step limit and
trajectory dump. This is the cheap "does mini work with M3" check before
committing to the Phase 0/1 work in docs/rtk-harness-phases.md.

Env (set authoritatively here):
  OPENCODE_GO_API_KEY  (read from the caller's env)
  ANTHROPIC_API_KEY    (aliased to OPENCODE_GO_API_KEY)
  ANTHROPIC_API_BASE   (https://opencode.ai/zen/go)

Uses the library's built-in `mini` config (tool-call-oriented system +
instance templates) rather than the markdown-oriented `default.yaml`,
so M3 emits OpenAI-format tool_calls instead of ```mswea_bash_command
blocks. Same config-loading path the Phase 3 harness will use.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from minisweagent.agents.default import DefaultAgent
from minisweagent.config import get_config_from_spec
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.litellm_model import LitellmModel

MODEL = "anthropic/minimax-m3"
STEP_LIMIT = 6
TASK = (
    "You are in a scratch directory. Use the bash tool to run: "
    "echo hello_from_m3_smoke\n"
    "Then print an exit message."
)


def main() -> int:
    key = os.environ.get("OPENCODE_GO_API_KEY")
    if not key:
        print("OPENCODE_GO_API_KEY not set", file=sys.stderr)
        return 2
    # litellm's anthropic/ provider reads ANTHROPIC_API_KEY + ANTHROPIC_API_BASE.
    # Set authoritatively so the run is reproducible regardless of caller env.
    os.environ["ANTHROPIC_API_KEY"] = key
    os.environ["ANTHROPIC_API_BASE"] = "https://opencode.ai/zen/go"

    scratch = Path(__file__).parent / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)

    # `mini` is the tool-call-oriented built-in config (system + instance
    # templates that ask for bash tool calls, not ```mswea_bash_command blocks).
    # Override only step_limit; leave everything else to the library config so
    # upstream improvements to mini.yaml flow through without edits here.
    agent_cfg = get_config_from_spec("mini")["agent"]
    agent_cfg["step_limit"] = STEP_LIMIT

    agent = DefaultAgent(
        LitellmModel(
            model_name=MODEL,
            cost_tracking="ignore_errors",
        ),
        LocalEnvironment(cwd=str(scratch)),
        **agent_cfg,
    )
    run_result = agent.run(TASK)

    out = Path(__file__).with_suffix(".traj.json")
    data = agent.save(out)
    print("trajectory:", out)
    print("exit_status:", run_result.get("exit_status"))
    print("submission:", json.dumps(run_result.get("submission", "")))
    print("cost:", data["info"]["model_stats"]["instance_cost"])
    print("api_calls:", data["info"]["model_stats"]["api_calls"])
    n_actions = sum(
        len(m.get("extra", {}).get("actions") or [])
        for m in data.get("messages", [])
    )
    print("n_actions:", n_actions)
    # Last few assistant turns (open the .traj.json for full fidelity).
    for m in data.get("messages", [])[-6:]:
        role = m.get("role")
        content = m.get("content")
        if isinstance(content, list):
            content = " ".join(
                b.get("text", "") if isinstance(b, dict) else str(b)
                for b in content
            )
        print(f"[{role}] {str(content)[:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())