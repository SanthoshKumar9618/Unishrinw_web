from src.application.dto.voice_dto import ProcessVoiceDTO

class ProcessVoiceUseCase:

    def __init__(self, voice_service, session_store):
        self.voice_service = voice_service
        self.session_store = session_store

    async def execute(self, dto, audio_bytes):

        session_id = dto["session_id"]

        # =========================
        # LOAD SESSION
        # =========================
        session = await self.session_store.get(session_id)
        history = session.get("history", []) if session else []

        print("📦 RAW HISTORY:", history)

        # =========================
        # STT
        # =========================
        user_text = await self.voice_service.speech_to_text(audio_bytes)

        print("🧾 USER TEXT:", user_text)

        if not user_text or len(user_text.strip()) == 0:
            return await self._fallback(dto, "I couldn't hear you clearly. Please speak again.")

        # =========================
        # STORE USER
        # =========================
        await self.session_store.append(session_id, "user", user_text)

        session = await self.session_store.get(session_id)
        history = session.get("history", [])

        # =========================
        # BUILD PROMPT
        # =========================
        prompt = self._build_prompt(user_text, dto, history)

        # =========================
        # LLM
        # =========================
        ai_text = await self.voice_service.generate_response(prompt)

        print("🤖 RAW AI:", repr(ai_text))

        # =========================
        # VALIDATION (CRITICAL)
        # =========================
        if not ai_text or len(ai_text.strip()) < 3:
            print("⚠️ EMPTY LLM RESPONSE — applying fallback")
            ai_text = self._safe_fallback()

        # =========================
        # STORE AI
        # =========================
        await self.session_store.append(session_id, "assistant", ai_text)

        # =========================
        # TTS
        # =========================
        audio_url = await self.voice_service.text_to_speech(
            text=ai_text,
            language=dto["language"],
            voice=dto["voice"]
        )

        return {
            "transcript": user_text,
            "response_text": ai_text,
            "audio_url": audio_url
        }

    # =========================
    # PROMPT
    # =========================
    def _build_prompt(self, user_text, dto, history):
        return f"""
You are Zeva AI, a professional AI solutions consultant.

Conversation History:
{self._format_history(history)}

User:
{user_text}

Instructions:
- Respond conversationally
- Be concise (2-3 sentences)
- Be business-oriented
- Ask a follow-up question
"""

    # =========================
    # 🔥 FIXED HISTORY FORMATTER
    # =========================
    def _format_history(self, history):
        formatted = []

        for h in history[-5:]:
            role = h.get("role", "user")

            content = (
                h.get("content")
                or h.get("text")
                or h.get("message")
                or ""
            )

            if content:
                formatted.append(f"{role}: {content}")

        return "\n".join(formatted)

    # =========================
    def _safe_fallback(self):
        return (
            "We provide AI voice agents, automation systems, and scalable web solutions. "
            "What are you looking to build?"
        )

    async def _fallback(self, dto, message):
        audio_url = await self.voice_service.text_to_speech(
            text=message,
            language=dto["language"],
            voice=dto["voice"]
        )

        return {
            "transcript": "",
            "response_text": message,
            "audio_url": audio_url
        }