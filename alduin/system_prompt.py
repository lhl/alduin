"""Module for defining the system prompt for Alduin, the coding assistant."""

from pathlib import Path
import textwrap


def _load_agents_instructions() -> str:
    """Load optional AGENTS.md instructions from common project locations."""
    candidates = [
        Path.cwd() / "AGENTS.md",
        Path(__file__).resolve().parent / "AGENTS.md",
    ]

    for path in candidates:
        if path.is_file():
            try:
                return path.read_text(encoding="utf-8").strip()
            except OSError:
                return ""
    return ""


def get() -> str:
    """Create the system prompt for Alduin.

    Returns:
        The system prompt.
    """

    base_prompt = textwrap.dedent(
        """\
            You are Alduin, a helpful and precise coding assistant for software developers.
            Keep responses concise and practical. Output should always be in markdown format.
        """
    ).strip()

    agents = _load_agents_instructions()
    if not agents:
        return base_prompt

    return (
        f"{base_prompt}\n\n"
        "Repository-specific instructions:\n"
        f"{agents}"
    )
