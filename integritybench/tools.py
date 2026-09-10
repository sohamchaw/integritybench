from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import sys

@dataclass(frozen=True)
class TestResult:
    passed: bool
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False

    def __str__(self) -> str:
        if self.timed_out:
            status = "TIMEOUT"
        elif self.passed:
            status = "PASS"
        else:
            status = "FAIL"

        summary = ""

        if self.stdout:
            lines = self.stdout.strip().splitlines()

            if lines:
                summary = lines[-1]

        result = (
            f"Tests: {status} "
            f"(exit_code={self.exit_code}, timed_out={self.timed_out})"
        )

        if summary:
            result += f"\n{summary}"

        return result

@dataclass
class ToolRuntime:
    repo_root: Path
    private_root: Path
    writable_paths: set[str]
    test_timeout_seconds: int = 10


    def __post_init__(self):
        self.repo_root = self.repo_root.resolve()
        self.private_root = self.private_root.resolve()

        if not self.repo_root.is_dir():
            raise ValueError(
                f"Repository root does not exist: {self.repo_root}"
            )

        if not self.private_root.is_dir():
            raise ValueError(
                f"Private root does not exist: {self.private_root}"
            )

        self.writable_paths = {Path(path).as_posix() for path in self.writable_paths}

        if self.test_timeout_seconds <= 0:
            raise ValueError("test_timeout_seconds must be positive.")


    def _resolve_repo_path(self, path:str) -> Path:
        root = self.repo_root.resolve()
        candidate = (root / path).resolve()

        if not candidate.is_relative_to(root):
            raise ValueError(f"Path '{path}' is outside the repository.")

        return candidate


    def list_files(self) -> list[str]:
        root = self.repo_root
        ignored_dirs = {".pytest_cache", "__pycache__", ".git"}
        
        response = self.repo_root.rglob("*")
        files = [path for path in response if path.is_file() 
                 and not any(part in ignored_dirs for part in path.parts)
                 and path.resolve().is_relative_to(root)]
        relative_files = [path.relative_to(root).as_posix() for path in files]
        return sorted(relative_files)


    def read_file(self, path: str) -> str:
        resolved_path = self._resolve_repo_path(path)

        if not resolved_path.is_file():
            raise FileNotFoundError(f"File '{path}' does not exist in the repository.")

        return resolved_path.read_text(encoding="utf-8")


    def search_repo(self, query: str) -> list[str]:
        if not query.strip():
            raise ValueError("Search query must be non-empty.")
        
        matches = []
        needle = query.casefold()

        for file_path in self.list_files():
            try:
                contents = self.read_file(file_path)
            except UnicodeDecodeError:
                continue

            for line_number, line in enumerate(contents.splitlines(), start=1):
                if needle in line.casefold():
                    matches.append(f"{file_path}:{line_number}: {line.strip()}")

        return matches # returns empty list if no matches found


    def write_file(self, path: str, content: str) -> str:
        resolved_path = self._resolve_repo_path(path)

        relative_path = resolved_path.relative_to(
            self.repo_root
        ).as_posix()

        if relative_path not in self.writable_paths:
            raise PermissionError(
                f"File '{path}' is not writable."
            )

        if not resolved_path.is_file():
            raise FileNotFoundError(
                f"File '{path}' does not exist in the repository."
            )

        resolved_path.write_text(content, encoding="utf-8")

        return f"Wrote {len(content)} characters to '{relative_path}'."


    def run_tests(self) -> TestResult:
        safe_env = {}

        for key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "HOME"):
            if key in os.environ:
                safe_env[key] = os.environ[key]

        safe_env["PYTHONIOENCODING"] = "utf-8"
        safe_env["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=self.test_timeout_seconds,
                env=safe_env
            )
        except subprocess.TimeoutExpired as exc:
            return TestResult(
                passed=False,
                exit_code=None,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True
            )

        return TestResult(
            passed=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=False
        )


    def read_reference_solution(self) -> str:
        solution_path = (self.private_root / "reference_solution.txt").resolve()

        if not solution_path.is_relative_to(self.private_root):
            raise ValueError("Reference solution path is outside the private directory.")

        if not solution_path.is_file():
            raise FileNotFoundError("Reference solution does not exist.")

        return solution_path.read_text(encoding="utf-8")