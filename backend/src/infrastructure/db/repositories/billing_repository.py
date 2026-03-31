from src.infrastructure.db.repositories.base_repository import BaseRepository
from src.infrastructure.db.models.billing_record import BillingRecordModel

from src.domain.entities.billing_record import BillingRecord


class BillingRepository(BaseRepository):

    async def save(self, record: BillingRecord):

        model = BillingRecordModel(
            tenant_id=record.tenant_id,
            call_id=record.call_id,
            stt_seconds=record.stt_seconds,
            tts_seconds=record.tts_seconds,
            llm_input_tokens=record.llm_input_tokens,
            llm_output_tokens=record.llm_output_tokens,
            total_cost=record.total_cost,
            created_at=record.created_at,
        )

        self.session.add(model)

        await self.session.commit()
        


