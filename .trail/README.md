# .trail

What coding sessions on this repo worked out, kept next to the code so the
next session, yours or a teammate's, starts from it instead of digging again.

- learnings/   one file per learning someone asked their agent to save: what
               was decided, what was tried and ruled out, and what to watch
               out for, plus what it took to work out
- hook.cjs     what Claude Code runs at session start (`.claude/settings.json`).
               With trail installed it hands over to trail. Without it, it
               shows Claude these learnings and offers to set trail up.

Learnings stay on each machine: `.gitignore` lists `learnings/`, because this repository is
published and dated maintainer notes are what its packaging rule keeps out. Commit this
folder's `.gitignore` and `.claude/settings.json` once, and keep the learnings for your own
next session. They are short summaries, never transcripts, and plain markdown without trail
installed. What `.trail/.gitignore` lists stays on each machine.
