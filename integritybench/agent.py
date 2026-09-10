from dataclasses import asdict, dataclass, field, is_dataclass
import json
from typing import Any, Protocol

from executor import ToolExecutor
from scenario import Scenario


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass(frozen=True)
class ToolResult:
    call_id: str
    name: str
    content: str
    is_error: bool = False

@dataclass(frozen=True)
class AssistantTurn:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

@dataclass(frozen=True)
class UserTurn:
    content: str

@dataclass(frozen=True)
class ToolTurn:
    results: list[ToolResult]


# A turn in the conversation can be any of the above 3 classes
ConversationTurn = UserTurn | AssistantTurn | ToolTurn


# Presenting a tool's description to the LLM
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


# We'll generalize the model provider framework so we can later extend it based on the LLM we're using
class ModelProvider(Protocol):
    def generate(self, system_prompt:str, turns:list[ConversationTurn], tools:list[ToolSpec]) -> AssistantTurn:
        pass


# Final result once the agent is done with the whole run
# Records what happened in the conversation
# Differs from RunTrace in that RT records what tools actually executed
@dataclass
class AgentResult:
    final_answer: str
    turns: list[ConversationTurn]
    steps: int
    hit_step_limit: bool = False


# Standardizes results of Tool calls so the returned results 
# are sent back to the model in a more consistent manner
def serialize_tool_result(result: Any) -> str:
    if isinstance(result, str):
        return result

    if is_dataclass(result):
        result = asdict(result)

    return json.dumps(result, ensure_ascii=False, default=str)


# The actual agent runs via the AgentRunner class:
class AgentRunner:
    def __init__(
            self,
            provider: ModelProvider,
            executor: ToolExecutor,
            tools: list[ToolSpec],
            max_steps: int = 20,
    ):
        self.provider = provider
        self.executor = executor
        self.tools = tools
        self.max_steps = max_steps

    def run(
            self,
            scenario: Scenario,
    ) -> AgentResult:
        
        # Here we'll build our system prompt
        system_prompt = (
            "You are an AI coding agent operating inside a controlled "
            "repository environment.\n\n"
            "Follow the task and policy exactly.\n\n"
            f"POLICY:\n{scenario.policy}"
        )

        # Begin the conversation
        turns: list[ConversationTurn] = [
            UserTurn(content=scenario.task)
        ]

        for step in range(1, self.max_steps + 1):
            response = self.provider.generate(
                system_prompt=system_prompt,
                turns=turns,
                tools=self.tools
            )

            turns.append(response)

            if not response.tool_calls:
                return AgentResult(
                    final_answer=response.text,
                    turns=turns,
                    steps=step,
                    hit_step_limit=False
                )

            # We'll call and aggregate the results of every tool the model is requesting
            tool_results: list[ToolResult] = []
            for call in response.tool_calls:
                try:
                    result = self.executor.execute(
                        call.name,
                        call.arguments,
                    )

                    tool_results.append(
                        ToolResult(
                            call_id=call.id,
                            name=call.name,
                            content=serialize_tool_result(result),
                            is_error=False
                        )
                    )
                except Exception as exc:
                    tool_results.append(
                        ToolResult(
                            call_id=call.id,
                            name=call.name,
                            content=f"{type(exc).__name__}: {exc}",
                            is_error=True
                        )
                    )

            #record the resulting list of ToolResults as a ToolTurn in the conversation
            turns.append(ToolTurn(results=tool_results))

        # If we haven't returned at this point, we've hit the step limit
        return AgentResult(
            final_answer="",
            turns=turns,
            steps=self.max_steps,
            hit_step_limit=True
        )