import httpx
import os

from src.application.interfaces.stt_provider import STTProvider
from src.config.settings import settings

class DeepgramProvider(STTProvider):
    def __init__(self):
        self.api_key = settings.deepgram_api_key   # ✅ FIX
        self.url = "https://api.deepgram.com/v1/listen"

    async def transcribe(self, audio_bytes: bytes) -> str:
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/webm"
            }

            params = {
                "model": "nova-2",
                "smart_format": "true"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    self.url,
                    headers=headers,
                    params=params,
                    content=audio_bytes
                )

            data = response.json()

            # 🔥 DEBUG
            print("🧠 DEEPGRAM RAW:", data)
            print("DG KEY:", self.api_key)

            text = (
                data.get("results", {})
                .get("channels", [{}])[0]
                .get("alternatives", [{}])[0]
                .get("transcript", "")
            )

            return text

        except Exception as e:
            print("❌ Deepgram Error:", str(e))
            return ""