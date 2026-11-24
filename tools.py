import subprocess
import json

from format import display_error


def tool_execute(tool_call):
    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    if tool_name == "shell":
        result = shell_tool(**arguments)
    elif tool_name == "read_file":
        result = read_file(**arguments)
    else:
        display_error(f"Unknown tool {tool_name!r}")
        result = None

    return result
    

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


SHELL_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "shell",
        "description": "Run a shell command and return its combined stdout and stderr.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run",
                }
            },
            "required": ["command"],
        },
    },
}

READ_FILE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file and return its contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                }
            },
            "required": ["path"],
        },
    },
}
