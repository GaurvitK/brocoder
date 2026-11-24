import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"

DEFAULT_MODEL = "qwen3:4b"
DEFAULT_REASONING_EFFORT = "low"
STREAM_RESPONSES = True


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str
    reasoning_effort: str
    stream_responses: bool


def load_config() -> Config:
    _load_env_file(ENV_FILE)

    return Config(
        api_key=_required_env("API_KEY"),
        base_url=_required_env("BASE_URL"),
        model=os.getenv("MODEL", DEFAULT_MODEL),
        reasoning_effort=os.getenv("REASONING_EFFORT", DEFAULT_REASONING_EFFORT),
        stream_responses=STREAM_RESPONSES,
    )


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"Invalid environment entry on line {line_number} of {path}")

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Copy .env.example to .env and provide a value."
        )
    return value
