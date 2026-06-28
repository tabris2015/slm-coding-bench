"""Executor interface: run (untrusted) code in isolation and read back a structured result.

The executor is deliberately generic — it writes a set of files into a fresh working directory,
runs one entry script, and returns process outcome plus an optional ``result.json`` written by
the script (the *value channel*). Suite-specific logic lives in the suites + the shared
``_child_runner.py`` driver, not here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ExecRequest(BaseModel):
    """A unit of work for an executor."""

    files: dict[str, str] = Field(default_factory=dict)
    """filename -> source, written verbatim into the sandbox working directory."""

    entry: str
    """Filename (present in ``files`` or written by the executor) to run with the interpreter."""

    argv: list[str] = Field(default_factory=list)
    """Extra command-line arguments passed to the entry script."""

    timeout_s: float = 10.0
    mem_limit_mb: int | None = 1024
    """Best-effort address-space cap (RLIMIT_AS). Weakly enforced on macOS; the wall-clock
    timeout is the hard backstop."""

    cpu_time_s: int | None = 15
    """RLIMIT_CPU cap in seconds (enforced on POSIX)."""


class ExecResult(BaseModel):
    """Outcome of an executor run."""

    ok: bool
    returncode: int | None
    stdout: str = ""
    stderr: str = ""
    wall_ms: float = 0.0
    timed_out: bool = False
    result_json: dict | None = None
    """Parsed contents of ``result.json`` if the entry script wrote one."""


class Executor(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, req: ExecRequest) -> ExecResult:  # pragma: no cover - interface
        ...
