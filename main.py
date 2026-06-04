import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

import config
from behaviors.auto_reply import AutoReplyBehavior
from behaviors.export_messages import ExportMessagesBehavior
from behaviors.translate import TranslateBehavior

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BEHAVIORS = [
    # AutoReplyBehavior(),
    TranslateBehavior(),
    ExportMessagesBehavior(),
]


async def main() -> None:
    if not config.SESSION_STRING:
        logger.info("No session found — starting interactive login")
        client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
        await client.start()
        print("\nSave this to SESSION_STRING in your .env:")
        print(client.session.save())
        await client.disconnect()
        return

    client = TelegramClient(StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH)
    for behavior in BEHAVIORS:
        behavior.register(client)
        logger.info("Registered behavior: %s", type(behavior).__name__)

    async with client:
        logger.info("Connected — running")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
