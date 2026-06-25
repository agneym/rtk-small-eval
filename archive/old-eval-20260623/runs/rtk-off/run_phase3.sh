#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
export ANTHROPIC_API_KEY="${OPENCODE_API_KEY}"
export ANTHROPIC_API_BASE="https://opencode.ai/zen/go"
exec mise exec -- mini-extra swebench \
  --subset lite --split test --slice 0:5 \
  --model anthropic/minimax-m3 \
  --environment-class docker \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -o runs/rtk-off \
  --workers 1 \
  "$@"
