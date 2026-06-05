# CLAUDE.md — Project Context for AI Assistants

## What This Project Is

A Telegram userbot built on Telethon. It connects to the user's own Telegram account and runs pluggable "behaviors" — self-contained event handlers that react to account activity (incoming DMs, group messages, etc.). No bot API token, no job queue, no database. The focus is on staying minimal while being easy to extend.

## Tech Stack

- **Python 3.11+**
- **Telethon 1.x** — Telegram MTProto user client (personal account, StringSession)
- **python-dotenv** — `.env` loading

## Architecture Overview

```
main.py              Entry point — builds client, registers behaviors, runs
config.py            .env loading, typed module-level constants
behaviors/
  base.py            Behavior ABC — single abstract method: register(client)
  auto_reply.py      DM auto-reply with per-sender 1-hour cooldown
```

## Key Design Decisions

- **No bot API**: This is a userbot — Telethon connects to the user's own account, not a bot token.
- **Behavior pattern**: Each behavior is a class subclassing `Behavior` (from `behaviors/base.py`). It calls `client.on(...)` inside its own `register(client)` method. Behaviors own their own state as instance variables — no shared state.
- **`BEHAVIORS` list in `main.py`**: The single place where behaviors are activated. Add one line to enable a new behavior, remove one line to disable it.
- **StringSession in `.env`**: The session string is stored in `SESSION_STRING`. First run (empty `SESSION_STRING`): interactive login prints the string to paste into `.env`. No DB needed.
- **Two-mode `main.py`**: If `SESSION_STRING` is empty → interactive login and exit. Otherwise → register behaviors and run.

## Adding a New Behavior

1. Create `behaviors/my_thing.py` with a class extending `Behavior`.
2. Implement `register(self, client)` — attach `@client.on(...)` handlers inside it.
3. Add one line to `BEHAVIORS` in `main.py`.

That's it. No registration system, no config DB, no other files to touch.

## Config

All config lives in `.env`:

| Key | Required | Description |
|---|---|---|
| `API_ID` | Yes | Telegram app API ID (from my.telegram.org/apps) |
| `API_HASH` | Yes | Telegram app API hash |
| `SESSION_STRING` | No | Telethon StringSession; empty on first run |

## Running

```bash
pip install -r requirements.txt

# First run — generates SESSION_STRING
python main.py
# Paste the printed SESSION_STRING into .env

# Normal run
python main.py
```

## Common Patterns

- **Logging**: `logger = logging.getLogger(__name__)` in every module. No print statements except the first-run session string output.
- **Per-sender cooldown**: Use `dict[int, datetime]` as an instance variable; default to `datetime.min` so the first event always triggers.
- **Private message check**: `func=lambda e: e.is_private` in the `events.NewMessage` filter.
- **Incoming-only**: Always pass `incoming=True` to avoid reacting to the user's own sent messages.

## Gotchas

- **Self-messages**: Without `incoming=True`, a behavior will also fire on messages the user sends. Almost never what you want.
- **Session expiry**: If Telegram invalidates the session (e.g., password change, forced logout), delete `SESSION_STRING` from `.env` and re-run for a fresh login.
- **Rate limits**: Telethon handles flood waits automatically, but behaviors that send many messages in rapid succession can still trigger account restrictions. Build per-sender cooldowns into any reply behavior.
- **Groups vs DMs**: `e.is_private` is `True` only for one-on-one chats. Use `e.is_group` or `e.is_channel` to target other chat types.
