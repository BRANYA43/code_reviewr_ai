from unittest.mock import patch, AsyncMock, Mock

import openai
import pytest
from openai.resources.chat import AsyncCompletions

from core.settings import settings
from integrations.chatgpt import ChatGPT


class TestChatGpt:
    @pytest.fixture()
    def chatgpt(self) -> ChatGPT:
        return ChatGPT()

    def test_creation_chatgpt(self):
        chatgpt = ChatGPT()
        assert chatgpt._model == 'gpt-4-turbo'
        assert isinstance(chatgpt._client, openai.AsyncClient)

    @pytest.mark.asyncio
    async def test_creating_message(self, chatgpt):
        assert await chatgpt.create_message('user', 'some message') == dict(role='user', content='some message')

    @pytest.mark.parametrize('role,content', [('system', None), ('user', 20), (None, 'some message')])
    @pytest.mark.asyncio
    async def test_creating_message_raises_error_for_invalid_user_or_content(self, role, content, chatgpt):
        with pytest.raises(ValueError):
            await chatgpt.create_message(role, content)

    @pytest.mark.asyncio
    @patch.object(AsyncCompletions, 'create', new_callable=AsyncMock)
    async def test_getting_response(self, mock_create, chatgpt):
        mock_message = Mock(content='Hello!')
        mock_choice = Mock(message=mock_message)
        mock_chat_completion = Mock(choices=[mock_choice])
        mock_create.return_value = mock_chat_completion
        msg = await chatgpt.create_message('user', 'hi')
        response = await chatgpt.get_response([msg])
        assert response == 'Hello!'

    @pytest.mark.skipif(settings.skip_integration_tests, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    async def test_integration_getting_response(self, mock_create, chatgpt):
        mock_create.return_value = 'Hello!'
        msg = await chatgpt.create_message('user', 'hi')
        response = await chatgpt.get_response([msg])
        assert bool(response)
