from dataclasses import dataclass

from format import (
    display_error,
    display_tool_call,
    StreamingChatDisplay,
)
from llm import call_llm
from messages import AssistantMessage, Message, ToolCall, ToolFunction, ToolResult
from tools import tool_execute


@dataclass
class _ToolCallParts:
    id: str = ""
    name: str = ""
    arguments: str = ""


def agent_loop(client, messages: list[Message], config) -> tuple[list[Message], bool]:
    content_parts = []
    thinking_parts = []
    streamed_tool_calls: dict[int, _ToolCallParts] = {}

    with StreamingChatDisplay() as display:
        for chunk in call_llm(client, messages, config):
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            thinking = (
                getattr(delta, "reasoning", None)
                or getattr(delta, "thinking", None)
                or getattr(delta, "reasoning_content", None)
            )
            if thinking:
                thinking_parts.append(thinking)
                display.add_thinking(thinking)

            if delta.content:
                content_parts.append(delta.content)
                display.add_message(delta.content)

            for tool_call in delta.tool_calls or []:
                current_call = streamed_tool_calls.setdefault(
                    tool_call.index, _ToolCallParts()
                )
                if tool_call.id:
                    current_call.id += tool_call.id
                if tool_call.function:
                    current_call.name += tool_call.function.name or ""
                    current_call.arguments += tool_call.function.arguments or ""

    tool_calls = tuple(
        ToolCall(
            id=parts.id,
            type="function",
            function=ToolFunction(name=parts.name, arguments=parts.arguments),
        )
        for _, parts in sorted(streamed_tool_calls.items())
    )
    messages.append(AssistantMessage(
        role="assistant",
        content="".join(content_parts),
        reasoning="".join(thinking_parts),
        tool_calls=tool_calls,
    ))

    for tool_call in tool_calls:
        try:
            display_tool_call(tool_call.function.name, tool_call.function.arguments)
            output = tool_execute(tool_call)
        except Exception as failure:  # noqa: BLE001 - the model gets to see and retry
            error = f"Tool failed - {type(failure).__name__}: {failure}"
            display_error(error)
            messages.append(ToolResult(role="tool", tool_call_id=tool_call.id, error=error))
        else:
            messages.append(ToolResult(role="tool", tool_call_id=tool_call.id, output=output))

    return messages, not tool_calls
