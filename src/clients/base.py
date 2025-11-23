from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IChatClient(ABC):
    """
    The Contract: All Agents must speak this language.
    This decouples the Agent Logic from the Model Provider.
    """
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], tools: List[Any] = None) -> str:
        pass

    @abstractmethod
    async def get_response(
        self,
        messages: str | Any | list[str] | list[Any],
        *,
        tools: List[Any] = None,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> Any:
        pass
