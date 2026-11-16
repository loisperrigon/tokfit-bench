"""Tableau des résultats : un summary.json par tâche et configuration, sous `results/`.

    python report.py results/   # Markdown sur la sortie standard
"""
import json
import sys
from pathlib import Path


def ligne(s: dict | None) -> str:
    if not s:
        return "— | — | — | —"
    ok = {1: "✅", 1.0: "✅", 0: "❌", 0.0: "❌"}.get(s.get("reward"), "⚠️ " + str(s.get("error")))
    cout = f"{s['cost_usd']:.2f} $" if isinstance(s.get("cost_usd"), (int, float)) else "—"
    duree = f"{s['agent_seconds'] / 60:.0f} min" if isinstance(s.get("agent_seconds"), (int, float)) else "—"
    sortie = f"{s['output_tokens']:,}".replace(",", " ") if isinstance(s.get("output_tokens"), int) else "—"
    return f"{ok} | {cout} | {duree} | {sortie}"


def main() -> None:
    racine = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    par_tache: dict[str, dict[str, dict]] = {}
    for f in racine.rglob("summary.json"):
        s = json.loads(f.read_text())
        par_tache.setdefault(s["task"], {})[s["config"]] = s
    print("| tâche | Claude Code : réussite | coût | durée | tokens de sortie | + tokfit : réussite | coût | durée | tokens de sortie |")
    print("|---|---|---|---|---|---|---|---|---|")
    for tache in sorted(par_tache):
        print(f"| {tache} | {ligne(par_tache[tache].get('vanilla'))} | {ligne(par_tache[tache].get('tokfit'))} |")


if __name__ == "__main__":
    main()
