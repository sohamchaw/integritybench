from dataclasses import asdict, is_dataclass
from typing import Any

from scenario import Scenario
from tools import ToolRuntime
from trace import RunTrace, TraceEvent

class ToolExecutor:
    def __init__(
        self,
        runtime: ToolRuntime,
        scenario: Scenario,
        trace: RunTrace,
    ):
        self.runtime = runtime
        self.scenario = scenario
        self.trace = trace

        self.tools = {
            "list_files": runtime.list_files,
            "read_file": runtime.read_file,
            "search_repo": runtime.search_repo,
            "write_file": runtime.write_file,
            "run_tests": runtime.run_tests,
            "read_reference_solution": runtime.read_reference_solution,
        }

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        if tool_name not in self.tools:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        tool = self.tools[tool_name]

        forbidden = (
            tool_name in self.scenario.forbidden_tools
        )

        step = len(self.trace.events) + 1

        try:
            result = tool(**arguments)

            if is_dataclass(result):
                trace_result = asdict(result)
            else:
                trace_result = result

            event = TraceEvent(
                step=step,
                tool_name=tool_name,
                arguments=arguments,
                forbidden=forbidden,
                succeeded=True,
                result=trace_result,
            )

            self.trace.add(event)

            return result

        except Exception as exc:
            event = TraceEvent(
                step=step,
                tool_name=tool_name,
                arguments=arguments,
                forbidden=forbidden,
                succeeded=False,
                error=f"{type(exc).__name__}: {exc}",
            )

            self.trace.add(event)

            raise