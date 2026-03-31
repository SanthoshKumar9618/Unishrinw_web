from src.infrastructure.db.models.agent import Agent as AgentORM
from src.domain.entities.agent import Agent as AgentDomain


class AgentMapper:

    @staticmethod
    def to_domain(model: AgentORM) -> AgentDomain:
        return AgentDomain(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            execution_mode=model.execution_mode,

            # ✅ NEW (aligned with domain)
            voice_config=model.voice_config or {},
            governance_config=model.governance_config or {},

            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(domain: AgentDomain) -> AgentORM:
        return AgentORM(
            id=domain.id,
            tenant_id=domain.tenant_id,
            name=domain.name,
            execution_mode=domain.execution_mode,

            # ✅ NEW (aligned with DB)
            voice_config=domain.voice_config,
            governance_config=domain.governance_config,
        )