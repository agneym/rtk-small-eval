"""Compute paired token stats for two mini-swe-agent SWE-bench output dirs."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

# USD per 1M tokens. Add models as needed.
# The model_name key matches info.config.model.model_name from the trajectory.
PRICING: dict[str, dict[str, float]] = {
    "deepseek/deepseek-v4-flash": {"prompt": 0.14, "completion": 0.28},
    "deepseek/deepseek-chat": {"prompt": 0.14, "completion": 0.28},
    "anthropic/minimax-m3": {"prompt": 0.50, "completion": 2.00},
    "anthropic/claude-sonnet-4-5-20250929": {"prompt": 3.00, "completion": 15.00},
}


def cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    p = PRICING.get(model_name)
    if p is None:
        return None
    return (prompt_tokens * p["prompt"] + completion_tokens * p["completion"]) / 1_000_000


def trajectory_stats(path: Path) -> dict:
    data = json.loads(path.read_text())
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
    model_name = data.get("info", {}).get("config", {}).get("model", {}).get("model_name", "")
    return {
        "instance_id": data.get("info", {}).get("instance_id", path.stem),
        "exit_status": data.get("exit_status"),
        "model_name": model_name,
        "n_calls": n_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost": cost(model_name, prompt_tokens, completion_tokens),
    }


def find_traj(root: Path, instance_id: str) -> Path:
    candidates = [
        root / instance_id / f"{instance_id}.traj.json",
        root / f"{instance_id}.traj.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = list(root.glob(f"**/{instance_id}.traj.json"))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(f"Could not uniquely find trajectory for {instance_id!r} under {root}")


def trajectory_instance_id(path: Path) -> str:
    return path.name.removesuffix(".traj.json")


def infer_instances(off_dir: Path, on_dir: Path) -> list[str]:
    off_ids = {trajectory_instance_id(p) for p in off_dir.glob("**/*.traj.json")}
    on_ids = {trajectory_instance_id(p) for p in on_dir.glob("**/*.traj.json")}
    return sorted(off_ids & on_ids)


def pct_delta(old: float, new: float) -> float:
    return ((new - old) / old * 100) if old else 0.0


def fmt_cost(c: float | None) -> str:
    if c is None:
        return "N/A".rjust(8)
    return f"${c:>7.4f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--off", type=Path, required=True, help="rtk-off output directory")
    parser.add_argument("--on", type=Path, required=True, help="rtk-on output directory")
    parser.add_argument("--instances", nargs="*", help="Instance IDs; defaults to paired trajectories")
    parser.add_argument(
        "--pricing", type=Path,
        help="JSON file mapping model_name → {prompt, completion} (USD per 1M tokens). "
             "Merged with built-in PRICING dict; file wins on conflict.",
    )
    args = parser.parse_args()

    pricing = dict(PRICING)
    if args.pricing:
        pricing |= json.loads(args.pricing.read_text())

    instances = args.instances or infer_instances(args.off, args.on)
    rows = []
    for iid in instances:
        off = trajectory_stats(find_traj(args.off, iid))
        on = trajectory_stats(find_traj(args.on, iid))
        rows.append({"instance_id": iid, "off": off, "on": on})

    # Per-instance table
    header = (
        f"{'instance_id':<30} {'off_cost':>8} {'on_cost':>8} {'delta_cost':>10} "
        f"{'off_tok':>10} {'on_tok':>10} {'delta_tok':>10} {'tok%':>8} "
        f"{'off_call':>8} {'on_call':>8}"
    )
    print(header)
    for r in rows:
        off = r["off"]
        on = r["on"]
        off_t = off["total_tokens"]
        on_t = on["total_tokens"]
        tok_delta = on_t - off_t
        cost_delta_str = ""
        if off["cost"] is not None and on["cost"] is not None:
            cost_delta_str = f"${on['cost'] - off['cost']:>+9.4f}"
        else:
            cost_delta_str = "N/A".rjust(10)
        print(
            f"{r['instance_id']:<30} {fmt_cost(off['cost'])} {fmt_cost(on['cost'])} {cost_delta_str} "
            f"{off_t:>10} {on_t:>10} {tok_delta:>+10} {pct_delta(off_t, on_t):>+7.1f}% "
            f"{off['n_calls']:>8} {on['n_calls']:>8}"
        )

    if not rows:
        return

    # Aggregate summary
    def print_agg(label: str, key: str, fmt_spec: str = ",.0f") -> None:
        off_vals = [r["off"][key] for r in rows]
        on_vals = [r["on"][key] for r in rows]
        off_sum = sum(off_vals)
        on_sum = sum(on_vals)
        off_med = statistics.median(off_vals)
        on_med = statistics.median(on_vals)
        print(f"\n{label}:")
        print(f"  total   off={off_sum:{fmt_spec}}  on={on_sum:{fmt_spec}}  delta={pct_delta(off_sum, on_sum):+.1f}%")
        print(f"  median  off={off_med:{fmt_spec}}  on={on_med:{fmt_spec}}  delta={pct_delta(off_med, on_med):+.1f}%")

    print_agg("total_tokens", "total_tokens")
    print_agg("n_calls", "n_calls")

    # Cost aggregates (only if pricing available)
    cost_rows = [r for r in rows if r["off"]["cost"] is not None and r["on"]["cost"] is not None]
    if cost_rows:
        print_agg("cost (USD)", "cost", fmt_spec=".4f")
        off_total_cost = sum(r["off"]["cost"] for r in cost_rows)
        on_total_cost = sum(r["on"]["cost"] for r in cost_rows)
        print(f"  total cost delta: ${on_total_cost - off_total_cost:+.4f}")
    else:
        print("\ncost: N/A (no pricing for model; see --pricing)")


if __name__ == "__main__":
    main()
