"""rtk-aware mini-swe-agent environment subclasses.

Two subclasses, one per execution surface:
- `RtkDockerEnvironment`  — Path A (SWE-bench score path). Rewrites on
  the host, injects a Linux rtk binary into the container at startup.
- `RtkLocalEnvironment`  — Path C (local smoke, not scored). Rewrites
  on the host; the rewritten command runs via the host rtk binary.

Both reuse `RtkMixin` for the `rtk rewrite` call and the per-decision
CSV rewrite log.

Phase 0 findings applied:
- Host rtk is Mach-O arm64; the Docker path needs a Linux x86_64 musl
  binary (`rtk_linux_binary`) `docker cp`'d into the container. The
  local path uses the host rtk for both rewrite *and* execution.
- `env_startup_command` can't inject rtk (no `{container_name}` var,
  `StrictUndefined`; runs inside the container where `docker cp` can't
  reach the host daemon). Injection happens in `_start_container`.
- `ENV_CLASSES` does not exist. Launch with
  `--environment-class rtk_env.RtkDockerEnvironment` (or
  `RtkLocalEnvironment`) — run from the repo root so `rtk_env` is importable; `get_environment_class` resolves the full
  dotted path.

No harness monkey-patching. The rewrite log uses a per-env `run_id`
(uuid4) as the join key, not `instance_id`. `run_id` lives on the Config,
so it lands in every trajectory's `info.config.environment.run_id`
automatically (both base classes' `serialize()` dump the config).
Post-processing groups `rtk_rewrite.log` lines by `run_id` and maps to
`instance_id` via the trajectory — no patch of `get_sb_environment`,
no agent subclass, no CLI flag, no upstream edit needed. Works
identically for the Docker and Local arms.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import Field

from minisweagent.environments.docker import (
    DockerEnvironment,
    DockerEnvironmentConfig,
)
from minisweagent.environments.local import (
    LocalEnvironment,
    LocalEnvironmentConfig,
)


# ---------------------------------------------------------------------------
# Mixin: the rtk rewrite chokepoint + rewrite log. Shared by Docker and Local.
# ---------------------------------------------------------------------------


class RtkMixin:
    """Shared `rtk rewrite` + rewrite-log logic for both env subclasses.

    Expects `self.config` to expose `rtk_enabled`, `rtk_path`,
    `rtk_rewrite_timeout`, `rtk_rewrite_log_path`, `run_id` (all defined
    on both Config subclasses below). `self.logger` comes from the base
    env class via MRO.
    """

    def _rewrite(self, command: str) -> tuple[str, int, str]:
        """Run `rtk rewrite <command>` on the host.

        Returns (effective_command, rtk_exit_code, rewritten_or_empty).
        - exit 3 + non-empty stdout → rewritten command, run that.
        - anything else             → passthrough, run the original.
        Defensive: exit 0 with empty stdout is also passthrough (doc §1;
        `--help` claiming exit 0 is stale).
        """
        if not command.strip():
            return command, -1, ""
        try:
            r = subprocess.run(
                [self.config.rtk_path, "rewrite", command],
                capture_output=True,
                text=True,
                timeout=self.config.rtk_rewrite_timeout,
            )
        except Exception as e:
            self.logger.warning(f"rtk rewrite failed ({e!r}); passthrough")
            return command, -1, ""
        rewritten = r.stdout.strip() if r.returncode == 3 and r.stdout and r.stdout.strip() else ""
        effective = rewritten if rewritten else command
        return effective, r.returncode, rewritten

    def _append_rewrite_log(self, exit_code: int, original: str, rewritten: str) -> None:
        path = self.config.rtk_rewrite_log_path
        if not path:
            return
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        write_header = not p.exists()
        with p.open("a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["timestamp", "run_id", "exit_code", "original", "rewritten"])
            w.writerow(
                [
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    self.config.run_id,
                    exit_code,
                    original,
                    rewritten,
                ]
            )

    def _rtk_wrap_action(self, action: dict) -> dict:
        """Shared execute() prelude. Returns the (possibly-new) action dict.

        When `rtk_enabled` is False the caller short-circuits to
        `super().execute(action)` without touching this.
        """
        original = action.get("command", "")
        effective, exit_code, rewritten = self._rewrite(original)
        if effective is not original:
            action = {**action, "command": effective}
        # Log every decision rtk actually saw (non-empty input). A passthrough
        # (exit 1) is still a decision — record it so "rtk didn't touch this"
        # is distinguishable from "rtk never saw it".
        if original.strip():
            self._append_rewrite_log(exit_code, original, rewritten)
        return action


# ---------------------------------------------------------------------------
# Docker (Path A)
# ---------------------------------------------------------------------------


class RtkDockerEnvironmentConfig(DockerEnvironmentConfig):
    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    """Per-env uuid4. Generated at config construction so every trajectory's
    `info.config.environment.run_id` is populated by the base class's
    `serialize()`. Post-processing joins the rtk rewrite log (`run_id`
    column) to trajectories by this key — no harness patching."""

    rtk_enabled: bool = True
    """Master switch. False = behaviourally identical to DockerEnvironment."""

    rtk_path: str = shutil.which("rtk") or "rtk"
    """Host rtk binary used for `rtk rewrite` (Mach-O on this machine)."""

    rtk_linux_binary: str = "vendor/rtk-x86_64-unknown-linux-musl"
    """Linux x86_64 musl rtk binary injected into the container via
    `docker cp`. NOT the host Mach-O binary — that fails with
    `Exec format error` inside the container."""

    rtk_container_path: str = "/usr/local/bin/rtk"
    """Where the Linux rtk binary lands inside the container."""

    rtk_rewrite_timeout: float = 5.0
    """Per-call timeout for `rtk rewrite` on the host."""

    rtk_rewrite_log_path: str = ""
    """Where to append one CSV line per rewrite decision. Empty disables
    logging. Default is set at launch time (e.g. runs/rtk-on/rtk_rewrite.log)."""


class RtkDockerEnvironment(RtkMixin, DockerEnvironment):
    def __init__(self, *, config_class: type = RtkDockerEnvironmentConfig, **kw):
        super().__init__(config_class=config_class, **kw)

    def _start_container(self) -> None:
        # Let the base class launch the container and set self.container_id.
        super()._start_container()
        assert self.container_id is not None, "super()._start_container set no container_id"
        if not self.config.rtk_enabled:
            return
        src = self.config.rtk_linux_binary
        dst = self.config.rtk_container_path
        cid = self.container_id
        cp = subprocess.run(
            [self.config.executable, "cp", src, f"{cid}:{dst}"],
            capture_output=True,
            text=True,
        )
        if cp.returncode != 0:
            self.logger.error(
                f"rtk injection: docker cp failed: {cp.stderr.strip() or cp.stdout.strip()}"
            )
            raise RuntimeError(f"docker cp of rtk binary failed: {cp.stderr.strip()}")
        chmod = subprocess.run(
            [self.config.executable, "exec", cid, "chmod", "+x", dst],
            capture_output=True,
            text=True,
        )
        if chmod.returncode != 0:
            self.logger.error(
                f"rtk injection: chmod +x failed: {chmod.stderr.strip() or chmod.stdout.strip()}"
            )
            raise RuntimeError(f"chmod +x of rtk binary failed: {chmod.stderr.strip()}")
        # Verify rtk is actually executable in the container (pitfall #1 / Phase 4
        # guard). Fail fast rather than silently turning every rewrite into
        # "command not found".
        ver = subprocess.run(
            [self.config.executable, "exec", cid, dst, "--version"],
            capture_output=True,
            text=True,
        )
        if ver.returncode != 0:
            raise RuntimeError(
                f"rtk not executable in container after cp: {ver.stderr.strip() or ver.stdout.strip()}"
            )
        self.logger.info(f"rtk {ver.stdout.strip()} injected into {cid}")

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        if not self.config.rtk_enabled:
            return super().execute(action, cwd=cwd, timeout=timeout)
        return super().execute(self._rtk_wrap_action(action), cwd=cwd, timeout=timeout)


# ---------------------------------------------------------------------------
# Local (Path C) — for smoke tests; not for SWE-bench scoring
# ---------------------------------------------------------------------------


class RtkLocalEnvironmentConfig(LocalEnvironmentConfig):
    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    """Per-env uuid4 (see RtkDockerEnvironmentConfig.run_id for rationale)."""

    rtk_enabled: bool = True
    """Master switch. False = behaviourally identical to LocalEnvironment."""

    rtk_path: str = shutil.which("rtk") or "rtk"
    """Host rtk binary used for BOTH `rtk rewrite` and running the rewritten
    command (e.g. `rtk git status`) on the host. Mach-O on this machine."""

    rtk_rewrite_timeout: float = 5.0
    """Per-call timeout for `rtk rewrite` on the host."""

    rtk_rewrite_log_path: str = ""
    """Where to append one CSV line per rewrite decision. Empty disables."""


class RtkLocalEnvironment(RtkMixin, LocalEnvironment):
    def __init__(self, *, config_class: type = RtkLocalEnvironmentConfig, **kw):
        super().__init__(config_class=config_class, **kw)

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        if not self.config.rtk_enabled:
            return super().execute(action, cwd=cwd, timeout=timeout)
        return super().execute(self._rtk_wrap_action(action), cwd=cwd, timeout=timeout)