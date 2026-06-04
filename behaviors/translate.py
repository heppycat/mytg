import asyncio
import logging

from telethon import TelegramClient, events

from .base import Behavior

logger = logging.getLogger(__name__)

LANG_MAP: dict[str, str] = {
    "english": "en",
    "arabic": "ar",
    "persian": "fa",
}

_CODE_TO_NAME: dict[str, str] = {v: k.capitalize() for k, v in LANG_MAP.items()}


class TranslateBehavior(Behavior):
    def register(self, client: TelegramClient) -> None:
        @client.on(events.NewMessage(outgoing=True, pattern=r"^!tr\s+(\w+)\s*$"))
        async def handler(event: events.NewMessage.Event) -> None:
            lang_input = event.pattern_match.group(1).lower()
            target_code = LANG_MAP.get(lang_input)

            if target_code is None:
                await event.edit(
                    f"Unknown language '{lang_input}'. Available: english, arabic, persian."
                )
                return

            if not event.reply_to_msg_id:
                await event.edit("Reply to a message to translate it.")
                return

            replied = await event.get_reply_message()
            text = getattr(replied, "text", None) or getattr(replied, "message", None)

            if not text:
                await event.edit("No text to translate.")
                return

            try:
                from langdetect import LangDetectException, detect

                source_code: str = await asyncio.to_thread(detect, text)
            except Exception:
                source_code = "unknown"

            target_name = _CODE_TO_NAME.get(target_code, target_code.upper())

            if source_code == target_code:
                await event.edit(f"[Already in {target_name}]")
                return

            try:
                from deep_translator import GoogleTranslator

                translated: str = await asyncio.to_thread(
                    lambda: GoogleTranslator(source="auto", target=target_code).translate(text)
                )
            except Exception as e:
                logger.error("Translation failed: %s", e)
                await event.edit("[Translation failed]")
                return

            source_name = _CODE_TO_NAME.get(source_code, source_code.upper())
            await event.edit(f"[{source_name} → {target_name}]\n{translated}")
