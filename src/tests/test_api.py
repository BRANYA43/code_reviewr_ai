from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from core.api import api
from core.settings import settings
from integrations.github import GitHubFile


class TestReviewEndpoint:
    client = TestClient(api)

    @pytest.mark.skipif(settings.skip_integration_tests is True, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    async def test_api_cant_get_content_of_repo_by_invalid_url(self):
        payload = {
            'github_repo_url': 'https://invalid.com/test_user/test_repo',
            'assignment_description': 'Review the code.',
            'candidate_level': 'junior',
        }

        response = self.client.post('/api/review', json=payload)

        assert response.status_code == 400
        assert 'Invalid GitHub repository URL.' in str(response.json())

    @pytest.mark.skipif(settings.skip_integration_tests is True, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    async def test_api_cant_get_content_of_non_existent_repo(self):
        payload = {
            'github_repo_url': 'https://github.com/non_existent_user/non_existent_repo',
            'assignment_description': 'Review the code.',
            'candidate_level': 'junior',
        }

        response = self.client.post('/api/review', json=payload)

        assert response.status_code == 404
        assert 'Not Found GitHub repository.' in str(response.json())

    @pytest.mark.skipif(settings.skip_integration_tests is True, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    @patch('core.api.get_repo_content', new_callable=AsyncMock)
    async def test_api_cant_use_openai_api_without_token(self, mock_get_repo_content):
        settings.openai_api_token = ''
        payload = {
            'github_repo_url': 'https://github.com/user/repo',
            'assignment_description': 'Review the code.',
            'candidate_level': 'junior',
        }
        mock_get_repo_content.return_value = [GitHubFile(path='test.txt', content=bytes('SGVsbG8gV29ybGQ=', 'utf-8'))]

        response = self.client.post('/api/review', json=payload)

        assert response.status_code == 500
        assert 'Error code: 429' in str(response.json())

    @pytest.mark.skipif(settings.skip_integration_tests is True, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    @patch('core.api.get_repo_content', new_callable=AsyncMock)
    async def test_api_returns_answer_of_chatgpt(self, mock_get_repo_content):
        payload = {
            'github_repo_url': 'https://github.com/user/repo',
            'assignment_description': 'Review the code.',
            'candidate_level': 'junior',
        }
        mock_get_repo_content.return_value = [GitHubFile(path='test.txt', content=bytes('SGVsbG8gV29ybGQ=', 'utf-8'))]

        response = self.client.post('/api/review', json=payload)
        assert response.status_code == 200
        assert bool(response.json())
