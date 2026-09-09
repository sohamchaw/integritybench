from dataclasses import dataclass
from pathlib import Path

@dataclass
class ToolRuntime:
    repo_root: Path
    private_root: Path
    writable_paths: set[str]

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