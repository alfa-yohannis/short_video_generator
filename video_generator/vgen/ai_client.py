"""AI command-line clients — a Strategy hierarchy.

The program can ask either the **Claude** or the **Codex** CLI to write text
(narration, scene code, YouTube metadata). Both are used the same way — "here
is a prompt, give me back text" — but each is launched with different flags.

That is exactly the situation the **Strategy pattern** is for:

    AiClient (abstract)          <- the interface every caller depends on
      ├── ClaudeClient           <- one concrete strategy
      └── CodexClient            <- another concrete strategy

Callers (the narration writer, the scene synthesizer, ...) hold an ``AiClient``
and call :meth:`AiClient.generate`; they never check "is this claude or codex?".
To add a third CLI you write one new subclass and register it in the factory —
no caller changes. ``create_ai_client(name)`` is the factory that hides the
choice behind a single function.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from . import config


class AiClient(ABC):
    """The interface every part of the program uses to talk to an AI CLI."""

    #: Human-readable name, also the value used in the storyboard (``ai_cli:``).
    name: str = ""
    #: Environment variable that may override the binary location.
    env_var: str = ""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send ``prompt`` to the CLI and return its text reply."""

    def locate_binary(self) -> Optional[str]:
        """Find the CLI executable, or return ``None`` if it isn't installed.

        Honours ``$CLAUDE_BIN`` / ``$CODEX_BIN`` first, then ``PATH``, then
        ``~/.local/bin`` (where the official installers put it).
        """
        if self.env_var and os.environ.get(self.env_var):
            return os.environ[self.env_var]
        found = shutil.which(self.name)
        if found:
            return found
        local = Path.home() / ".local" / "bin" / self.name
        return str(local) if local.exists() else None

    def _resolve_binary(self) -> str:
        """Like :meth:`locate_binary` but raises a helpful error when missing."""
        path = self.locate_binary()
        if not path:
            raise SystemExit(self._not_found_message())
        return path

    def _not_found_message(self) -> str:
        return (
            f"AI CLI '{self.name}' not found. Install it, set ${self.env_var} to "
            "its path, or pre-fill narration / scene .py files in the storyboard."
        )

    # --- Template method: every CLI runs the same way, only the command differs.

    def _run(self, command: List[str], prompt: str) -> str:
        proc = subprocess.run(command, input=prompt, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stdout or "").strip() or (proc.stderr or "").strip() or "(no output)"
            raise SystemExit(
                f"{self.name} CLI failed (exit {proc.returncode}). Output: {detail}\n"
                f"If this says 'Not logged in', run `{command[0]} /login` once to "
                "authenticate before retrying."
            )
        return proc.stdout.strip()


class ClaudeClient(AiClient):
    """Drives Anthropic's ``claude`` CLI in non-interactive print mode.

    ``--tools ""`` disables all tools, which is essential: otherwise Claude Code
    behaves like an agent and *writes the file itself*, printing only a prose
    summary, instead of returning the file's text on stdout.
    """

    name = "claude"
    env_var = "CLAUDE_BIN"

    def __init__(self, model: str = config.DEFAULT_CLAUDE_MODEL,
                 effort: str = config.DEFAULT_CLAUDE_EFFORT) -> None:
        self.model = model
        self.effort = effort

    def generate(self, prompt: str) -> str:
        binary = self._resolve_binary()
        command = [
            binary, "-p",
            "--model", self.model,
            "--effort", self.effort,
            "--tools", "",                       # return text, don't write files
            "--permission-mode", "bypassPermissions",
            "--allow-dangerously-skip-permissions",
            "--disable-slash-commands",
        ]
        return self._run(command, prompt)

    def _not_found_message(self) -> str:
        return (
            "claude CLI not found. Install Claude Code "
            "(https://docs.claude.com/en/docs/claude-code/installation), or set "
            "$CLAUDE_BIN to its path, or pre-fill narration / scene .py files in "
            "the storyboard."
        )


class CodexClient(AiClient):
    """Drives OpenAI's ``codex`` CLI. ``--sandbox read-only`` stops it writing
    files (the same agentic pitfall as Claude), so the reply lands on stdout.

    Defaults to the flagship model at codex's highest reasoning effort ("high"
    = max capacity for codex), independent of ClaudeClient's effort default.
    """

    name = "codex"
    env_var = "CODEX_BIN"

    def __init__(self, model: "Optional[str]" = config.DEFAULT_CODEX_MODEL,
                 reasoning: str = config.DEFAULT_CODEX_REASONING) -> None:
        self.model = model
        self.reasoning = reasoning

    def generate(self, prompt: str) -> str:
        binary = self._resolve_binary()
        command = [binary, "exec", "--sandbox", "read-only"]
        if self.model:                       # only pin a model if one is set
            command += ["--model", self.model]
        command += ["-c", f'model_reasoning_effort="{self.reasoning}"']
        return self._run(command, prompt)


# Registry the factory looks up. Add a new CLI by writing a subclass and
# adding one entry here — nothing else changes.
_CLIENTS = {
    "claude": ClaudeClient,
    "codex": CodexClient,
}


def create_ai_client(name: str, effort: "Optional[str]" = None) -> AiClient:
    """Factory: build the :class:`AiClient` for a storyboard's ``ai_cli`` value.

    ``effort`` sets Claude's reasoning tier (low/medium/high/xhigh/max). It only
    applies to :class:`ClaudeClient`; codex has its own reasoning default and
    ignores it.
    """
    try:
        cls = _CLIENTS[name]
    except KeyError:
        raise SystemExit(f"Unknown ai_cli '{name}'. Use 'claude' or 'codex'.")
    if cls is ClaudeClient and effort:
        return cls(effort=effort)
    return cls()
