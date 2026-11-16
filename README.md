# tokfit-bench

Claude Code alone vs Claude Code + [tokfit](https://github.com/loisperrigon/tokfit-connector)
on [Terminal-Bench 4.0](https://www.tbench.ai), run with [Harbor](https://github.com/harbor-framework/harbor).

- **Same tasks, same model, same effort**: Claude Opus 5.5, `high`, both sides.
- **20 tasks** drawn at random (fixed seed `20261116`) from the 54 tasks that need
  no GPU, at most 8 GB and 4 CPUs: see `tasks.txt`.
- **One run per configuration**, both configurations started at the same time.
- Agent time capped at 2 h per task (official 8 h × 0.25), identical on both sides.
- Plain GitHub-hosted `ubuntu-latest` runners (x86_64): Terminal-Bench images are amd64-only.
- tokfit side: the published plugin, as customers install it, with its own trial key.

Every run's logs and trajectories are kept as workflow artifacts.

Run one task: *Actions → bench → Run workflow*, task name from `tasks.txt`.
