from typing import Dict, Any

from src.application.interfaces.tool_executor import ToolExecutor


class ActionDispatcher(ToolExecutor):

    def __init__(self):
        self._tools = {}

    def register(self, name: str, handler):
        self._tools[name] = handler

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:

        handler = self._tools.get(tool_name)

        if not handler:
            raise RuntimeError(f"Tool {tool_name} not registered")

        result = await handler(arguments, tenant_id)

        return {
            "tool": tool_name,
            "result": result
        }