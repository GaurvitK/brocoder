import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from messages import ToolCall


class ToolName(Enum):
    SHELL = "shell"
    READ_FILE = "read_file"


@dataclass(frozen=True)
class ToolDefinition:
    description: str
    arguments: type[BaseModel]
    handler: Callable[..., str]


class ShellArgs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    command: str = Field(description="The shell command to run")


class ReadFileArgs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    path: str = Field(description="Path to the file to read")


def tool_execute(tool_call: ToolCall) -> str:
    function = tool_call.function
    try:
        name = ToolName(function.name)
    except ValueError:
        raise ValueError(f"Unknown tool {function.name!r}") from None

    tool = _TOOLS[name]
    args = tool.arguments.model_validate_json(function.arguments)
    return tool.handler(**args.model_dump())


def shell_tool(command: str) -> str:
    """Run an shell command and return it's combined stdout and stderr""" 
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    except subprocess.TimeoutExpired as expired:
        # Hand the failure back as a result. A slow command is the model's
        # problem to work around, not a reason to take the session down.
        return (
            f"Timed out after {expired.timeout}s and was killed. "
            "Narrow it down - search inside the working directory rather than /."
        )
    return result.stdout + result.stderr

def read_file(path: str) -> str:
    """Read a file and return its contents."""
    with open(path) as f:
        return f.read()


_TOOLS = {
    ToolName.SHELL: ToolDefinition(
        description="Run a shell command and return its combined stdout and stderr.",
        arguments=ShellArgs,
        handler=shell_tool,
    ),
    ToolName.READ_FILE: ToolDefinition(
        description="Read a file and return its contents.",
        arguments=ReadFileArgs,
        handler=read_file,
    ),
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": name.value,
            "description": tool.description,
            "parameters": tool.arguments.model_json_schema(),
        },
    }
    for name, tool in _TOOLS.items()
]
