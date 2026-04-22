# Debugging notes — LocalLLM_Pipeline Stage 4 (aider) timeout

## Symptom

Step 28 (Static CSS tests), invoked as:

```
aider --message <prompt> --yes tests/test_static_css.py --model ollama_chat/qwen3-coder:30b
```

Failed with:

```
litellm.APIConnectionError: Ollama_chatException - litellm.Timeout: Connection timed out after 600.0 seconds.
Retrying in 0.2 seconds...
```

After the auto-retry, generation began streaming but aider's progress bar showed an absurd target:

```
+ 6 / 8289 lines [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0%
```

## What's happening

Stage 4 spawns aider as a subprocess. Aider talks to Ollama via **litellm's `ollama_chat` adapter** — a separate code path from `_pipeline/ollama.py`. Litellm's HTTP request to `192.168.1.126:11434` exceeded its default **600s** timeout, raised `Timeout`, wrapped it as `APIConnectionError`, and auto-retried after 200ms.

Two compounding issues:

### 1. Runaway generation (the real problem)

`qwen3-coder:30b` is producing ~8000 lines for `tests/test_static_css.py`. A normal version of that file is 100–500 lines. Likely causes, in order of probability:

- The Stage 3b prompt for Step 28 included a large architecture-plan slice and the model is regurgitating large parts of it back as test scaffolding. The `[symbols] injecting inventory (128 entries) from ctags` log line is a hint that a lot of context went in.
- `qwen3-coder:30b` entered a repetition loop (a known failure mode on test-generation prompts that include long file inventories).
- `num_predict` is effectively unbounded in aider's litellm path, so the model has no upper limit and keeps going.

### 2. The 600s litellm timeout is too short for that volume

At ~50 tok/s on a 30B model and ~10 tokens/line, 8289 lines is ≈1700s. Litellm gives up at 600s.

### Why orchestrator timeouts don't apply

`LLM_PLANNING_TIMEOUT` and the adaptive timeout in `_pipeline/ollama.py` only apply to coding stages 0–3. Stage 4 runs aider as a subprocess (`run_aider.py`); aider's own litellm config governs HTTP behavior. The orchestrator does not control it.

## Fixes (in order of leverage)

### 1. Don't just raise the timeout — fix the runaway first

Open `aidercommands.md` and read the Step 28 prompt. If it's bloated with the full ctags inventory and architecture plan, that's the trigger. Trim the prompt rather than tolerating 30-minute generations. A prompt that fits in 4–8k tokens is a healthy size for a single test file.

### 2. Switch the aider model for this step

In `Common/.env`:

```
LLM_AIDER_MODEL=qwen2.5-coder:32b
```

The 2.5 coder line is more deterministic on test generation than 3-coder.

### 3. Raise litellm's timeout

Before running:

```powershell
$env:OLLAMA_REQUEST_TIMEOUT = "1800"
```

Or pass `--timeout 1800` to aider in the `aidercommands.md` step. 1800s (30 min) is enough headroom for legitimate large generations.

### 4. Cap output length

Add `num_predict` to the aider model config (`.aider.model.metadata.json` or equivalent) so runaway generation forcibly stops at, say, 4000 tokens. Failing fast with a partial file beats waiting 30 minutes for a wrong one.

### 5. Resume

Stage 4 is per-step. Once the model / timeout / prompt is fixed, just rerun the pipeline — it picks up at Step 28 with no `--restart` needed.

## Diagnostic checklist for next time

When a Stage-4 step times out, before changing config, answer these:

1. **What was the prompt size?** `wc -l aidercommands.md` and look at the Step N block. >300 lines of prompt is suspicious.
2. **What does the partial output look like?** If aider streamed any content to disk, read the first 50 lines — repetition or off-topic content confirms a runaway, not a slow but legitimate generation.
3. **How many tokens did the model actually emit?** Aider logs token counts on completion; if it died mid-stream, check Ollama's logs on the server.
4. **Is the server itself slow right now?** Quick check from the client:
   ```powershell
   Measure-Command { Invoke-RestMethod -Uri "http://192.168.1.126:11434/api/generate" -Method Post -Body '{"model":"qwen3-coder:30b","prompt":"hi","stream":false}' -ContentType "application/json" }
   ```
   If a one-token generation is slow, the issue is server-side (model not warm, GPU contention) rather than prompt-related.

## Reference

- Pipeline doc: `C:\Coding\LocalLLM_Pipeline\Common\Documentation\ArchPipeline.md`
- Stage 4 implementation: `LocalLLMCoding/run_aider.py`
- Default model fallback chain: `LLM_AIDER_MODEL` → `LLM_DEFAULT_MODEL` → `qwen3-coder:30b`
- Orchestrator's own LLM client (separate from aider): `Common/_pipeline/ollama.py`
