from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.db.repositories.base_repository import TenantScopedRepository
from src.infrastructure.db.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepository(TenantScopedRepository):

    def __init__(self, db: AsyncSession, tenant_id: str):
        super().__init__(db, tenant_id)


    async def get_active_by_user(self, user_id):

        stmt = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.tenant_id == self.tenant_id)
            .where(RefreshTokenModel.revoked == False)
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()


    async def save(self, model: RefreshTokenModel):

        self.db.add(model)


    async def commit(self):

        await self.db.commit()