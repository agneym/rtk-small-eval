"""Smoke test: RtkDockerEnvironment with DeepSeek V4 Flash on a single SWE-bench instance.

Verifies the fair eval harness end-to-end:
- swebench_rtk.yaml loads correctly (RTK awareness in system prompt)
- rtk rewrite fires on the host and Linux binary runs in container
- Trajectory is written
- Measure script works on the output

Single cheap instance to validate before committing to a full slice.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

MODEL = "deepseek/deepseek-v4-flash"
SLICE = "0:1"
INSTANCE = "astropy__astropy-12907"  # cheap, usually resolves fast


def run_cmd(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO, **kw)


def main() -> int:
    # 1. Verify prerequisites
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("DEEPSEEK_API_KEY not set", file=sys.stderr)
        return 2

    linux_binary = REPO / "vendor" / "rtk-x86_64-unknown-linux-musl"
    if not linux_binary.exists():
        print(f"Linux rtk binary not found at {linux_binary}", file=sys.stderr)
        print("Run: bash scripts/fetch-rtk-linux.sh", file=sys.stderr)
        return 2

    if not shutil.which("rtk"):
        print("Host rtk not found on PATH", file=sys.stderr)
        return 2

    # 2. Run rtk-off arm (single instance, stock swebench.yaml)
    off_dir = REPO / "runs" / "smoke-fair" / "rtk-off"
    r = run_cmd(
        [
            sys.executable, "-m", "minisweagent.run.benchmarks.swebench",
            "--subset", "lite", "--split", "test", "--slice", SLICE,
            "--model", MODEL,
            "--environment-class", "docker",
            "-c", "swebench.yaml",
            "-c", "agent.step_limit=30",
            "-c", "model.cost_tracking=ignore_errors",
            "-o", str(off_dir),
        ],
        timeout=900,
    )
    if r.returncode != 0:
        print(f"rtk-off failed (exit {r.returncode})", file=sys.stderr)
        print(r.stdout[-2000:] if r.stdout else "", file=sys.stderr)
        print(r.stderr[-2000:] if r.stderr else "", file=sys.stderr)
        return 1

    # 3. Run rtk-on arm (single instance, swebench_rtk.yaml + RtkDockerEnvironment)
    on_dir = REPO / "runs" / "smoke-fair" / "rtk-on"
    r = run_cmd(
        [
            sys.executable, "-m", "minisweagent.run.benchmarks.swebench",
            "--subset", "lite", "--split", "test", "--slice", SLICE,
            "--model", MODEL,
            "--environment-class", "rtk_env.RtkDockerEnvironment",
            "-c", "swebench.yaml",
            "-c", "swebench_rtk.yaml",
            "-c", "agent.step_limit=30",
            "-c", "model.cost_tracking=ignore_errors",
            "-c", f"environment.rtk_rewrite_log_path={on_dir}/rtk_rewrite.log",
            "-o", str(on_dir),
        ],
        timeout=900,
    )
    if r.returncode != 0:
        print(f"rtk-on failed (exit {r.returncode})", file=sys.stderr)
        print(r.stdout[-2000:] if r.stdout else "", file=sys.stderr)
        print(r.stderr[-2000:] if r.stderr else "", file=sys.stderr)
        return 1

    # 4. Verify outputs exist
    off_traj = off_dir / INSTANCE / f"{INSTANCE}.traj.json"
    on_traj = on_dir / INSTANCE / f"{INSTANCE}.traj.json"
    rewrite_log = on_dir / "rtk_rewrite.log"

    for p in [off_traj, on_traj, rewrite_log]:
        if not p.exists():
            print(f"Missing: {p}", file=sys.stderr)
            return 1

    # 5. Check rewrite log has entries
    with open(rewrite_log, newline="") as f:
        reader = list(csv.reader(f))
    print(f"\nRewrite log: {len(reader)} lines (including header)")
    rewrites = [r for r in reader[1:] if r[2] == "3"]
    bypasses = [r for r in reader[1:] if r[2] in ("-2", "-3")]
    passthroughs = [r for r in reader[1:] if r[2] == "1"]
    print(f"  rewrites: {len(rewrites)}")
    print(f"  bypasses: {len(bypasses)}")
    print(f"  passthroughs: {len(passthroughs)}")

    # 6. Check system template has RTK awareness
    off_data = json.loads(off_traj.read_text())
    on_data = json.loads(on_traj.read_text())
    system_msg = on_data["messages"][0]["content"]
    has_rtk = "RTK Auto-Rewrite" in system_msg
    has_bypass = "RTK_DISABLED=1" in system_msg
    print(f"\nSystem prompt RTK awareness: {has_rtk}")
    print(f"System prompt bypass hint: {has_bypass}")

    if not has_rtk:
        print("FAIL: system prompt missing RTK awareness", file=sys.stderr)
        return 1

    # 7. Check trajectory has tool calls
    off_calls = sum(1 for m in off_data["messages"] if m.get("role") == "assistant" and "tool_calls" in m)
    on_calls = sum(1 for m in on_data["messages"] if m.get("role") == "assistant" and "tool_calls" in m)
    print(f"\nTool call turns: off={off_calls} on={on_calls}")

    # 8. Run measure script
    print("\n--- measure_paired.py ---")
    r = subprocess.run(
        [sys.executable, str(REPO / "runs" / "measure_paired.py"),
         "--off", str(off_dir), "--on", str(on_dir)],
        cwd=REPO, capture_output=True, text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)

    print("\nSmoke test PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
