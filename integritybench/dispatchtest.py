from pathlib import Path

from executor import ToolExecutor
from scenario import RANKING_BUG
from tools import ToolRuntime
from trace import RunTrace
from workspace import create_run_workspace


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "fixtures" / "ranking_bug"


with create_run_workspace(FIXTURE_ROOT) as workspace:
    runtime = ToolRuntime(
        repo_root=workspace.repo_root,
        private_root=workspace.private_root,
        writable_paths=RANKING_BUG.writable_paths,
    )

    trace = RunTrace(
        run_id="test_run_001",
        scenario_id=RANKING_BUG.id,
    )

    executor = ToolExecutor(
        runtime=runtime,
        scenario=RANKING_BUG,
        trace=trace,
    )

    print("fixture repo:", FIXTURE_ROOT / "repo")
    print("workspace repo:", workspace.repo_root)
    print("runtime repo:", runtime.repo_root)

    assert runtime.repo_root != (FIXTURE_ROOT / "repo").resolve()

    print(
        executor.execute(
            "list_files",
            {},
        )
    )

    print(
        executor.execute(
            "read_file",
            {"path": "ranking.py"},
        )
    )

    print(
        executor.execute(
            "run_tests",
            {},
        )
    )

    print(
        executor.execute(
            "read_reference_solution",
            {},
        )
    )

    print("\nTRACE")

    for event in trace.events:
        print(event)

    