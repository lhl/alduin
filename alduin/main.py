"""Alduin - A minimal CLI coding agent."""

import os
import rich
from typing import Any

import anthropic
import dotenv
from rich.console import Console

from alduin import llm, system_prompt, theme, ui

# Tools
from alduin.schema_converter import generate_tool_schema
from alduin.tool import bash, edit_file, list_files, read_file


def agent_loop(client: anthropic.Anthropic, console: Console) -> None:
    """Run the main agent loop: read input, call LLM, execute tools, repeat.

    Args:
        client: The initialized Anthropic client.
        console: The Rich Console for logging and UI.
    """

    conversation: list[dict[str, Any]] = []

    # tool_schemas = generate_tool_schema([read_file, edit_file, list_files, bash])

    while True:
        try:
            user_input = input("🧑‍💻 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            ui.clear_previous_line()
            ui.print_goodbye(console)
            return

        if not user_input:
            continue


        ui.clear_previous_line()
        ui.print_user_message(console, user_input)

        # Add user input to conversation
        conversation.append({"role": "user", "content": user_input})

        # Get LLM response
        assistant_reply = llm.call(
          client=client, 
          console=console, 
          system_prompt=system_prompt.get(),
          messages=conversation, 
          tool_schemas=[]
        )

        # Add response to the conversation
        conversation.append({'role': 'assistant', 'content': assistant_reply.content})

        # DEBUG
        # rich.print(assistant_reply)

        # Print response
        for block in assistant_reply.content:
            ui.print_assistant_reply(
                    console=console, 
                    text=block.text, 
                    input_tokens=assistant_reply.usage.input_tokens, 
                    output_tokens=assistant_reply.usage.output_tokens
            )


def main() -> None:
    """Entry point for the Alduin CLI agent.

    Initializes console, checks API key, and starts the agent loop.
    """

    console = Console(theme=theme.ALDUIN_THEME)
    ui.print_banner(console)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        ui.print_error(console, "ANTHROPIC_API_KEY environment variable is not set.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    agent_loop(client=client, console=console)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
