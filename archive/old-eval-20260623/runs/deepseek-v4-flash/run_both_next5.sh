#!/usr/bin/env bash
set -euo pipefail
cd /Users/agney/code/run-throughs/rtk-evaluation
mkdir -p runs/deepseek-v4-flash/rtk-off runs/deepseek-v4-flash/rtk-on

./runs/deepseek-v4-flash/run_rtk_off_next5.sh "$@" 2>&1 | tee runs/deepseek-v4-flash/rtk-off/run.log
./runs/deepseek-v4-flash/run_rtk_on_next5.sh "$@" 2>&1 | tee runs/deepseek-v4-flash/rtk-on/run.log
