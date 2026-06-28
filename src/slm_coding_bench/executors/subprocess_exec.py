"""Subprocess executor: a hardened, single-machine code runner.

Isolation provided:
- a fresh temporary working directory (removed after the run);
- a scrubbed environment (no inherited vars beyond a minimal PATH/PYTHON set);
- ``RLIMIT_CPU`` (POSIX) and best-effort ``RLIMIT_AS`` resource limits;
- ``start_new_session`` so a timed-out process *group* can be killed cleanly;
- a wall-clock timeout as the hard backstop.

Limitations (documented, by design for v1): no network namespace and no cgroups on macOS, so
this is appropriate for evaluating models you are willing to run on your own machine. Use a
``DockerExecutor``/``RemoteExecutor`` (future) for untrusted code.
"""

from __future__ import annotations

import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from slm_coding_bench.executors.base import ExecRequest, ExecResult, Executor

# Path to the value-channel driver, copied into each sandbox so it needs no package import.
_CHILD_RUNNER = Path(__file__).with_name("_child_runner.py")


def _make_preexec(mem_limit_mb: int | None, cpu_time_s: int | None):
    """Build a preexec_fn that applies resource limits.

    Note: the new session (setsid) is created by Popen's ``start_new_session=True``; we must not
    call ``setsid`` again here or it raises in the child.
    """

    def _preexec() -> None:  # pragma: no cover - runs in the child process
        if cpu_time_s is not None:
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_time_s, cpu_time_s + 1))
            except (ValueError, OSError):
                pass
        if mem_limit_mb is not None:
            nbytes = mem_limit_mb * 1024 * 1024
            for lim in ("RLIMIT_AS", "RLIMIT_DATA"):
                rlim = getattr(resource, lim, None)
                if rlim is None:
                    continue
                try:
                    resource.setrlimit(rlim, (nbytes, nbytes))
                except (ValueError, OSError):
                    # macOS frequently rejects RLIMIT_AS; rely on the wall-clock timeout.
                    pass

    return _preexec


def _scrubbed_env() -> dict[str, str]:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        # Discourage accidental network use by libraries that honor proxies.
        "no_proxy": "*",
    }
    if "SystemRoot" in os.environ:  # Windows safety; harness targets POSIX.
        env["SystemRoot"] = os.environ["SystemRoot"]
    return env


class SubprocessExecutor(Executor):
    name = "subprocess"

    def __init__(self, python_executable: str | None = None) -> None:
        self.python = python_executable or sys.executable

    def run(self, req: ExecRequest) -> ExecResult:
        workdir = Path(tempfile.mkdtemp(prefix="slm_bench_"))
        try:
            for name, source in req.files.items():
                target = workdir / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source)
            # Always provide the value-channel driver.
            shutil.copy(_CHILD_RUNNER, workdir / "_child_runner.py")

            # -s (no user site) + -E (ignore PYTHON* env) isolate without dropping the
            # sandbox dir from sys.path (which -I/-P would do, breaking local imports).
            cmd = [self.python, "-s", "-E", req.entry, *req.argv]
            preexec = _make_preexec(req.mem_limit_mb, req.cpu_time_s)

            start = time.perf_counter()
            proc = subprocess.Popen(
                cmd,
                cwd=workdir,
                env=_scrubbed_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
                preexec_fn=preexec,
            )
            timed_out = False
            try:
                stdout, stderr = proc.communicate(timeout=req.timeout_s)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill_group(proc)
                stdout, stderr = proc.communicate()
            wall_ms = (time.perf_counter() - start) * 1000.0

            result_json = _read_result(workdir)
            rc = proc.returncode
            ok = (not timed_out) and rc == 0
            return ExecResult(
                ok=ok,
                returncode=rc,
                stdout=stdout or "",
                stderr=stderr or "",
                wall_ms=wall_ms,
                timed_out=timed_out,
                result_json=result_json,
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


def _kill_group(proc: subprocess.Popen) -> None:  # pragma: no cover - timing dependent
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass


def _read_result(workdir: Path) -> dict | None:
    path = workdir / "result.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
