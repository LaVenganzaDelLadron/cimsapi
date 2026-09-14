from dataclasses import dataclass, field
from .tool_call import ToolCall
from .usage import Usage

@dataclass(slots=True)
class AIResponse:
    content: str | None
    model: str
    usage: Usage
    finish_reason: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)