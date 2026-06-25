#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
source /tmp/deepseek_key.sh
: "${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY must be set in the environment}"
export DEEPSEEK_API_KEY
export DEEPSEEK_API_BASE="${DEEPSEEK_API_BASE:-https://api.deepseek.com/beta}"
unset ANTHROPIC_API_BASE ANTHROPIC_API_KEY || true
mkdir -p runs/deepseek-v4-flash-slice20-25/rtk-off
exec mise exec -- mini-extra swebench \
  --subset lite --split test --slice 20:25 \
  --model deepseek/deepseek-v4-flash \
  --environment-class docker \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -o runs/deepseek-v4-flash-slice20-25/rtk-off \
  --workers 1 \
  "$@"
