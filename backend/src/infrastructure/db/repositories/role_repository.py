from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.db.models.user_role import UserRoleModel
from src.infrastructure.db.models.role import RoleModel


class RoleRepository:

    def __init__(self, db: AsyncSession, tenant_id):
        self.db = db
        self.tenant_id = tenant_id

    async def get_user_roles(self, user_id):
        stmt = (
            select(RoleModel.name)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .where(UserRoleModel.user_id == user_id)
            .where(RoleModel.tenant_id == self.tenant_id)
        )

        result = await self.db.execute(stmt)
        return [r[0] for r in result.all()]