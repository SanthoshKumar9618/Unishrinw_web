import os
import time
import httpx
import subprocess
import shutil

from typing import List, Dict

from src.application.interfaces.llm_provider import LLMProvider
from src.application.interfaces.stt_provider import STTProvider
from src.application.interfaces.tts_provider import TTSProvider
from src.config.settings import settings


class VoiceService:
    def __init__(self, llm: LLMProvider, stt: STTProvider, tts: TTSProvider):
        self.llm = llm
        self.stt = stt
        self.tts = tts

        self.ffmpeg_path = os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg")

        if not self.ffmpeg_path:
            self.ffmpeg_path = r"D:\Zeva.AI\zeva-ai\ffmpeg-8.1-essentials_build\bin\ffmpeg.exe"

        if not os.path.exists(self.ffmpeg_path):
            raise RuntimeError(f"FFmpeg not found: {self.ffmpeg_path}")

        print(f"✅ Using FFmpeg: {self.ffmpeg_path}")

    # =========================
    # SPEECH → TEXT
    # =========================
    async def speech_to_text(self, audio_bytes: bytes | None) -> str:
        if not audio_bytes or len(audio_bytes) < 1000:
            print("⚠️ No valid audio")
            return ""

        try:
            print("AUDIO SIZE:", len(audio_bytes))

            text = await self.stt.transcribe(audio_bytes)

            print("🧠 STT TEXT:", text)

            if not text or len(text.strip()) < 2:
                return ""

            return text.strip()

        except Exception as e:
            print("STT ERROR:", str(e))
            return ""

    # =========================
    # LLM RESPONSE (🔥 FIXED)
    # =========================
    async def generate_response(self, prompt: str) -> str:

        start = time.time()

        try:
            response = await self.llm.generate(prompt)
        except Exception as e:
            print("[LLM ERROR]:", str(e))
            return "Sorry, something went wrong."

        latency = time.time() - start
        print(f"[LLM] LATENCY: {latency:.2f}s")

        print("🤖 AI RESPONSE:", response)

        if not response or len(response.strip()) < 3:
            return "Can you please clarify your requirement?"

        return response.strip()

        

    # =========================
    # TEXT → SPEECH
    # =========================
    async def text_to_speech(self, text: str, language: str, voice: str) -> str:
        start = time.time()

        try:
            file_path = await self.tts.synthesize(
                text=text,
                language=language,
                voice=voice
            )
        except Exception as e:
            print("[TTS ERROR]:", str(e))
            raise RuntimeError("TTS failed")

        if not file_path or not os.path.exists(file_path):
            raise RuntimeError("TTS failed")

        latency = time.time() - start
        print(f"[TTS] LATENCY: {latency:.2f}s")

        return f"{settings.PUBLIC_BASE_URL}/audio/{os.path.basename(file_path)}?t={int(time.time())}"
    
    
        # =========================
    # STRUCTURED DATA EXTRACTION
    # =========================
    async def extract_structured_data(self, conversation):
        # 🔥 simple version (replace later with LLM parsing)
        return {
            "intent": "website_inquiry",
            "message_count": len(conversation)
        }

    # =========================
    # STORE CONVERSATION
    # =========================
    async def store_conversation(
        self,
        lead_id: str,
        session_id: str,
        transcript,
        extracted: dict
    ):
        # 🔥 TEMP LOGGING (replace with DB later)
        print("💾 STORING CONVERSATION")
        print("lead_id:", lead_id)
        print("session_id:", session_id)
        print("messages:", len(transcript))
        print("extracted:", extracted)

        return True