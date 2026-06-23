# Combined rtk evaluation summary (8 paired instances)

Generated: 2026-06-23 20:30:00

This summarizes the two completed paired pilots under `logs/run_evaluation/`: 4 Minimax M3 pairs and 4 DeepSeek V4 Flash pairs. The DeepSeek fifth candidate (`django__django-11019`) is excluded because rtk-off did not produce a trajectory or prediction, so it has no paired comparison.

## Evaluation-log locations

| cohort | rtk-off logs | rtk-on logs |
|---|---|---|
| Minimax M3 | `logs/run_evaluation/rtk-off-20260623/anthropic__minimax-m3/` | `logs/run_evaluation/rtk-on-20260623/anthropic__minimax-m3/` |
| DeepSeek V4 Flash | `logs/run_evaluation/rtk-off-deepseek-20260623/deepseek__deepseek-v4-flash/` | `logs/run_evaluation/rtk-on-deepseek-20260623/deepseek__deepseek-v4-flash/` |

## Per-instance results

| model | instance | off resolved | on resolved | off tokens | on tokens | delta | delta % | off calls | on calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `anthropic/minimax-m3` | `astropy__astropy-12907` | yes | yes | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 |
| `anthropic/minimax-m3` | `astropy__astropy-14182` | no | no | 2,040,992 | 609,360 | -1,431,632 | -70.1% | 82 | 43 |
| `anthropic/minimax-m3` | `astropy__astropy-14995` | yes | yes | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 |
| `anthropic/minimax-m3` | `astropy__astropy-6938` | yes | yes | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 |
| `deepseek/deepseek-v4-flash` | `astropy__astropy-7746` | no | no | 185,426 | 1,237,088 | +1,051,662 | +567.2% | 20 | 56 |
| `deepseek/deepseek-v4-flash` | `django__django-10914` | yes | yes | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 |
| `deepseek/deepseek-v4-flash` | `django__django-10924` | yes | yes | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 |
| `deepseek/deepseek-v4-flash` | `django__django-11001` | yes | yes | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 |

## Aggregate by cohort

| cohort | pairs | resolution off → on | median total tokens off → on | mean total tokens off → on | median calls off → on | mean calls off → on |
|---|---:|---:|---:|---:|---:|---:|
| Minimax M3 / OpenCode Go | 4 | 3/4 → 3/4 | 609,872 → 646,275 (+6.0%) | 856,028 → 1,004,341 (+17.3%) | 46 → 51 (+12.1%) | 48 → 58 (+20.8%) |
| DeepSeek V4 Flash / DeepSeek API | 4 | 3/4 → 3/4 | 288,560 → 676,366 (+134.4%) | 437,176 → 748,511 (+71.2%) | 28 → 46 (+65.5%) | 31 → 44 (+43.9%) |

## Overall across 8 paired instances

- Resolution: **6/8 → 6/8** (no net change).
- Median total tokens: **460,795 → 646,275 (+40.3%)**.
- Mean total tokens: **646,602 → 876,426 (+35.5%)**.
- Median API calls: **36 → 46 (+26.4%)**.
- Mean API calls: **39 → 51 (+29.8%)**.

## Read-out

Across these 8 paired instances, rtk did not change resolution count: both arms resolved 6/8. Token use increased overall, driven by trajectory-length regressions in `astropy__astropy-14995` under Minimax and `astropy__astropy-7746` under DeepSeek. The two clear token wins were `astropy__astropy-14182` (-70.1%) and `django__django-10924` (-19.7%). Treat this as a small, noisy pilot rather than a stable estimate.

## Exclusions

- `astropy__astropy-14365`: excluded from the Minimax paired set because the earlier rtk-off run hung.
- `django__django-11019`: excluded from the DeepSeek paired set because rtk-off did not complete and wrote no trajectory/prediction.
