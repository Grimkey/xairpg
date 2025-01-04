"""
We only use llama3.2 model for now. We can add more models in the future.
"""

from typing import Iterator
from ollama import ChatResponse, chat
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str


class AIModel:
    def __init__(self, model:str='llama3.2'):
        self.model = model

    def chat(self, messages: list[Message]) -> Iterator[ChatResponse]:
        return self._call(messages, stream=True)
    
    def response(self, messages: list[Message]) -> ChatResponse:
        return self._call(messages, stream=False)
    
    def _call(self, messages: list[Message], stream: bool) -> ChatResponse | Iterator[ChatResponse]:
        messages = [m.model_dump() for m in messages]

        stream = chat(
           model='llama3.2',
            messages=messages,
            stream=stream,
        )
        return stream