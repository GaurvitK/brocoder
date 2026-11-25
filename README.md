# Brocoder

Brocoder is a terminal-based coding assistant that can inspect a project, read files, run commands, and answer questions about the codebase. It supports OpenAI-compatible model providers, including optional local models through Ollama.

## Features

- [x] Terminal chat with in-memory conversation history
- [x] Streaming responses and reasoning when the model provides it
- [x] Markdown rendering and visible tool activity
- [x] File reading and shell command execution through tool calls
- [x] Typed messages, a shared tool registry, and Pydantic validation for tool arguments
- [x] Configurable OpenAI-compatible providers, with optional local models through Ollama
- [ ] Add tool-round limits, command timeouts, and output limits
- [ ] Add automated tests for streaming, tool validation, and failure handling
- [ ] Save and resume conversations across sessions
- [ ] Compaction of older turns when conversation history grows
- [ ] Inject relevant project context when a turn needs it
- [ ] TODOs and Plans
- [ ] Sandboxing
- [ ] Launching subagents to offload tasks with fresh context


## Requirements

- Python 3.10 or newer
- Access to an OpenAI-compatible model provider
- Ollama only when using a local model

## Setup

Clone the repository and enter its directory.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Set `BASE_URL` and `API_KEY` in `.env` for your provider. You can also override the default `MODEL` and `REASONING_EFFORT` values there.

Run Brocoder from the repository directory:

```bash
python main.py
```

Enter `/bye` to end the session.

## Optional local setup with Ollama

Pull and serve a model:

```bash
ollama pull qwen3:4b
ollama serve
```

Configure `.env` to use Ollama's OpenAI-compatible endpoint:

```dotenv
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=qwen3:4b
```

Ollama requires an API key value for compatibility with the OpenAI client but does not use it for local authentication.

## Configuration

Runtime defaults are defined in `config.py`. Sensitive provider values belong in `.env`, which is excluded from version control. Use `.env.example` as the template for new installations.
