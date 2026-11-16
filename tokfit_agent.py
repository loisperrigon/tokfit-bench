"""Claude Code avec le plugin tokfit publié, pour Harbor (Terminal-Bench).

Même agent que `claude-code` de Harbor, plus la copie publique du plugin (celle
qu'installent les clients) posée dans le conteneur et chargée par `--plugin-dir`,
avec la clé tokfit du banc (fichier hors dépôt, lu par la variable TOKFIT_CONFIG).
"""
import os
from pathlib import Path

from harbor.agents.installed.claude_code import ClaudeCode

PLUGIN = Path(os.environ.get("TOKFIT_PUBLIC_PLUGIN", "/tmp/tokfit-connector-pub/claude-code"))
CONFIG = Path(os.path.expanduser(os.environ.get("TOKFIT_BENCH_CONFIG", "~/.config/tokfit-bench/config.json")))
REMOTE_PLUGIN = "/opt/tokfit/plugin"
REMOTE_CONFIG = "/opt/tokfit/config.json"


class TokfitClaudeCode(ClaudeCode):
    @staticmethod
    def name() -> str:
        return "claude-code-tokfit"

    def build_cli_flags(self) -> str:
        base = super().build_cli_flags()
        return f"{base} --plugin-dir {REMOTE_PLUGIN}".strip()

    async def run(self, instruction, environment, context) -> None:  # type: ignore[no-untyped-def]
        await environment.upload_dir(PLUGIN, REMOTE_PLUGIN)
        await environment.upload_file(CONFIG, REMOTE_CONFIG)
        self._resolved_env_vars["TOKFIT_CONFIG"] = REMOTE_CONFIG
        await super().run(instruction, environment, context)
