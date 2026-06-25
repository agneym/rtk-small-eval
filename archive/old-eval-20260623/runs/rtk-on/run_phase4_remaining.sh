#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
export ANTHROPIC_API_BASE="https://opencode.ai/zen/go"
export ANTHROPIC_API_KEY="${OPENCODE_API_KEY}"
# Run the remaining 3 instances that completed in rtk-off (skip 14365 which hung).
exec mise exec -- mini-extra swebench \
  --subset lite --split test \
  --filter 'astropy__astropy-14182|astropy__astropy-14995|astropy__astropy-6938' \
  --model anthropic/minimax-m3 \
  --environment-class rtk_env.RtkDockerEnvironment \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -c environment.rtk_rewrite_log_path=runs/rtk-on/rtk_rewrite.log \
  -o runs/rtk-on \
  --workers 1 \
  "$@"
