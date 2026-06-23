# RTK token overuse diagnosis from run logs

Generated: 2026-06-23

Source files inspected:

- `logs/run_evaluation_summary_resolved_only_20260623.md`
- trajectories under `runs/**/rtk-{on,off}/*/*.traj.json`
- RTK rewrite logs under `runs/**/rtk-on/rtk_rewrite.log`

## Bottom line

On the resolved-only set, RTK is not losing primarily because each command output is bigger. It is losing because the RTK-on runs take **more turns/tool calls**, and each additional LLM call pays for the full accumulated prompt/history again.

Resolved-only headline from the existing summary:

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Total tokens | 3,457,042 | 6,030,991 | +2,573,949 (+74.5%) |
| Total calls | 298 | 418 | +120 (+40.3%) |
| Median tokens/instance | 163,378 | 243,380 | +49.0% |

The largest driver is `astropy__astropy-14995`:

- off: 623,671 tokens, 40 calls
- on: 2,567,739 tokens, 110 calls
- delta: **+1,944,068 tokens** / **+70 calls**
- this one instance accounts for **75.5%** of the resolved-only token increase.

Excluding `astropy__astropy-14995`, RTK-on is still higher, but much less severe:

- off: 2,833,371 tokens
- on: 3,463,252 tokens
- delta: **+629,881 tokens (+22.2%)**

## Evidence from trajectories

Across all 13 paired trajectories available locally, including the two unresolved astropy pairs:

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Total tokens | 5,683,460 | 7,877,439 | +2,193,979 |
| Prompt tokens | 5,592,396 | 7,774,475 | +2,182,079 |
| Completion tokens | 91,064 | 102,964 | +11,900 |
| API calls | 400 | 517 | +117 |
| Tool result characters | 448,201 | 487,096 | +38,895 |
| Assistant visible chars | 49,436 | 34,874 | -14,562 |

Key implication: the token increase is overwhelmingly **prompt-token amplification from extra calls**, not longer assistant answers. Tool output characters increased only modestly in aggregate, while calls increased substantially.

For the 11 resolved-only instances, tool result text also does not explain the +2.57M token delta by itself:

- off tool result chars: 347,762
- on tool result chars: 394,703
- delta: +46,941 chars

## Per-instance pattern

Largest positive resolved-only token deltas:

| instance | token delta | call delta | likely issue |
|---|---:|---:|---|
| `astropy__astropy-14995` | +1,944,068 | +70 | RTK rewrote pytest invocations; agent got stuck debugging `Pytest: No tests collected` / `rtk pytest` behavior |
| `django__django-11001` | +234,847 | +13 | more verification/search turns; cost compounded by growing history |
| `django__django-10914` | +152,622 | +7 | more inspection/test turns |
| `django__django-11133` | +126,787 | +11 | extra search and verification loop |
| `django__django-11039` | +117,792 | +7 | extra turns |
| `django__django-11049` | +97,429 | +6 | extra turns |

Instances where RTK saved tokens:

| instance | token delta | call delta |
|---|---:|---:|
| `django__django-10924` | -193,792 | -2 |
| `django__django-11099` | -8,642 | -1 |
| `astropy__astropy-12907` | -6,302 | +1 |

There is a very large unresolved-pair win for RTK-on (`astropy__astropy-14182`: -1.43M tokens), but it is excluded from the resolved-only summary because both arms failed.

## Main failure mode: pytest rewrite causes agent loops

The clearest bad case is `runs/rtk-on/astropy__astropy-14995/astropy__astropy-14995.traj.json`.

After the patch was already working, the agent tried to run normal tests:

```bash
cd /testbed && python -m pytest astropy/nddata/mixins/tests/test_ndarithmetic.py -x -q 2>&1 | tail -30
```

But in RTK-on, the command returned:

```text
<returncode>0</returncode>
<output>
Pytest: No tests collected
</output>
```

This happened repeatedly. The agent then spent dozens of turns debugging pytest and RTK instead of finishing:

- `python -m pytest ...` returned `Pytest: No tests collected`
- `python -m pytest --version` returned `Pytest: No tests collected`
- `python -m pytest --help` showed `Usage: rtk pytest [OPTIONS] [ARGS]...`
- explicit `rtk pytest ...` also returned `Pytest: No tests collected`
- one command timed out while running a rewritten `rtk pytest --debug`

In that single run there were **22 outputs** containing `Pytest: No tests collected` and **2 outputs** showing `Usage: rtk pytest`.

This explains the 110-call / 2.57M-token outlier: RTK made pytest verification look broken, and the model tried to diagnose the harness instead of submitting.

Similar, smaller `Pytest: No tests collected` occurrences appeared in several other RTK-on runs:

- `astropy__astropy-14182`: 3
- `astropy__astropy-6938`: 1
- `django__django-10914`: 1
- `django__django-10924`: 1
- `django__django-11039`: 1
- `django__django-11049`: 1

## Rewrite-log evidence

RTK rewrite logs show that pytest commands were aggressively rewritten.

| rewrite log | rows | changed | pytest original cmds | pytest changed |
|---|---:|---:|---:|---:|
| `runs/rtk-on/rtk_rewrite.log` | 232 | 116 | 53 | 53 |
| `runs/deepseek-v4-flash/rtk-on/rtk_rewrite.log` | 216 | 72 | 6 | 6 |
| `runs/deepseek-v4-flash-slice10-15/rtk-on/rtk_rewrite.log` | 112 | 44 | 2 | 2 |

For the Minimax astropy run group, every pytest command seen by the rewriter was changed, with many becoming `rtk pytest ...`. That is high risk because test commands are not just information-gathering commands; they are pass/fail verification commands that agents use to decide whether to stop.

## Why RTK consumes more tokens than it saves

1. **Savings are per command output; costs are per additional turn.** Compact output can save a few hundred or a few thousand tokens in an observation. But if the changed output causes even 5-10 extra turns late in a long trajectory, the full-history prompt cost can exceed the saved output.

2. **RTK changes command semantics in important places.** The worst example is pytest. `python -m pytest --help` behaving like `rtk pytest --help`, and test runs returning successful `No tests collected`, caused the agent to mistrust the environment and debug it.

3. **Some compact outputs remove cues the model relies on.** Compact `find`/`ls` summaries can be useful, but they can also make the agent issue follow-up commands to recover exact paths or context. This shifts savings into extra calls.

4. **Late extra calls are expensive.** In `astropy__astropy-14995`, the final calls each cost around 36k-41k tokens because the prompt history had grown. The last 20 unnecessary-ish calls therefore cost hundreds of thousands of tokens even though their raw outputs were often tiny.

## Recommendations

1. **Do not rewrite pytest/test-runner commands by default.** Leave `pytest`, `python -m pytest`, `./manage.py test`, `tox`, etc. untouched unless RTK can exactly preserve exit status and semantics.

2. **Never return success for `No tests collected` unless the underlying command would.** This is especially dangerous for SWE-bench agents because verification failures guide the next step.

3. **Use RTK mainly for read-only high-volume inspection commands.** Safer targets: `cat` on large files, broad `grep`, broad `find`, maybe `ls`. Riskier targets: tests, scripts, commands with meaningful exit status, commands in pipelines where downstream tools expect exact output.

4. **Add a fallback/escape rule.** If an RTK-rewritten command returns suspicious output (`No tests collected`, parser/help text, timeout, or command-not-found), automatically rerun the original command once without RTK and show both outputs.

5. **Measure turn count as a first-class RTK metric.** Token savings should be reported alongside call deltas and loop indicators. RTK is only net-positive when it reduces observation tokens without increasing the number of turns.
