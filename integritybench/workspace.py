from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterator
import shutil
import tempfile


@dataclass(frozen=True)
class RunWorkspace:
    root: Path
    repo_root: Path
    private_root: Path


@contextmanager
def create_run_workspace(
    fixture_root: Path,
) -> Iterator[RunWorkspace]:
    fixture_root = fixture_root.resolve()

    source_repo = fixture_root / "repo"
    source_private = fixture_root / "private"

    if not source_repo.is_dir():
        raise ValueError(
            f"Fixture repo does not exist: {source_repo}"
        )

    if not source_private.is_dir():
        raise ValueError(
            f"Fixture private directory does not exist: {source_private}"
        )

    with tempfile.TemporaryDirectory(
        prefix="integritybench_"
    ) as temp_dir:
        root = Path(temp_dir).resolve()

        repo_root = root / "repo"
        private_root = root / "private"

        shutil.copytree(
            source_repo,
            repo_root,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                ".pytest_cache",
                "*.pyc",
                ".git",
            ),
        )
        shutil.copytree(source_private, private_root)

        yield RunWorkspace(
            root=root,
            repo_root=repo_root,
            private_root=private_root,
        )