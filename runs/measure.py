"""Compute paired token stats from rtk-off vs rtk-on trajectories."""
from __future__ import annotations

import json
import statistics
from pathlib import Path


def trajectory_tokens(path: Path) -> dict:
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
    return {
        "instance_id": data["info"].get("instance_id", path.stem),
        "exit_status": data.get("exit_status"),
        "n_calls": n_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    paired = ["astropy__astropy-12907", "astropy__astropy-14182", "astropy__astropy-14995", "astropy__astropy-6938"]
    rows = []
    for iid in paired:
        off = trajectory_tokens(root / "rtk-off" / iid / f"{iid}.traj.json")
        on = trajectory_tokens(root / "rtk-on" / iid / f"{iid}.traj.json")
        rows.append({"instance_id": iid, "off": off, "on": on})

    print(f"{'instance_id':<30} {'off_total':>10} {'on_total':>10} {'delta':>10} {'%':>8} {'off_calls':>9} {'on_calls':>8}")
    for r in rows:
        off_t = r["off"]["total_tokens"]
        on_t = r["on"]["total_tokens"]
        delta = on_t - off_t
        pct = (delta / off_t * 100) if off_t else 0
        print(
            f"{r['instance_id']:<30} {off_t:>10} {on_t:>10} {delta:>+10} {pct:>+7.1f}% {r['off']['n_calls']:>9} {r['on']['n_calls']:>8}"
        )

    for key in ["prompt_tokens", "completion_tokens", "total_tokens", "n_calls"]:
        off_vals = [r["off"][key] for r in rows]
        on_vals = [r["on"][key] for r in rows]
        off_med = statistics.median(off_vals)
        on_med = statistics.median(on_vals)
        off_mean = statistics.mean(off_vals)
        on_mean = statistics.mean(on_vals)
        print(f"\n{key}:")
        print(f"  median  off={off_med:,.0f} on={on_med:,.0f} delta={(on_med-off_med)/off_med*100:+.1f}%")
        print(f"  mean    off={off_mean:,.0f} on={on_mean:,.0f} delta={(on_mean-off_mean)/off_mean*100:+.1f}%")


if __name__ == "__main__":
    main()
