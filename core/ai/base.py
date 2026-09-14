from abc import ABC, abstractmethod
from .response import AIResponse


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, history=None, tool_result=None, system_prompt=None, tools=None) -> AIResponse:
        raise NotImplementedError