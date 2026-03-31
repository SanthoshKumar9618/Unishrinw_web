import asyncio
from typing import AsyncIterator
from src.application.interfaces.tts_provider import TTSProvider


class MockStreamingTTSProvider(TTSProvider):
    """
    Mock streaming TTS provider.
    Simulates chunked audio output.
    """

    async def stream_audio(self, text: str) -> AsyncIterator[bytes]:
        words = text.split()

        for word in words:
            await asyncio.sleep(0.03)

            # Simulated audio frame
            yield f"AUDIO({word})".encode("utf-8")