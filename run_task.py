"""Une tâche de Terminal-Bench 4.0, une configuration : `vanilla` (Claude Code seul)
ou `tokfit` (Claude Code + plugin tokfit publié). Même modèle et même réflexion
des deux côtés (Opus 5.5, medium), agent plafonné à 2 h (8 h officielles x 0.25).

    python run_task.py <tache> <vanilla|tokfit>

Écrit `out/<config>/summary.json` : réussite, coût estimé par Claude Code,
tokens, durées, erreur éventuelle. Le jeton de l'abonnement est lu dans
l'environnement (CLAUDE_CODE_OAUTH_TOKEN) par le gabarit ${...} de Harbor :
il n'apparaît ni en ligne de commande ni dans les fichiers.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent
MODELE = "anthropic/claude-opus-5-5"
EFFORT = "medium"
MULTIPLICATEUR = 0.25
AGENTS = {"vanilla": ["-a", "claude-code"], "tokfit": ["-a", "tokfit_agent:TokfitClaudeCode"]}


def secondes(debut: str | None, fin: str | None) -> float | None:
    if not debut or not fin:
        return None
    return (datetime.fromisoformat(fin) - datetime.fromisoformat(debut)).total_seconds()


def resume(tache: str, config: str, dossier: Path) -> dict:
    trouves = sorted(dossier.glob(f"{tache}/*/result.json"))
    if not trouves:
        return {"task": tache, "config": config, "error": "aucun résultat"}
    r = json.loads(trouves[-1].read_text())
    agent = r.get("agent_result") or {}
    rewards = (r.get("verifier_result") or {}).get("rewards") or {}
    execution = r.get("agent_execution") or {}
    erreur = r.get("exception_info")
    return {
        "task": tache,
        "config": config,
        "reward": rewards.get("reward"),
        "cost_usd": agent.get("cost_usd"),
        "input_tokens": agent.get("n_input_tokens"),
        "cache_tokens": agent.get("n_cache_tokens"),
        "output_tokens": agent.get("n_output_tokens"),
        "model_usage": agent.get("model_usage"),
        "agent_seconds": secondes(execution.get("started_at"), execution.get("finished_at")),
        "total_seconds": secondes(r.get("started_at"), r.get("finished_at")),
        "error": (erreur or {}).get("exception_type"),
    }


def main() -> int:
    tache, config = sys.argv[1], sys.argv[2]
    sortie = ICI / "out" / config
    sortie.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ICI)}
    env.pop("ANTHROPIC_API_KEY", None)
    commande = ["harbor", "run", "-p", str(ICI / "tasks" / "terminal-bench" / tache), *AGENTS[config],
                "-m", MODELE, "--ak", f"reasoning_effort={EFFORT}",
                "--agent-timeout-multiplier", str(MULTIPLICATEUR), "-n", "1",
                "-o", str(sortie / "jobs"), "--job-name", tache, "--yes",
                "--ae", "CLAUDE_CODE_OAUTH_TOKEN=${CLAUDE_CODE_OAUTH_TOKEN}"]
    code = subprocess.run(commande, env=env, cwd=ICI).returncode
    synthese = resume(tache, config, sortie / "jobs")
    synthese["harbor_exit"] = code
    (sortie / "summary.json").write_text(json.dumps(synthese, indent=2, ensure_ascii=False))
    print(json.dumps(synthese, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
