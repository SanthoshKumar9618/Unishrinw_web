from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from typing import Generic, TypeVar, Type

T = TypeVar("T")

class TenantScopedRepository:

    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    def _tenant_filter(self, model):
        return select(model).where(model.tenant_id == self.tenant_id)

    async def get_by_id(self, model, entity_id):
        stmt = (
            select(model)
            .where(model.id == entity_id)
            .where(model.tenant_id == self.tenant_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    

    async def soft_delete(self, entity_id):

        entity = await self.session.get(self.model, entity_id)

        if not entity:
            return None

        entity.deleted_at = datetime.utcnow()

        await self.session.commit()

        return entity
    



class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.
    Designed for Async SQLAlchemy usage.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, entity_id):
        return await self.session.get(self.model, entity_id)

    async def add(self, entity: T):
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: T):
        await self.session.delete(entity)
        await self.session.flush()

    async def commit(self):
        await self.session.commit()