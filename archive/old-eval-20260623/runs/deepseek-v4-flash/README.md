# DeepSeek V4 Flash next-5 SWE-bench Lite run

Model: `deepseek/deepseek-v4-flash` via DeepSeek API/LiteLLM.
API key: `DEEPSEEK_API_KEY` from the environment.
Default API base: `https://api.deepseek.com/beta` (override with `DEEPSEEK_API_BASE`).

Instances: SWE-bench Lite test `--slice 5:10`:

- `astropy__astropy-7746`
- `django__django-10914`
- `django__django-10924`
- `django__django-11001`
- `django__django-11019`

Run both paired arms:

```bash
./runs/deepseek-v4-flash/run_both_next5.sh
```

Run one arm only:

```bash
./runs/deepseek-v4-flash/run_rtk_off_next5.sh 2>&1 | tee runs/deepseek-v4-flash/rtk-off/run.log
./runs/deepseek-v4-flash/run_rtk_on_next5.sh 2>&1 | tee runs/deepseek-v4-flash/rtk-on/run.log
```

Measure paired trajectory tokens after both arms finish:

```bash
python runs/measure_paired.py \
  --off runs/deepseek-v4-flash/rtk-off \
  --on runs/deepseek-v4-flash/rtk-on
```
