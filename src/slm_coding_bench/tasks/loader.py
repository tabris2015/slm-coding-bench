"""Discover, parse, and validate task directories into runtime :class:`Task` objects."""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

from slm_coding_bench.models import Task
from slm_coding_bench.tasks.manifest import SuiteName, TaskManifest

MANIFEST_NAME = "manifest.yaml"


class TaskLoadError(Exception):
    """Raised when a task directory is malformed or inconsistent."""


def _resolve_root(root: Path | str) -> Path:
    root = Path(root)
    if not root.exists():
        raise TaskLoadError(f"tasks root does not exist: {root}")
    return root


def discover_manifests(root: Path | str) -> list[Path]:
    """Return every ``manifest.yaml`` under ``root`` (sorted, recursive)."""
    root = _resolve_root(root)
    return sorted(root.rglob(MANIFEST_NAME))


def _check_files_exist(manifest: TaskManifest, task_dir: Path) -> list[str]:
    """Return a list of problems with the on-disk artifacts referenced by the manifest."""
    problems: list[str] = []

    def _require(field: str, value: str | None) -> None:
        if value and not (task_dir / value).is_file():
            problems.append(f"{field} not found: {value}")

    _require("prompt_file", manifest.prompt_file)
    if SuiteName.test in manifest.suites:
        _require("tests_file", manifest.tests_file)
    if {SuiteName.parity, SuiteName.perf} & set(manifest.suites):
        _require("reference_file", manifest.reference_file)
    if SuiteName.parity in manifest.suites:
        _require("generators_file", manifest.generators_file)

    return problems


def load_task(manifest_path: Path | str) -> Task:
    """Load and validate a single task from its ``manifest.yaml`` path."""
    manifest_path = Path(manifest_path)
    task_dir = manifest_path.parent

    try:
        raw = yaml.safe_load(manifest_path.read_text()) or {}
    except yaml.YAMLError as e:  # pragma: no cover - exercised via validate
        raise TaskLoadError(f"{manifest_path}: invalid YAML: {e}") from e

    try:
        manifest = TaskManifest.model_validate(raw)
    except Exception as e:
        raise TaskLoadError(f"{manifest_path}: {e}") from e

    problems = _check_files_exist(manifest, task_dir)
    if problems:
        raise TaskLoadError(f"{manifest_path}: " + "; ".join(problems))

    prompt = (task_dir / manifest.prompt_file).read_text()
    return Task(manifest=manifest, dir=task_dir, prompt=prompt)


def load_tasks(root: Path | str, globs: list[str] | None = None) -> list[Task]:
    """Load every valid task under ``root``, optionally filtered by id globs.

    ``globs`` match against the task id (e.g. ``["custom/*", "humaneval/he_000"]``).
    Raises :class:`TaskLoadError` on the first malformed task so problems surface early.
    """
    root = _resolve_root(root)
    tasks: list[Task] = []
    for manifest_path in discover_manifests(root):
        task = load_task(manifest_path)
        if globs and not any(fnmatch.fnmatch(task.id, g) for g in globs):
            continue
        tasks.append(task)

    if globs and not tasks:
        raise TaskLoadError(f"no tasks under {root} matched globs: {globs}")
    return tasks


def validate_tasks(root: Path | str) -> list[tuple[Path, str]]:
    """Validate all task dirs; return a list of ``(manifest_path, error)`` for any failures."""
    failures: list[tuple[Path, str]] = []
    for manifest_path in discover_manifests(root):
        try:
            load_task(manifest_path)
        except TaskLoadError as e:
            failures.append((manifest_path, str(e)))
    return failures
