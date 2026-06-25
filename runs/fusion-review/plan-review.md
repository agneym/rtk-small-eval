Verdict: The plan is well-structured and addresses key aspects of an A/B test for `rtk`. The phased approach is sensible for mitigating risks. The logging and measurement strategies are clear.

Blockers:
1.  **`rtk rewrite` exit code 3+stdout behavior:** The plan states "if exit 3+stdout run rewritten command in container, otherwise original". This implies that `rtk rewrite` might exit with codes other than 0 for success or 1/2 for failure, and specifically that exit code 3 *with* stdout indicates a successful rewrite. This needs explicit confirmation from the `rtk` documentation or source code. If `rtk rewrite` only exits with 0 for success and non-zero for failure, then the logic needs to be adjusted.
2.  **`env_startup_command unusable`:** Phase0 verified this. This is a significant limitation for setting up the environment for `rtk` within the container. A workaround or alternative method for environment setup needs to be explicitly defined and tested.
3.  **`trajectory failure caveats`:** Phase0 verified this. The nature of these caveats and how they will be handled or accounted for in the analysis needs to be detailed. For example, if trajectories fail due to `rtk` issues, how will this impact the token measurement or correctness evaluation?

Required changes before running:
1.  **Clarify `rtk rewrite` exit code logic:** Define precisely what `rtk rewrite` exit codes mean and adjust the conditional logic for running the rewritten command accordingly. If exit code 3 is indeed a success with a rewritten command, document this behavior.
2.  **Address `env_startup_command unusable`:** Propose and implement an alternative mechanism for `rtk` setup within the Docker container, given that `env_startup_command` is unusable. This could involve modifying the Dockerfile, using a different entrypoint script, or another method.
3.  **Detail `trajectory failure caveats` handling:** Document the specific "trajectory failure caveats" and outline the strategy for handling them during the experiment and analysis. This might involve filtering out failed runs, analyzing the failure modes, or adjusting metrics.
4.  **Specify `run_id` serialization:** While `run_id` is mentioned as serialized in trajectories, the exact mechanism (e.g., as part of `extra` in a message, or a top-level field) should be specified for clarity and consistency.

Non-blocking recommendations:
1.  **Add `rtk` version to logs:** In addition to the `rtk` binary verification during Docker startup, consider logging the exact `rtk` version used in the CSV output for each run. This provides valuable context for analysis and reproducibility.
2.  **Consider a small pilot run for `rtk-on`:** Before running the full 0:20 slice for `rtk-on`, a very small pilot (e.g., 1-2 tasks) could be beneficial to catch any unforeseen issues specific to the `rtk-on` configuration that might have been missed in Phase2 local smoke testing.
3.  **Define success metrics for Phase2/3/4:** While the overall goal is A/B testing, defining clear success criteria for each phase (e.g., "Phase2 local smoke: `rtk` binary successfully copied and verified, `rtk rewrite` command executes without errors for a sample input") would make progress tracking more robust.
4.  **Consider logging `rtk` stderr:** The plan mentions logging `stdout` for `rtk rewrite` when exit code 3 occurs. It might be beneficial to also log `stderr` for all `rtk rewrite` executions, especially for non-zero exit codes, to aid in debugging.
5.  **Document `rtk` configuration:** If `rtk` has any configurable parameters, ensure that the specific configuration used for the experiment is documented.

Specific doc/command edits:
1.  **Update `RtkDockerEnvironment.execute` logic documentation:**
    *   Current: "if exit 3+stdout run rewritten command in container, otherwise original"
    *   Proposed: "The `RtkDockerEnvironment.execute` method will first attempt to execute `rtk rewrite <original_command>`.
        *   If `rtk rewrite` exits with code 3 and produces stdout, the stdout will be treated as the `rewritten_command`, and `rewritten_command` will be executed in the container.
        *   In all other cases (e.g., exit code 0, 1, 2, or 3 without stdout), the `original_command` will be executed in the container.
        *   The `rtk` exit code, original command, and rewritten command (if applicable) will be logged."
2.  **Add a section on `env_startup_command` workaround:**
    *   "**Workaround for `env_startup_command`:** Due to `env_startup_command` being unusable, the `rtk` binary will be made available in the container by [**INSERT SPECIFIC WORKAROUND HERE, e.g., modifying the Dockerfile to include `COPY vendor/rtk /usr/local/bin/rtk` or using a custom entrypoint script that sets up the environment**]."
3.  **Add a section on `trajectory failure caveats` handling:**
    *   "**Handling Trajectory Failure Caveats:** [**INSERT SPECIFIC STRATEGY HERE, e.g., "Runs where the agent fails to produce a valid `preds.json` will be excluded from correctness metrics but included in token usage analysis. Specific failure modes will be categorized and analyzed separately."**]"
4.  **Update CSV log format documentation:**
    *   Current: "log CSV timestamp,run_id,exit_code,original,rewritten"
    *   Proposed: "log CSV timestamp,run_id,rtk_exit_code,original_command,rewritten_command,rtk_version" (adding `rtk_version` and clarifying `exit_code` to `rtk_exit_code`).
5.  **Add `rtk` version verification command:**
    *   In the Docker startup script, after copying the binary, add: `/usr/local/bin/rtk --version` and capture its output for logging.