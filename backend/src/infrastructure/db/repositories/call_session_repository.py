from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.infrastructure.db.models.call import CallSession as ORMCall

from src.domain.entities.call_session import CallSession


class CallSessionRepository(BaseRepository):

    async def save(self, call: CallSession):

        model = ORMCall(
            id=call.id,
            tenant_id=call.tenant_id,
            agent_id=call.agent_id,
            status=call.status.value,
            started_at=call.started_at,
            ended_at=call.ended_at,
            tool_invocation_count=call.tool_invocation_count,
            total_tokens=call.total_tokens,
            token_budget=call.token_budget,
            active_agent_id=call.active_agent_id,
            version=call.version,
        )

        self.session.add(model)

        await self.session.commit()

    async def get(self, call_id):

        return await self.session.get(ORMCall, call_id)