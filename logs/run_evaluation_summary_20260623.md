# rtk evaluation summary: tokens and tool calls (8 paired instances)

Generated: 2026-06-23 20:30:00

This summary is about the effect of **rtk-on vs rtk-off** on token spend and tool/API-call count. The model/provider is included only as run context. The paired set contains 8 completed SWE-bench Lite comparisons: 4 from the earlier Minimax M3 run and 4 from the DeepSeek V4 Flash run.

## Headline

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved | 6 / 8 | 6 / 8 | no change |
| Total tokens spent | 5,172,818 | 7,011,409 | +1,838,591 (+35.5%) |
| Total tool/API calls | 315 | 409 | +94 (+29.8%) |
| Median total tokens per instance | 460,795 | 646,275 | +40.3% |
| Median calls per instance | 36 | 46 | +26.4% |

Paired-instance direction:

- Token use decreased on **3 / 8** paired instances and increased on **5 / 8**.
- Tool/API calls decreased on **2 / 8** paired instances and increased on **6 / 8**.
- Median paired token delta: **+119,870 tokens** (**+37.6%** by per-instance percentage).
- Median paired call delta: **+7.5 calls** (**+23.1%** by per-instance percentage).

## Per-instance token and call deltas

| instance | run context | resolved off → on | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | Minimax M3 / OpenCode Go | yes → yes | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14182` | Minimax M3 / OpenCode Go | no → no | 2,040,992 | 609,360 | -1,431,632 | -70.1% | 82 | 43 | -39 |
| `astropy__astropy-14995` | Minimax M3 / OpenCode Go | yes → yes | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | Minimax M3 / OpenCode Go | yes → yes | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `astropy__astropy-7746` | DeepSeek V4 Flash / DeepSeek API | no → no | 185,426 | 1,237,088 | +1,051,662 | +567.2% | 20 | 56 | +36 |
| `django__django-10914` | DeepSeek V4 Flash / DeepSeek API | yes → yes | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash / DeepSeek API | yes → yes | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash / DeepSeek API | yes → yes | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |

## Largest token changes

Token decreases with rtk-on:

1. `astropy__astropy-14182`: **-1,431,632 tokens** (-70.1%), 82 → 43 calls. This was still unresolved in both arms.
2. `django__django-10924`: **-193,792 tokens** (-19.7%), 48 → 46 calls. Resolved in both arms.
3. `astropy__astropy-12907`: **-6,302 tokens** (-3.9%), 19 → 20 calls. Resolved in both arms.

Token increases with rtk-on:

1. `astropy__astropy-14995`: **+1,944,068 tokens** (+311.7%), 40 → 110 calls. Resolved in both arms.
2. `astropy__astropy-7746`: **+1,051,662 tokens** (+567.2%), 20 → 56 calls. Unresolved in both arms.
3. `django__django-11001`: **+234,847 tokens** (+72.1%), 32 → 45 calls. Resolved in both arms.
4. `django__django-10914`: **+152,622 tokens** (+60.7%), 23 → 30 calls. Resolved in both arms.
5. `astropy__astropy-6938`: **+87,118 tokens** (+14.6%), 51 → 59 calls. Resolved in both arms.

## Secondary run context

| run context | pairs | resolution off → on | median tokens off → on | mean tokens off → on | median calls off → on | mean calls off → on |
|---|---:|---:|---:|---:|---:|---:|
| Minimax M3 / OpenCode Go | 4 | 3/4 → 3/4 | 609,872 → 646,275 (+6.0%) | 856,028 → 1,004,341 (+17.3%) | 46 → 51 (+12.1%) | 48 → 58 (+20.8%) |
| DeepSeek V4 Flash / DeepSeek API | 4 | 3/4 → 3/4 | 288,560 → 676,366 (+134.4%) | 437,176 → 748,511 (+71.2%) | 28 → 46 (+65.5%) | 31 → 44 (+43.9%) |

## Evaluation-log locations

| run context | rtk-off logs | rtk-on logs |
|---|---|---|
| Minimax M3 / OpenCode Go | `logs/run_evaluation/rtk-off-20260623/anthropic__minimax-m3/` | `logs/run_evaluation/rtk-on-20260623/anthropic__minimax-m3/` |
| DeepSeek V4 Flash / DeepSeek API | `logs/run_evaluation/rtk-off-deepseek-20260623/deepseek__deepseek-v4-flash/` | `logs/run_evaluation/rtk-on-deepseek-20260623/deepseek__deepseek-v4-flash/` |

Aggregate harness reports:

- `logs/run_evaluation/rtk-off-20260623/sb_result.json`
- `logs/run_evaluation/rtk-on-20260623/sb_result.json`
- `logs/run_evaluation/rtk-off-deepseek-20260623/sb_result.json`
- `logs/run_evaluation/rtk-on-deepseek-20260623/sb_result.json`

## Read-out

Across these 8 paired instances, rtk did **not** change the resolution count: both arms resolved 6/8. It did increase total token spend and total tool/API calls in this pilot. The overall regression is driven by longer rtk-on trajectories, especially `astropy__astropy-14995` and `astropy__astropy-7746`. The clearest useful rtk-on reductions were `astropy__astropy-14182` and `django__django-10924`, but the former remained unresolved in both arms.

This is still a small, noisy paired pilot; the main measured outcome here is token/call trajectory shape, not model quality.

## Exclusions

- `astropy__astropy-14365`: excluded from the Minimax paired set because the earlier rtk-off run hung.
- `django__django-11019`: excluded from the DeepSeek paired set because rtk-off did not complete and wrote no trajectory/prediction.
