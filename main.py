from openai import OpenAI

from agent import agent_loop
from config import load_config
from format import prompt_user_message
from llm import SYSTEM_PROMPT
from messages import Message, SystemMessage, UserMessage


def main():
    config = load_config()
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    messages: list[Message] = [SystemMessage(role="system", content=SYSTEM_PROMPT)]

    while True:
        try:
            user_input = prompt_user_message()
        except EOFError:
            break

        if user_input.strip() == "/bye":
            break

        messages.append(UserMessage(role="user", content=user_input))

        while True:
            messages, is_done = agent_loop(client, messages, config)

            if is_done:
                break


if __name__ == "__main__":
    main()
