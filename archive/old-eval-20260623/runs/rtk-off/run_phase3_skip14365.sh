#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
export ANTHROPIC_API_KEY="${OPENCODE_API_KEY}"
export ANTHROPIC_API_BASE="https://opencode.ai/zen/go"
# Slice 0:5 minus astropy__astropy-14365: run 3 and 4 explicitly via filter.
exec mise exec -- mini-extra swebench \
  --subset lite --split test \
  --filter 'astropy__astropy-14995|astropy__astropy-6938' \
  --model anthropic/minimax-m3 \
  --environment-class docker \
  -c swebench.yaml \
  -c model.cost_tracking=ignore_errors \
  -o runs/rtk-off \
  --workers 1 \
  "$@"
