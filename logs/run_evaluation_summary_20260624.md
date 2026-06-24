# rtk evaluation summary: tokens, tool calls, and resolved status (23 paired instances)

Generated: 2026-06-24

This summary covers all completed paired SWE-bench Lite instances across five slices: 0:5 (MiniMax M3), 5:10, 10:15, 15:20, and 20:25 (DeepSeek V4 Flash).

## Headline

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved | 18 / 23 | 17 / 23 | rtk-on lost 1 |
| Total tokens spent | 15,696,536 | 20,989,751 | +5,293,215 (+33.7%) |
| Total tool/API calls | 813 | 1,001 | +188 (+23.1%) |
| Median total tokens per instance | 311,269 | 609,360 | +95.8% |
| Mean total tokens per instance | 682,458 | 912,598 | +33.7% |
| Median calls per instance | 28 | 39 | +39.3% |
| Mean calls per instance | 35.3 | 43.5 | +23.1% |

Paired-instance direction:

- Token use decreased on **5 / 23** paired instances and increased on **18 / 23**.
- Resolution changed on **1 / 23**: `django__django-11630` resolved rtk-off but not rtk-on. This is the first resolution regression observed.

## Per-instance token and call deltas

| instance | run context | resolved off → on | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | MiniMax M3 (0:5) | yes → yes | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14182` | MiniMax M3 (0:5) | no → no | 2,040,992 | 609,360 | -1,431,632 | -70.1% | 82 | 43 | -39 |
| `astropy__astropy-14995` | MiniMax M3 (0:5) | yes → yes | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | MiniMax M3 (0:5) | yes → yes | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `astropy__astropy-7746` | DeepSeek V4 Flash (5:10) | no → no | 185,426 | 1,237,088 | +1,051,662 | +567.2% | 20 | 56 | +36 |
| `django__django-10914` | DeepSeek V4 Flash (5:10) | yes → yes | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash (5:10) | yes → yes | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash (5:10) | yes → yes | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |
| `django__django-11039` | DeepSeek V4 Flash (10:15) | yes → yes | 95,013 | 212,805 | +117,792 | +124.0% | 17 | 24 | +7 |
| `django__django-11049` | DeepSeek V4 Flash (10:15) | yes → yes | 113,053 | 210,482 | +97,429 | +86.2% | 19 | 25 | +6 |
| `django__django-11099` | DeepSeek V4 Flash (10:15) | yes → yes | 52,555 | 43,913 | -8,642 | -16.4% | 13 | 12 | -1 |
| `django__django-11133` | DeepSeek V4 Flash (10:15) | yes → yes | 116,593 | 243,380 | +126,787 | +108.7% | 16 | 27 | +11 |
| `django__django-11179` | DeepSeek V4 Flash (10:15) | yes → yes | 133,428 | 155,450 | +22,022 | +16.5% | 20 | 20 | +0 |
| `django__django-11283` | DeepSeek V4 Flash (15:20) | yes → yes | 158,836 | 827,200 | +668,364 | +420.8% | 16 | 43 | +27 |
| `django__django-11422` | DeepSeek V4 Flash (15:20) | yes → yes | 520,638 | 739,211 | +218,573 | +42.0% | 36 | 39 | +3 |
| `django__django-11564` | DeepSeek V4 Flash (15:20) | no → no | 575,578 | 1,423,574 | +847,996 | +147.3% | 31 | 49 | +18 |
| `django__django-11583` | DeepSeek V4 Flash (15:20) | yes → yes | 145,612 | 207,407 | +61,795 | +42.4% | 18 | 21 | +3 |
| `django__django-11620` | DeepSeek V4 Flash (15:20) | yes → yes | 2,088,378 | 1,083,419 | -1,004,959 | -48.1% | 72 | 54 | -18 |
| `django__django-11630` | DeepSeek V4 Flash (20:25) | **yes → no** | 424,357 | 431,430 | +7,073 | +1.7% | 32 | 32 | +0 |
| `django__django-11742` | DeepSeek V4 Flash (20:25) | no → no | 587,869 | 1,245,018 | +657,149 | +111.8% | 39 | 52 | +13 |
| `django__django-11797` | DeepSeek V4 Flash (20:25) | yes → yes | 4,953,181 | 6,254,382 | +1,301,201 | +26.3% | 112 | 131 | +19 |
| `django__django-11815` | DeepSeek V4 Flash (20:25) | yes → yes | 311,269 | 733,747 | +422,478 | +135.7% | 28 | 41 | +13 |
| `django__django-11848` | DeepSeek V4 Flash (20:25) | no → no | 247,358 | 166,924 | -80,434 | -32.5% | 29 | 22 | -7 |

## New slice (20:25) highlights

The DeepSeek V4 Flash slice 20:25 is the first to show a resolution regression: `django__django-11630` resolved under rtk-off but not rtk-on, despite nearly identical resource usage (+1.7% tokens, same call count). Total token spend: **6,524,034 → 8,831,501** (+35.4%), calls **240 → 278** (+15.8%).

`django__django-11797` is the most expensive instance across all slices at 4.95M–6.25M tokens (112–131 calls), dwarfing even the previous worst performer. Both arms resolved it.

## Run-context split

| run context | pairs | resolution off → on | total tokens off → on | median tokens off → on | total calls off → on | median calls off → on |
|---|---:|---:|---:|---:|---:|---:|
| MiniMax M3 (0:5) | 4 | 3/4 → 3/4 | 3,424,113 → 4,017,365 (+17.3%) | 609,872 → 646,275 | 192 → 232 (+20.8%) | 45.5 → 51 |
| DeepSeek V4 Flash (5:10) | 4 | 3/4 → 3/4 | 1,748,705 → 2,994,044 (+71.2%) | 288,560 → 676,366 | 123 → 177 (+43.9%) | 27.5 → 45.5 |
| DeepSeek V4 Flash (10:15) | 5 | 5/5 → 5/5 | 510,642 → 866,030 (+69.6%) | 113,053 → 210,482 | 85 → 108 (+27.1%) | 17 → 24 |
| DeepSeek V4 Flash (15:20) | 5 | 4/5 → 4/5 | 3,488,042 → 4,280,811 (+22.7%) | 520,638 → 827,200 | 173 → 206 (+19.1%) | 31 → 43 |
| DeepSeek V4 Flash (20:25) | 5 | 3/5 → 2/5 | 6,524,034 → 8,831,501 (+35.4%) | 587,869 → 1,245,018 | 240 → 278 (+15.8%) | 32 → 41 |

## Evaluation-log locations

| run context | rtk-off logs | rtk-on logs |
|---|---|---|
| MiniMax M3 (0:5) | `logs/run_evaluation/rtk-off-20260623/anthropic__minimax-m3/sb_result.json` | `logs/run_evaluation/rtk-on-20260623/anthropic__minimax-m3/sb_result.json` |
| DeepSeek V4 Flash (5:10) | `logs/run_evaluation/rtk-off-deepseek-20260623/deepseek__deepseek-v4-flash/sb_result.json` | `logs/run_evaluation/rtk-on-deepseek-20260623/deepseek__deepseek-v4-flash/sb_result.json` |
| DeepSeek V4 Flash (10:15) | `logs/run_evaluation/rtk-off-deepseek-slice10-15-20260623/` | `logs/run_evaluation/rtk-on-deepseek-slice10-15-20260623/` |
| DeepSeek V4 Flash (15:20) | `logs/run_evaluation/rtk-off-deepseek-slice15-20-20260624/` | `logs/run_evaluation/rtk-on-deepseek-slice15-20-20260624/` |
| DeepSeek V4 Flash (20:25) | `logs/run_evaluation/rtk-off-deepseek-slice20-25-20260624/` | `logs/run_evaluation/rtk-on-deepseek-slice20-25-20260624/` |

## Exclusions

- `astropy__astropy-14365`: excluded from the MiniMax paired set because the earlier rtk-off run hung.
- `django__django-11019`: excluded from the DeepSeek slice 5:10 paired set because the runs did not complete a paired trajectory.

## Read-out

Across 23 paired instances, rtk-on reduced resolution (18→17) for the first time while increasing total token spend by **+33.7%** and total tool/API calls by **+23.1%**. The new slice 20:25 produced the most expensive instance yet (`django__django-11797` at 5–6M tokens) and the first resolution regression (`django__django-11630`).
