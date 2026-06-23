# rtk evaluation summary: tokens and tool calls (13 paired instances)

Generated: 2026-06-23 21:17:00

This summary updates the earlier 8-pair pilot with the additional DeepSeek V4 Flash `--slice 10:15` next-5 run. It compares **rtk-on vs rtk-off** for token spend, tool/API-call count, and SWE-bench resolved status.

## Headline

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved | 11 / 13 | 11 / 13 | no change |
| Total tokens spent | 5,683,460 | 7,877,439 | +2,193,979 (+38.6%) |
| Total tool/API calls | 400 | 517 | +117 (+29.2%) |
| Median total tokens per instance | 185,426 | 404,225 | +118.0% |
| Mean total tokens per instance | 437,189 | 605,957 | +38.6% |
| Median calls per instance | 20 | 30 | +50.0% |
| Mean calls per instance | 30.8 | 39.8 | +29.2% |

Paired-instance direction:

- Token use decreased on **4 / 13** paired instances and increased on **9 / 13**.
- Tool/API calls decreased on **3 / 13** paired instances, were unchanged on **1 / 13**, and increased on **9 / 13**.
- Median paired token delta: **97,429 tokens** (**+60.7%** by per-instance percentage).
- Median paired call delta: **7 calls** (**+30.4%** by per-instance percentage).

## Per-instance token and call deltas

| instance | run context | resolved off → on | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | Minimax M3 / OpenCode Go | yes → yes | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14182` | Minimax M3 / OpenCode Go | no → no | 2,040,992 | 609,360 | -1,431,632 | -70.1% | 82 | 43 | -39 |
| `astropy__astropy-14995` | Minimax M3 / OpenCode Go | yes → yes | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | Minimax M3 / OpenCode Go | yes → yes | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `astropy__astropy-7746` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | no → no | 185,426 | 1,237,088 | +1,051,662 | +567.2% | 20 | 56 | +36 |
| `django__django-10914` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | yes → yes | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | yes → yes | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | yes → yes | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |
| `django__django-11039` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | yes → yes | 95,013 | 212,805 | +117,792 | +124.0% | 17 | 24 | +7 |
| `django__django-11049` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | yes → yes | 113,053 | 210,482 | +97,429 | +86.2% | 19 | 25 | +6 |
| `django__django-11099` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | yes → yes | 52,555 | 43,913 | -8,642 | -16.4% | 13 | 12 | -1 |
| `django__django-11133` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | yes → yes | 116,593 | 243,380 | +126,787 | +108.7% | 16 | 27 | +11 |
| `django__django-11179` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | yes → yes | 133,428 | 155,450 | +22,022 | +16.5% | 20 | 20 | +0 |

## New next-5 slice (`10:15`)

The newly added DeepSeek slice completed and resolved all five instances in both arms. Cost still moved upward with rtk-on: total tokens **510,642 → 866,030** (+69.6%), and calls **85 → 108** (+27.1%).

## Largest token changes

Token decreases with rtk-on:
1. `astropy__astropy-14182`: **-1,431,632 tokens** (-70.1%), 82 → 43 calls. Resolved no → no.
2. `django__django-10924`: **-193,792 tokens** (-19.7%), 48 → 46 calls. Resolved yes → yes.
3. `django__django-11099`: **-8,642 tokens** (-16.4%), 13 → 12 calls. Resolved yes → yes.
4. `astropy__astropy-12907`: **-6,302 tokens** (-3.9%), 19 → 20 calls. Resolved yes → yes.

Token increases with rtk-on:
1. `astropy__astropy-14995`: **+1,944,068 tokens** (+311.7%), 40 → 110 calls. Resolved yes → yes.
2. `astropy__astropy-7746`: **+1,051,662 tokens** (+567.2%), 20 → 56 calls. Resolved no → no.
3. `django__django-11001`: **+234,847 tokens** (+72.1%), 32 → 45 calls. Resolved yes → yes.
4. `django__django-10914`: **+152,622 tokens** (+60.7%), 23 → 30 calls. Resolved yes → yes.
5. `django__django-11133`: **+126,787 tokens** (+108.7%), 16 → 27 calls. Resolved yes → yes.
6. `django__django-11039`: **+117,792 tokens** (+124.0%), 17 → 24 calls. Resolved yes → yes.
7. `django__django-11049`: **+97,429 tokens** (+86.2%), 19 → 25 calls. Resolved yes → yes.
8. `astropy__astropy-6938`: **+87,118 tokens** (+14.6%), 51 → 59 calls. Resolved yes → yes.
9. `django__django-11179`: **+22,022 tokens** (+16.5%), 20 → 20 calls. Resolved yes → yes.

## Run-context split

| run context | pairs | resolution off → on | total tokens off → on | median tokens off → on | total calls off → on | median calls off → on |
|---|---:|---:|---:|---:|---:|---:|
| Minimax M3 / OpenCode Go | 4 | 3/4 → 3/4 | 3,424,113 → 4,017,365 (+17.3%) | 609,872 → 646,275 | 192 → 232 (+20.8%) | 45.5 → 51 |
| DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | 4 | 3/4 → 3/4 | 1,748,705 → 2,994,044 (+71.2%) | 288,560 → 676,366 | 123 → 177 (+43.9%) | 27.5 → 45.5 |
| DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 5 | 5/5 → 5/5 | 510,642 → 866,030 (+69.6%) | 113,053 → 210,482 | 85 → 108 (+27.1%) | 17 → 24 |

## Evaluation-log locations

| run context | rtk-off logs | rtk-on logs |
|---|---|---|
| Minimax M3 / OpenCode Go | `logs/run_evaluation/rtk-off-20260623/anthropic__minimax-m3/` | `logs/run_evaluation/rtk-on-20260623/anthropic__minimax-m3/` |
| DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | `logs/run_evaluation/rtk-off-deepseek-20260623/deepseek__deepseek-v4-flash/` | `logs/run_evaluation/rtk-on-deepseek-20260623/deepseek__deepseek-v4-flash/` |
| DeepSeek V4 Flash / DeepSeek API (slice 10:15) | `logs/run_evaluation/rtk-off-deepseek-slice10-15-20260623/deepseek__deepseek-v4-flash/` | `logs/run_evaluation/rtk-on-deepseek-slice10-15-20260623/deepseek__deepseek-v4-flash/` |

Aggregate harness reports:
- `logs/run_evaluation/rtk-off-20260623/sb_result.json`
- `logs/run_evaluation/rtk-on-20260623/sb_result.json`
- `logs/run_evaluation/rtk-off-deepseek-20260623/sb_result.json`
- `logs/run_evaluation/rtk-on-deepseek-20260623/sb_result.json`
- `logs/run_evaluation/rtk-off-deepseek-slice10-15-20260623/sb_result.json`
- `logs/run_evaluation/rtk-on-deepseek-slice10-15-20260623/sb_result.json`

## Read-out

Across the 13 completed paired instances, rtk did **not** change resolved count: both arms resolved 11/13. It increased total token spend by **+38.6%** and total tool/API calls by **+29.2%**. The additional next-5 slice is consistent with the earlier direction: all five solved in both arms, but rtk-on used more tokens on 4/5 of those instances.

## Exclusions

- `astropy__astropy-14365`: excluded from the Minimax paired set because the earlier rtk-off run hung.
- `django__django-11019`: excluded from the DeepSeek slice 5:10 paired set because the initial rtk-off/rtk-on runs did not complete a paired trajectory/prediction for that instance.
