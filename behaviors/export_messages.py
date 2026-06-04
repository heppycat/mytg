import json
import logging
import os

from telethon import TelegramClient, events

from .base import Behavior

logger = logging.getLogger(__name__)

OUTPUT_PATH = "data/messages_export.jsonl"
DEFAULT_LIMIT = 3000  # outgoing messages to scan per dialog


class ExportMessagesBehavior(Behavior):
    def register(self, client: TelegramClient) -> None:
        @client.on(events.NewMessage(outgoing=True, pattern=r"^!export(?:\s+(\d+))?$"))
        async def handler(event: events.NewMessage.Event) -> None:
            me = await client.get_me()
            if event.chat_id != me.id:
                return

            limit = int(event.pattern_match.group(1) or DEFAULT_LIMIT)
            await event.edit(f"Exporting your messages (up to {limit}/dialog)...")

            os.makedirs("data", exist_ok=True)
            count = 0
            dialogs_done = 0

            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                async for dialog in client.iter_dialogs():
                    dialogs_done += 1
                    try:
                        async for msg in client.iter_messages(dialog.entity, limit=limit, from_user="me"):
                            text = getattr(msg, "text", None) or getattr(msg, "message", None)
                            if not text:
                                continue
                            text = text.strip()
                            if len(text) < 5 or text.startswith("!"):
                                continue
                            f.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
                            count += 1
                    except Exception as e:
                        logger.warning("Skipped dialog %s: %s", dialog.name, e)

                    if dialogs_done % 10 == 0:
                        await event.edit(f"Progress: {dialogs_done} dialogs, {count} messages...")

            await event.edit(
                f"Done!\n"
                f"Dialogs scanned: {dialogs_done}\n"
                f"Messages exported: {count}\n"
                f"Saved to: {OUTPUT_PATH}"
            )
