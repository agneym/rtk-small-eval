#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
: "${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY must be set in the environment}"
export DEEPSEEK_API_KEY
export DEEPSEEK_API_BASE="${DEEPSEEK_API_BASE:-https://api.deepseek.com/beta}"
unset ANTHROPIC_API_BASE ANTHROPIC_API_KEY || true
mkdir -p runs/deepseek-v4-flash-slice10-15/rtk-on
exec mise exec -- mini-extra swebench \
  --subset lite --split test --slice 10:15 \
  --model deepseek/deepseek-v4-flash \
  --environment-class rtk_env.RtkDockerEnvironment \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -c environment.rtk_rewrite_log_path=runs/deepseek-v4-flash-slice10-15/rtk-on/rtk_rewrite.log \
  -o runs/deepseek-v4-flash-slice10-15/rtk-on \
  --workers 1 \
  "$@"
