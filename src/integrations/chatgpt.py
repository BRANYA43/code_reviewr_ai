from typing import TypedDict, Literal

from openai import AsyncClient, BaseModel
from tenacity import retry, wait_random_exponential, stop_after_attempt

from core.settings import settings


class Message(BaseModel):
    role: Literal['system', 'user']
    content: str


class MessageDict(TypedDict):
    role: Literal['system', 'user']
    content: str


class ChatGPT:
    def __init__(self, model='gpt-4-turbo'):
        self._client = AsyncClient(api_key=settings.openai_api_token)
        self._model = model

    @staticmethod
    async def create_message(role: Literal['system', 'user'], content: str) -> MessageDict | dict:
        return Message(role=role, content=content).to_dict()

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5), reraise=True)
    async def get_response(self, messages: list[MessageDict | dict], max_token=None) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_token,
        )
        return response.choices[0].message.content
