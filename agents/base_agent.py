from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseAgent(ABC):
    """Abstract Base Class for all RARE agents."""
    def __init__(self, name: str, system_prompt: str, color: str, emoji: str,
                 kpi_config: Dict, image_key: str, reasoning_effort: str = "high"):
        self.name = name
        self.system_prompt = system_prompt
        self.color = color
        self.emoji = emoji
        self.kpi_config = kpi_config
        self.image_key = image_key
        self.reasoning_effort = reasoning_effort

    @abstractmethod
    async def generate_response(
        self,
        user_text: str,
        images: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        pass