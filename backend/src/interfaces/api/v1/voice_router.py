from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from src.application.dto.voice_dto import ProcessVoiceDTO, EndSessionDTO
from src.application.use_cases.voice.process_voice import ProcessVoiceUseCase
from src.application.use_cases.voice.end_session import EndSessionUseCase

from src.application.services.voice_service import VoiceService
from src.infrastructure.providers.stt.deepgram_provider import DeepgramProvider 
from src.infrastructure.providers.tts.coqui_provider import CoquiProvider
from src.infrastructure.cache.inmemory_session_store import InMemorySessionStore
from src.config.llm_factory import get_llm_provider
router = APIRouter()

# 🔧 INIT (singleton for demo)
voice_service = VoiceService(
    llm = get_llm_provider(),
    stt=DeepgramProvider(),
    tts=CoquiProvider(),
)

session_store = InMemorySessionStore()

process_usecase = ProcessVoiceUseCase(
    voice_service=voice_service,
    session_store=session_store,
)
end_usecase = EndSessionUseCase(
    voice_service=voice_service,
    session_store=session_store,    
)

@router.post("/process")
async def process_voice(
    request_id: str = Form(...),   # 🔥 IMPORTANT
    session_id: str = Form(...),
    persona: str = Form(...),
    prompt: str = Form(...),
    language: str = Form(...),
    voice: str = Form(...),
    audio: UploadFile = File(...),
):
    audio_bytes = await audio.read()

    dto = {
        "session_id": session_id,
        "persona": persona,
        "prompt": prompt,
        "language": language,
        "voice": voice,
    }

    result = await process_usecase.execute(dto, audio_bytes)

    return {
        "request_id": request_id,   # 🔥 IMPORTANT
        "data": result
    }

# ==============================
# POST /voice/end-session
# ==============================
@router.post("/end-session")
async def end_session(payload: EndSessionDTO):
    try:
        result = await end_usecase.execute(payload)

        return {
            "success": True,
            "data": result
        }

    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()  # 🔥 ADD THIS

        raise HTTPException(status_code=500, detail=str(e))