# Security

Short version: **the optional render server in `server/` executes arbitrary
Python by design.** Keep it on loopback. Everything else in this skill is
scripts you run yourself against your own files.

## The render server executes the code you send it

`server/server.py` exists so a coding agent can iterate on build123d models:
POST modeling code to `/model/create`, get back a rendered PNG, adjust, repeat.
That endpoint runs the code with `exec()`. There is no sandbox, and adding one
would defeat the purpose — the code *is* the input.

This is fine on loopback and dangerous anywhere else. An unauthenticated
`exec()` endpoint reachable from your network is a remote shell for anyone on
that network.

**How it's configured to keep that safe:**

| Launch method | Binds to | Safe by default |
| --- | --- | --- |
| `./run_local.sh` or `python server.py` | `127.0.0.1:8123` | Yes |
| `docker compose up -d --build` | `127.0.0.1:8123` on the host | Yes |

The Docker path is worth understanding, because the two settings look
contradictory and only one of them controls exposure:

- `ENV HOST=0.0.0.0` in the `Dockerfile` binds all interfaces **inside the
  container**. Required for the published port to reach the process.
- `- "127.0.0.1:8123:8123"` in `docker-compose.yml` publishes it to **your
  host's loopback only**. This is the line that matters.

Dropping the `127.0.0.1:` prefix — making it a plain `8123:8123` — publishes
the exec endpoint on every interface on your machine. Don't. If you need it
from another machine, forward it over SSH:

```bash
ssh -L 8123:127.0.0.1:8123 user@your-machine
```

Also note `restart: unless-stopped`: once started under Docker, the server comes
back after reboots until you explicitly `docker compose down`. That's convenient
and it means you should know it's running. `curl -s localhost:8123/health` tells
you.

**You don't need the server at all.** build123d works headless, and the skill
treats renders as a sanity check rather than evidence — cross-sections and
watertightness checks are the real verification. If you'd rather not run it,
delete `server/`; nothing else depends on it.

## Never commit printer credentials

`.gitignore` excludes `.env`, `*.local.md` and `print-log.json`. Printer serial
numbers, LAN IPs, Bambu access codes, cloud tokens and MQTT credentials belong
in your OS keychain or environment, never in a file in this repository.

The `SKILL.md` instructions tell Claude the same thing: leave `bambu_serial`,
`bambu_token` and `host` unset on printer MCP calls so they resolve from the
server's own environment instead of passing through a conversation. Use
placeholders in any documentation you add: `<printer-lan-ip>`,
`<printer-serial>`, `<access-code>`.

## The print log is personal data

`print-log.json` records what you printed and when. It's gitignored. If you want
it backed up, put it somewhere you control rather than in a public repository.

## What this skill will not do

Two refusals are load-bearing rather than cautious, and you should not "fix"
them:

- **It will not fabricate a machine profile to satisfy a slicer.** A profile
  carries bed shape, toolhead clearance and start/end G-code; an invented one
  produces plausible G-code that can drive the toolhead into a printed part
  hours into a job, and you cannot tell good G-code from bad by reading it.
- **It will not guess `bambu_model` on a slice or print call.** The wrong model
  drives the wrong machine profile, which is the same failure by another route.

## Reporting

Found something? Open an issue. If it's a vulnerability you'd rather not post
publicly, open a minimal issue asking for a contact and it can move to private
disclosure from there.
