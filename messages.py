from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MessageModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class SystemMessage(MessageModel):
    role: Literal["system"]
    content: str


class UserMessage(MessageModel):
    role: Literal["user"]
    content: str


class ToolFunction(MessageModel):
    name: str
    arguments: str


class ToolCall(MessageModel):
    id: str
    type: Literal["function"]
    function: ToolFunction


class AssistantMessage(MessageModel):
    role: Literal["assistant"]
    content: str = Field(default="", exclude_if=lambda text: text == "")
    reasoning: str = Field(default="", exclude_if=lambda text: text == "")
    tool_calls: tuple[ToolCall, ...] = Field(default=(), exclude_if=lambda calls: calls == ())


class ToolResult(MessageModel):
    role: Literal["tool"]
    tool_call_id: str
    output: str = Field(default="", exclude=True)
    error: str | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def content(self) -> str:
        return self.output if self.error is None else f"Error: {self.error}"


Message = SystemMessage | UserMessage | AssistantMessage | ToolResult
