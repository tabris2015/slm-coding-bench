# slm-coding-bench

A small, **high-signal** coding benchmark for (small) LLMs — designed to compare models,
**deployment methods**, and **solver strategies** on the same footing, with results that stay
comparable across runs over time.

It was built to evaluate small local models (e.g. Qwen2.5-Coder 3B/7B, Qwen3-1.7B) served via
[MLX](https://github.com/ml-explore/mlx-lm) on Apple Silicon, but works against **any
OpenAI-compatible endpoint** (mlx_lm.server, llama-swap, vLLM, or a cloud API).

## What it measures

For each task it runs up to three **code-level** suites on the model's generated solution:

| Suite | Question | Metric |
|-------|----------|--------|
| **test**   | Does the code work? | pass@1 (greedy) / pass@k (sampled) against unit tests |
| **parity** | Does it behave like a reference impl? | agreement rate over seeded differential inputs |
| **perf**   | Is it fast? | runtime ratio vs the reference implementation |

Plus a **serving-level** layer recorded per `(model × deployment)`: latency (p50/p95), throughput
(tok/s), time-to-first-token, token counts, and peak RAM (when the harness owns the process).

## Why three suites

`test` alone is the standard pass@1 number, but it's coarse and contaminated (HumanEval/MBPP are
in training data). `parity` catches solutions that pass the shipped tests but diverge from the
spec on edge cases, and `perf` catches the difference between an `O(n·k)` and an `O(n)` answer —
both are where small models tend to differ from large ones, so they add signal pass@1 misses.

## Design

Three pluggable axes, so a new experiment is a config change, not a rewrite:

- **Deployments** — `openai_compat` (any endpoint), `mlx_server` (launches/manages a local
  `mlx_lm.server`). Future: `llama-swap`, `vllm-mlx`, cloud.
- **Solvers** — `single_agent` (one model call → code). `multi_agent` (planner→coder→verifier)
  ships as a documented stub for a later phase.
- **Executors** — all generated code runs only through an `Executor`. `subprocess` (hardened,
  default). Future: `docker`, `remote`.

## Tasks

A hybrid curated corpus (~18 tasks), one directory per task under `tasks/`:

- **custom/** — hand-authored mini-projects (LRU cache, sliding-window-max, topo-sort, …) that
  ship a reference implementation + seeded input generators + perf sizes, so they exercise all
  three suites and are contamination-free.
- **humaneval/** — a slice of HumanEval/MBPP, `test`-only, tagged so the report separates
  contaminated-but-comparable scores from the custom scores.

## Quickstart

```bash
uv sync
uv run slm-bench list-tasks
uv run slm-bench validate-tasks
# point configs/m4-local.yaml at your endpoint, then:
uv run slm-bench run -c configs/m4-local.yaml
uv run slm-bench report <run_id>
```

## Example results

A first run of the three-model MLX roster on an M4 Pro (24 GB), single-agent solver, greedy
pass@1 — see [`docs/example-report-m4-roster.md`](docs/example-report-m4-roster.md):

| Model | pass@1 (custom) | parity | perf ratio | tok/s (e2e) |
|---|---|---|---|---|
| Qwen2.5-Coder-7B-4bit | 100% | 100% | 1.29× | 37 |
| Qwen2.5-Coder-3B-4bit | 75% | 93.9% | 1.32× | 71 |
| Qwen3-1.7B-4bit | 25% | 28.6% | 0.97× | 137 |

The parity column already earns its keep: the 3B passes 75% of custom tasks outright but agrees
with the reference on 93.9% of differential inputs — pass@1 alone would have hidden how close the
near-misses were. (Qwen3-1.7B is a reasoning model; it spends its token budget "thinking", which
is why it trails here and needs a larger `max_tokens`.)

## Status

v1: benchmark core + `single_agent` solver + OpenAI-compatible/`mlx_server` deployment, validated
end-to-end. `multi_agent` solver and `docker`/`remote` executors are scoped as follow-ups.

## License

MIT.
