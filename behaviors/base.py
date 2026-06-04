from abc import ABC, abstractmethod
from telethon import TelegramClient


class Behavior(ABC):
    @abstractmethod
    def register(self, client: TelegramClient) -> None:
        """Attach event handlers to the client."""
