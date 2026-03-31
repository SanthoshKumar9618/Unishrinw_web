from abc import ABC, abstractmethod


class TTSProvider(ABC):

    @abstractmethod
    async def synthesize(self, text: str, language: str, voice: str) -> str:
        """
        Returns file path or URL
        """
        pass