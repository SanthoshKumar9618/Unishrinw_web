from src.application.dto.voice_dto import EndSessionDTO


class EndSessionUseCase:

    def __init__(self, voice_service, session_store):
        self.voice_service = voice_service
        self.session_store = session_store

    async def execute(self, dto):
        session_id = dto.session_id
        lead_id = dto.lead_id

        session = await self.session_store.get(session_id)

        if not session:
            raise ValueError("Session not found")

        conversation = session.get("history", [])

        extracted = {}
        if conversation:
            extracted = await self.voice_service.extract_structured_data(conversation)

        await self.voice_service.store_conversation(
            lead_id=lead_id,
            session_id=session_id,
            transcript=conversation,
            extracted=extracted
        )

        await self.session_store.delete(session_id)

        return {
            "message": "Session ended",
            "count": len(conversation)
        }