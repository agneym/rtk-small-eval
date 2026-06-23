#!/usr/bin/env python3
"""Run a command with a wall-clock timeout and kill its process group on expiry."""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-seconds", type=float, required=True)
    parser.add_argument("--grace-seconds", type=float, default=30.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("missing command after --")

    start = time.time()
    proc = subprocess.Popen(command, start_new_session=True)
    try:
        return proc.wait(timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(
            f"\n[timeout] {elapsed:.0f}s elapsed; sending SIGTERM to process group {proc.pid}: "
            + " ".join(command),
            file=sys.stderr,
            flush=True,
        )
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            return proc.wait(timeout=args.grace_seconds)
        except subprocess.TimeoutExpired:
            print(
                f"[timeout] still running after {args.grace_seconds:.0f}s grace; sending SIGKILL",
                file=sys.stderr,
                flush=True,
            )
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            return 124


if __name__ == "__main__":
    raise SystemExit(main())
