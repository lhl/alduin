"""Module for tool implementations for the coding agent."""

import subprocess
from pathlib import Path


def read_file(path: str) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.

    Returns:
        The contents of the file, or an error message if it fails.
    """

    file_path = Path(path)
    if not file_path.is_file():
        return f"Error: file not found: {path}"

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error reading file '{path}': {exc}"


def edit_file(path: str, old_str: str, new_str: str) -> str:
    """Create or edit a file by replacing occurrences of a string.

    This tool can be used to do both, create a new file (if old_str is empty) or edit an existing file.

    Args:
        path: The path to the file to edit.
        old_str: The string to be replaced.
        new_str: The replacement string.

    Returns:
        A success message, or an error message if it fails.
    """

    file_path = Path(path)

    if old_str == "":
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(new_str, encoding="utf-8")
        except Exception as exc:
            return f"Error creating/updating '{path}': {exc}"
        return f"Created or replaced '{path}'."

    if not file_path.is_file():
        return f"Error: file not found: {path}"

    try:
        original = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error reading '{path}': {exc}"

    if old_str not in original:
        return f"Error: target string not found in '{path}'."

    replacement_count = original.count(old_str)
    updated = original.replace(old_str, new_str)
    try:
        file_path.write_text(updated, encoding="utf-8")
    except Exception as exc:
        return f"Error writing '{path}': {exc}"

    return f"Updated '{path}' ({replacement_count} replacement(s))."


def list_files(path: str) -> str:
    """List files in a directory.

    Args:
        path: The path to the directory to list files in.

    Returns:
        A newline-separated list of file names, or an error message.
    """

    p = Path(path)
    if not p.is_dir():
        if not p.exists():
            return f"Error: path does not exist: {path}"
        return f"Error: not a directory: {path}"

    contents = sorted(p.iterdir())
    if not contents:
        return "Directory is empty."

    lines = [f"{item.name}/" if item.is_dir() else item.name for item in contents]
    return "\n".join(lines)


def bash(command: str) -> str:
    """Execute a bash command and return its output.

    Ask the user for confirmation before executing, and handle errors gracefully.

    Args:
        command: The bash command to execute.

    Returns:
        The output of the command, or an error message.
    """

    if not command.strip():
        return "Error: empty command."

    confirmation = input(f"Allow execution of command: {command}\nRun? [y/N]: ").strip().lower()
    if confirmation not in {"y", "yes"}:
        return "Command execution canceled by user."

    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return f"Error running command '{command}': {exc}"

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    if completed.returncode != 0:
        parts = [f"Command failed with exit code {completed.returncode}."]
    else:
        parts = ["Command completed successfully."]

    if stdout:
        parts.append("STDOUT:")
        parts.append(stdout)
    if stderr:
        parts.append("STDERR:")
        parts.append(stderr)

    if len(parts) == 1:
        return "Command executed with no output."
    return "\n".join(parts)
