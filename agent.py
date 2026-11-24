from openai.types.chat import ChatCompletionMessageToolCall

from format import (
    display_error,
    display_tool_call,
    StreamingChatDisplay,
)
from llm import call_llm
from tools import tool_execute


def agent_loop(client, messages, config):
    content_parts = []
    thinking_parts = []
    streamed_tool_calls = {}

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
                    tool_call.index,
                    {
                        "id": "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    },
                )
                if tool_call.id:
                    current_call["id"] += tool_call.id
                if tool_call.function and tool_call.function.name:
                    current_call["function"]["name"] += tool_call.function.name
                if tool_call.function and tool_call.function.arguments:
                    current_call["function"]["arguments"] += tool_call.function.arguments

    content = "".join(content_parts)
    thinking = "".join(thinking_parts)
    tool_call_data = [streamed_tool_calls[index] for index in sorted(streamed_tool_calls)]

    assistant_message = {"role": "assistant"}
    if content:
        assistant_message["content"] = content
    if thinking:
        assistant_message["reasoning"] = thinking
    if tool_call_data:
        assistant_message["tool_calls"] = tool_call_data
    messages.append(assistant_message)

    if not tool_call_data:
        return messages, True

    tool_calls = [ChatCompletionMessageToolCall.model_validate(call) for call in tool_call_data]
    for tool_call in tool_calls:
        try:
            display_tool_call(tool_call.function.name, tool_call.function.arguments)
            result = tool_execute(tool_call)
            if result is not None:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        except Exception as failure:  # noqa: BLE001 - the model gets to see and retry
            error = f"Tool failed - {type(failure).__name__}: {failure}"
            display_error(error)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": f"Error: {error}"
            })

    return messages, False
