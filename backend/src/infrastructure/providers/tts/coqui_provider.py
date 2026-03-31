import uuid
import os
import edge_tts
import asyncio


class CoquiProvider:
    def __init__(self):
        self.audio_dir = os.path.join("storage", "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    async def synthesize(self, text: str, language: str, voice: str) -> str:

        # 🔥 FIX 1: fallback for empty text
        if not text or len(text.strip()) < 3:
            text = "Sorry, I didn't catch that. Can you repeat?"

        file_name = f"{uuid.uuid4()}.mp3"
        file_path = os.path.join(self.audio_dir, file_name)

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice or "en-US-AriaNeural"
        )

        try:
            await communicate.save(file_path)
        except Exception as e:
            print("TTS ERROR:", e)
            text = "Sorry, something went wrong."
            communicate = edge_tts.Communicate(
                text=text,
                voice="en-US-AriaNeural"
            )
            await communicate.save(file_path)

        await asyncio.sleep(0.1)

        # 🔥 FIX 2: retry if file too small
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            print("Retrying TTS...")

            communicate = edge_tts.Communicate(
                text="Please repeat your request.",
                voice="en-US-AriaNeural"
            )

            await communicate.save(file_path)
            await asyncio.sleep(0.1)

        # final validation
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            raise RuntimeError("TTS failed completely")

        return file_path