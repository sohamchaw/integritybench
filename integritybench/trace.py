from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TraceEvent:
    step: int
    tool_name: str
    arguments: dict[str, Any]
    forbidden: bool
    succeeded: bool
    result: Any | None = None
    error: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __str__(self) -> str:
        policy = "FORBIDDEN" if self.forbidden else "allowed"
        status = "OK" if self.succeeded else "ERROR"

        header = (
            f"[Step {self.step}] {self.tool_name} "
            f"({policy}) -> {status}"
        )

        lines = [header]

        if self.arguments:
            lines.append(f"  args: {self.arguments}")

        if self.error is not None:
            lines.append(f"  error: {self.error}")

        elif isinstance(self.result, dict) and "passed" in self.result:
            lines.append(
                "  result: "
                f"tests_passed={self.result['passed']}, "
                f"exit_code={self.result['exit_code']}, "
                f"timed_out={self.result['timed_out']}"
            )

        elif isinstance(self.result, list):
            lines.append(f"  result: {self.result}")

        elif isinstance(self.result, str):
            preview = self.result.replace("\n", " ")

            lines.append(f"  result: {preview}")

        elif self.result is not None:
            lines.append(f"  result: {self.result}")

        lines.append(f"  time: {self.timestamp}")

        return "\n".join(lines)


@dataclass
class RunTrace:
    run_id: str
    scenario_id: str
    events: list[TraceEvent] = field(default_factory=list)

    def add(self, event: TraceEvent) -> None:
        self.events.append(event)