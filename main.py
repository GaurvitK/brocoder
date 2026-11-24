import os

from openai import OpenAI

from agent import agent_loop
from format import prompt_user_message
from llm import SYSTEM_PROMPT


def read_env():
    env_fields = {}
    current_path = os.getcwd()
    with open(current_path + '/.env') as f:
        for line in f:
            env_var, value = line.strip().split("=", 1)
            if env_var.startswith("#"):
                continue
            env_fields[env_var.lower()] = value

    return env_fields


client = OpenAI(**read_env())

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}, 
]

while True:
    try:
        user_input = prompt_user_message()
    except EOFError:
        break

    if user_input.strip() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    while True:
        messages, is_done = agent_loop(client, messages)

        if is_done:
            break
