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

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from . import config
from .progress import progress


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

    # --- agentic mode (tools ENABLED) -------------------------------------
    #
    # generate() above deliberately disables tools so the reply is plain text.
    # run_agent() is the opposite: a print-mode run that KEEPS tools on so the
    # model can drive an MCP server and write files itself (used by the
    # preparation step to fetch reference assets). Its return value is the final
    # text result; the real product is the side effects (files it wrote).

    def run_agent(self, prompt: str, *, mcp_config: "Optional[Path]" = None,
                  allowed_tools: "Optional[List[str]]" = None,
                  add_dirs: "Optional[List[Path]]" = None,
                  cwd: "Optional[Path]" = None,
                  timeout: "Optional[float]" = None) -> str:
        """Run ``claude`` agentically (tools on) and stream its progress.

        ``mcp_config`` points at an ``.mcp.json`` so the agent can call that
        server's tools; ``allowed_tools`` pre-approves tools (e.g.
        ``["Bash", "Write", "mcp__archi__*"]``) so nothing blocks on a prompt.
        Returns the agent's final text; raises ``SystemExit`` on a non-zero exit.
        """
        binary = self._resolve_binary()
        command = self._agent_command(binary, mcp_config, allowed_tools, add_dirs)
        return self._run_streaming(command, prompt, cwd=cwd, timeout=timeout)

    def _agent_command(self, binary: str, mcp_config: "Optional[Path]",
                       allowed_tools: "Optional[List[str]]",
                       add_dirs: "Optional[List[Path]]") -> List[str]:
        command = [
            binary, "-p",
            "--model", self.model,
            "--effort", self.effort,
            "--permission-mode", "bypassPermissions",
            "--dangerously-skip-permissions",
            "--output-format", "stream-json", "--verbose",
        ]
        if mcp_config:                           # load + ONLY use this MCP config
            command += ["--mcp-config", str(mcp_config), "--strict-mcp-config"]
        if allowed_tools:
            command += ["--allowedTools", ",".join(allowed_tools)]
        for d in add_dirs or []:
            command += ["--add-dir", str(d)]
        return command

    def _run_streaming(self, command: List[str], prompt: str, *,
                       cwd: "Optional[Path]" = None,
                       timeout: "Optional[float]" = None) -> str:
        """Run a stream-json print command, logging each event, return the result."""
        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True,
            cwd=str(cwd) if cwd else None,
        )
        assert proc.stdin and proc.stdout
        proc.stdin.write(prompt)
        proc.stdin.close()
        result_text = ""
        for line in proc.stdout:                 # NDJSON: one event per line
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue                         # ignore any non-JSON noise
            label = self._describe_event(event)
            if label:
                progress.log(f"    [prep] {label}")
            if event.get("type") == "result" and event.get("result"):
                result_text = event["result"]
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise SystemExit(f"{self.name} agentic run timed out after {timeout:.0f}s.")
        if code != 0:
            raise SystemExit(
                f"{self.name} agentic run failed (exit {code}). "
                f"If this says 'Not logged in', run `{command[0]} /login` once."
            )
        return result_text.strip()

    @staticmethod
    def _describe_event(event: dict) -> "Optional[str]":
        """Turn one stream-json event into a short human progress line (or None)."""
        etype = event.get("type")
        if etype == "system" and event.get("subtype") == "init":
            tools = event.get("mcp_servers") or []
            names = ", ".join(s.get("name", "?") for s in tools) if tools else "none"
            return f"session started (mcp servers: {names})"
        if etype == "assistant":
            for block in (event.get("message", {}) or {}).get("content", []) or []:
                if block.get("type") == "tool_use":
                    return f"using tool {block.get('name', '?')}"
                if block.get("type") == "text" and block.get("text", "").strip():
                    return block["text"].strip().splitlines()[0][:100]
            return None
        if etype == "result":
            turns = event.get("num_turns")
            return f"finished ({turns} turns)" if turns is not None else "finished"
        return None

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
