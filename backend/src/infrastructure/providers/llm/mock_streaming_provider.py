import asyncio
from typing import AsyncGenerator, List, Dict, Any

from src.infrastructure.providers.llm.provider import LLMProvider


class MockStreamingLLMProvider(LLMProvider):

    async def stream_generate(
        self,
        messages: List[Dict[str, Any]],
        config: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:

        response = "Hello this is a mock LLM response."

        for token in response.split():
            await asyncio.sleep(0.05)
            yield token + " "

    async def parse_tool_call(self, text: str):
        return None