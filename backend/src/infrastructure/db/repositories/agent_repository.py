from sqlalchemy import select, update
from uuid import UUID
from src.infrastructure.db.repositories.base_repository import TenantScopedRepository
from src.infrastructure.db.models.agent import Agent as AgentORM
from src.infrastructure.db.mappers.agent_mapper import AgentMapper
from sqlalchemy import func

class AgentRepository(TenantScopedRepository):

    def __init__(self, db, tenant_id):
        super().__init__(db, tenant_id)

    async def create(self, agent):
        model = AgentMapper.to_model(agent)

        self.db.add(model)
        await self.db.flush()

        return AgentMapper.to_domain(model)

    async def get_by_id(self, agent_id: UUID):
        stmt = (
            select(AgentORM)
            .where(AgentORM.id == agent_id)
            .where(AgentORM.tenant_id == self.tenant_id)
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return AgentMapper.to_domain(model)
    
    async def list_paginated(self, page: int, page_size: int):
        offset = (page - 1) * page_size

        stmt = (
            select(AgentORM)
            .where(AgentORM.tenant_id == self.tenant_id)
            .order_by(AgentORM.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        count_stmt = (
            select(func.count())
            .select_from(AgentORM)
            .where(AgentORM.tenant_id == self.tenant_id)
        )

        result = await self.db.execute(stmt)
        agents = result.scalars().all()

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        return agents, total


    async def update(self, agent_id, updates: dict):
        stmt = (
            update(AgentORM)
            .where(AgentORM.id == agent_id)
            .where(AgentORM.tenant_id == self.tenant_id)
            .values(**updates)
            .returning(AgentORM)
        )

        result = await self.db.execute(stmt)
        updated = result.fetchone()

        if not updated:
            return None

        return updated[0]