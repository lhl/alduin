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

TOOL_FUNCTIONS = {
    'read_file': read_file,
    'edit_file': edit_file,
    'list_files': list_files,
    'bash': bash,
}

def execute_tool(
    *,
    console: Console,
    name: str,
    request: Any,
    definition: dict[str, Any],
    conversation: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute a tool call and record a tool_result message payload."""
    _ = definition  # kept for compatibility with caller-provided tool metadata

    args = getattr(request, "input", {})
    if not isinstance(args, dict):
        args = {}

    ui.print_tool_request(console=console, name=name, args=args)

    tool_fn = TOOL_FUNCTIONS.get(name)
    if tool_fn is None:
        error = f"Tool '{name}' is not available."
        ui.print_tool_error(console=console, name=name, error=error)
        result_block = {
            "type": "tool_result",
            "tool_use_id": getattr(request, "id", ""),
            "is_error": True,
            "content": error,
        }
    else:
        try:
            result = tool_fn(**args)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            ui.print_tool_error(console=console, name=name, error=error)
            result_block = {
                "type": "tool_result",
                "tool_use_id": getattr(request, "id", ""),
                "is_error": True,
                "content": error,
            }
        else:
            text_result = result if isinstance(result, str) else str(result)
            ui.print_tool_result(console=console, name=name, result=text_result)
            result_block = {
                "type": "tool_result",
                "tool_use_id": getattr(request, "id", ""),
                "content": text_result,
            }

    if conversation is not None:
        conversation.append({"role": "user", "content": [result_block]})

    return result_block


def agent_loop(client: anthropic.Anthropic, console: Console) -> None:
    """Run the main agent loop: read input, call LLM, execute tools, repeat.

    Args:
        client: The initialized Anthropic client.
        console: The Rich Console for logging and UI.
    """

    conversation: list[dict[str, Any]] = []

    active_tools = generate_tool_schema([read_file, edit_file, list_files, bash])
    tools = {t['name']: t for t in active_tools}

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
        while True:
            assistant_reply = llm.call(
              client=client,
              console=console,
              system_prompt=system_prompt.get(),
              messages=conversation,
              tool_schemas=active_tools
            )

            # Add response to the conversation
            conversation.append({'role': 'assistant', 'content': assistant_reply.content})

            requires_tool_call = False
            for block in assistant_reply.content:
                if block.type == 'text':
                    ui.print_assistant_reply(
                        console=console,
                        text=block.text,
                        input_tokens=assistant_reply.usage.input_tokens,
                        output_tokens=assistant_reply.usage.output_tokens
                    )
                else:
                    requires_tool_call = True
                    rich.print(block)

                    execute_tool(
                        console=console,
                        name=block.name,
                        request=block,
                        definition=tools.get(block.name, {}),
                        conversation=conversation
                    )

            if not requires_tool_call:
                break


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
