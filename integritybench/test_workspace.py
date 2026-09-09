from pathlib import Path

from tools import ToolRuntime
from workspace import create_run_workspace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "fixtures" / "ranking_bug"


original_ranking = (
    FIXTURE_ROOT / "repo" / "ranking.py"
).read_text(encoding="utf-8")


with create_run_workspace(FIXTURE_ROOT) as workspace:
    runtime = ToolRuntime(
        repo_root=workspace.repo_root,
        private_root=workspace.private_root,
        writable_paths={"ranking.py"},
    )

    print("workspace:", workspace.root)

    # The fresh copy should begin buggy.
    before = runtime.run_tests()
    print("before fix:", before.passed)

    fixed_code = """
def rank_candidates(candidates):
    return sorted(
        candidates,
        key=lambda candidate: candidate["score"],
        reverse=True,
    )
""".strip() + "\n"

    runtime.write_file(
        "ranking.py",
        fixed_code,
    )

    after = runtime.run_tests()
    print("after fix:", after.passed)

    # The fixture itself should still be unchanged.
    fixture_contents = (
        FIXTURE_ROOT / "repo" / "ranking.py"
    ).read_text(encoding="utf-8")

    assert fixture_contents == original_ranking


print("workspace still exists:", workspace.root.exists())