"""On-disk task schema (`manifest.yaml`) and its validation rules.

A task lives in its own directory and is described by a `manifest.yaml` that parses into
:class:`TaskManifest`. Code artifacts (tests, reference implementation, input generators) are
real importable ``.py`` files alongside the manifest, so they can be unit-tested and linted on
their own. HumanEval/MBPP-style tasks simply omit the optional artifacts and declare only the
``test`` suite.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class SuiteName(str, Enum):
    test = "test"
    parity = "parity"
    perf = "perf"


class ParitySpec(BaseModel):
    """Configuration for the differential-testing (parity) suite."""

    generator: str = "generators:make_inputs"
    """``module:callable`` (relative to the task dir) returning a list of JSON-serializable
    input payloads. Called as ``make_inputs(seed=int, n=int)``."""

    num_cases: int = 200
    seed: int = 1234
    compare: str = "equal"
    """Comparison policy: ``equal``, ``approx`` (uses tolerances below), or a custom
    ``module:callable`` taking ``(reference_output, candidate_output) -> bool``."""

    abs_tol: float = 0.0
    rel_tol: float = 0.0
    max_failing_examples: int = 5
    """How many minimal failing payloads to retain in the result detail."""


class PerfPoint(BaseModel):
    """A single performance measurement point."""

    name: str
    size: int
    repeats: int = 7
    max_ratio: float | None = None
    """Budget on ``candidate_min_time / reference_min_time``. ``None`` = report only."""


class PerfSpec(BaseModel):
    """Configuration for the runtime-performance suite."""

    runner: str = "perf:run_once"
    """``module:callable`` (relative to the task dir) executed once per timed iteration,
    called as ``run_once(impl, size=int)``. ``impl`` is the resolved entrypoint."""

    points: list[PerfPoint]
    warmup: int = 1
    seed: int = 99


class TaskManifest(BaseModel):
    """Declarative description of one benchmark task."""

    schema_version: int = 1
    id: str
    origin: str = "custom"  # "humaneval" | "mbpp" | "custom"
    title: str
    tags: list[str] = Field(default_factory=list)

    entrypoint: str
    """Top-level name the candidate must define (function or class)."""

    signature: str | None = None
    """Human-readable expected signature, surfaced in the prompt."""

    language: str = "python"

    suites: list[SuiteName] = Field(default_factory=lambda: [SuiteName.test])

    # Files, relative to the task directory. Presence is validated against `suites`.
    prompt_file: str = "prompt.md"
    tests_file: str | None = "tests.py"
    reference_file: str | None = None
    generators_file: str | None = None

    parity: ParitySpec | None = None
    perf: PerfSpec | None = None

    # Provenance / contamination tracking.
    source_ref: str | None = None
    canonical_solution_redacted: bool = True

    @model_validator(mode="after")
    def _check_suite_applicability(self) -> TaskManifest:
        suites = set(self.suites)

        if SuiteName.test in suites and not self.tests_file:
            raise ValueError(f"task {self.id!r}: 'test' suite requires tests_file")

        if SuiteName.parity in suites:
            if not self.reference_file:
                raise ValueError(f"task {self.id!r}: 'parity' suite requires reference_file")
            if not self.generators_file:
                raise ValueError(f"task {self.id!r}: 'parity' suite requires generators_file")
            if self.parity is None:
                raise ValueError(f"task {self.id!r}: 'parity' suite requires a parity spec")

        if SuiteName.perf in suites:
            if not self.reference_file:
                raise ValueError(f"task {self.id!r}: 'perf' suite requires reference_file")
            if self.perf is None:
                raise ValueError(f"task {self.id!r}: 'perf' suite requires a perf spec")

        if not suites:
            raise ValueError(f"task {self.id!r}: at least one suite must be declared")

        return self
