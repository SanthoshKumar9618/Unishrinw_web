from src.domain.entities.call_session import CallSession as DomainCall
from src.infrastructure.db.models.call import CallSession as ORMCall


class CallSessionMapper:

    @staticmethod
    def to_domain(model: ORMCall) -> DomainCall:
        return DomainCall(
            id=model.id,
            tenant_id=model.tenant_id,
            agent_id=model.agent_id,
            status=model.status,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )

    @staticmethod
    def to_model(domain: DomainCall) -> ORMCall:
        return ORMCall(
            id=domain.id,
            tenant_id=domain.tenant_id,
            agent_id=domain.agent_id,
            status=domain.status,
            started_at=domain.started_at,
            ended_at=domain.ended_at,
        )