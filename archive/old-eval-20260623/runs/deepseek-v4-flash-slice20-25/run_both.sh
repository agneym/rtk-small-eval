#!/usr/bin/env bash
set -uo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
mkdir -p runs/deepseek-v4-flash-slice20-25/rtk-off runs/deepseek-v4-flash-slice20-25/rtk-on

TIMEOUT_SECONDS="${RUN_TIMEOUT_SECONDS:-7200}"

echo "[run] slice 20:25; per-arm timeout: ${TIMEOUT_SECONDS}s"

run_arm() {
  local arm="$1"
  shift
  local log="runs/deepseek-v4-flash-slice20-25/${arm}/run.log"
  echo "[run] starting ${arm} at $(date); log=${log}"
  python3 scripts/run_with_timeout.py --timeout-seconds "${TIMEOUT_SECONDS}" -- "$@" 2>&1 | tee "${log}"
  local status=${PIPESTATUS[0]}
  echo "[run] finished ${arm} at $(date) with status ${status}" | tee -a "${log}"
  return "${status}"
}

status_off=0
status_on=0
run_arm rtk-off ./runs/deepseek-v4-flash-slice20-25/run_rtk_off.sh "$@" || status_off=$?
run_arm rtk-on ./runs/deepseek-v4-flash-slice20-25/run_rtk_on.sh "$@" || status_on=$?

printf '[run] done; rtk-off=%s rtk-on=%s\n' "${status_off}" "${status_on}"
if [[ "${status_off}" != 0 || "${status_on}" != 0 ]]; then
  exit 1
fi
