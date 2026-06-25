#!/usr/bin/env bash
# Batch run: 30 SWE-bench Lite instances (6 slices of 5), paired rtk-off/rtk-on.
# Uses DeepSeek V4 Flash, fair eval harness (swebench_rtk.yaml).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  [ -f /tmp/deepseek_key.sh ] && source /tmp/deepseek_key.sh
fi
if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  echo "DEEPSEEK_API_KEY not set" >&2; exit 1
fi

MODEL="deepseek/deepseek-v4-flash"
PYTHON=".venv/bin/python"
OFF_DIR="runs/fair/rtk-off"
ON_DIR="runs/fair/rtk-on"

SLICES=("0:5" "5:10" "10:15" "15:20" "20:25" "25:30")
START_TIME=$(date +%s)

for slice in "${SLICES[@]}"; do
  echo "=== $(date): slice $slice ==="

  # rtk-off
  echo "  rtk-off → $OFF_DIR"
  $PYTHON -m minisweagent.run.benchmarks.swebench \
    --subset lite --split test --slice "$slice" \
    --model "$MODEL" \
    --environment-class docker \
    -c swebench.yaml \
    -c agent.step_limit=100 \
    -c model.cost_tracking=ignore_errors \
    -o "$OFF_DIR"

  # rtk-on
  echo "  rtk-on → $ON_DIR"
  $PYTHON -m minisweagent.run.benchmarks.swebench \
    --subset lite --split test --slice "$slice" \
    --model "$MODEL" \
    --environment-class rtk_env.RtkDockerEnvironment \
    -c swebench.yaml \
    -c swebench_rtk.yaml \
    -c agent.step_limit=100 \
    -c model.cost_tracking=ignore_errors \
    -c "environment.rtk_rewrite_log_path=$ON_DIR/rtk_rewrite.log" \
    -o "$ON_DIR"

  echo "  elapsed: $(( ($(date +%s) - START_TIME) / 60 ))m"
done

echo "=== Done in $(( ($(date +%s) - START_TIME) / 60 ))m ==="
echo ""
$PYTHON runs/measure_paired.py --off "$OFF_DIR" --on "$ON_DIR"
