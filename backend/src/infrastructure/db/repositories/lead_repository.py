from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.lead import LeadModel


class LeadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict):
        lead = LeadModel(**data)

        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)

        return lead