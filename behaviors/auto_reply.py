from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import UserStatusOnline
from .base import Behavior


class AutoReplyBehavior(Behavior):
    COOLDOWN = timedelta(hours=1)
    MESSAGE = "hi im not available right now, i will message you later."

    def __init__(self) -> None:
        self._last_replied: dict[int, datetime] = {}

    def register(self, client: TelegramClient) -> None:
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handler(event: events.NewMessage.Event) -> None:
            me = await client.get_me()
            if isinstance(me.status, UserStatusOnline):
                return

            now = datetime.now()
            if now - self._last_replied.get(event.sender_id, datetime.min) >= self.COOLDOWN:
                await event.reply(self.MESSAGE)
                self._last_replied[event.sender_id] = now
