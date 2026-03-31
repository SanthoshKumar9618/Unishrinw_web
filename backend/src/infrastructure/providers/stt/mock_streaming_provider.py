import asyncio
from src.infrastructure.providers.stt.provider import StreamingSTTProvider


class MockStreamingSTTProvider(StreamingSTTProvider):

    def __init__(self):
        self._buffer = []

    async def start(self) -> None:
        pass

    async def send_audio(self, chunk: bytes) -> None:
        self._buffer.append(chunk)

    async def receive_transcript(self) -> str | None:
        await asyncio.sleep(0.01)
        if self._buffer:
            self._buffer.clear()
            return "mock_transcript"
        return None

    async def close(self) -> None:
        self._buffer.clear()