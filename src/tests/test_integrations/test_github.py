from unittest.mock import patch, AsyncMock

import httpx
import pytest
from httpx import Request

from core.settings import settings
from integrations.github import GitHubRepo


class TestGitHubRepo:
    OWNER = 'bob'
    REPO = 'cli_app'
    REPO_URL = f'https://github.com/{OWNER}/{REPO}'
    CONTENT_REPO_URL = f'https://api.github.com/repos/{OWNER}/{REPO}/contents'
    INVALID_REPO_URL = f'https://invalid-url.com/{OWNER}/{REPO}'

    @pytest.mark.asyncio
    async def test_creating_repo_with_valid_url(self):
        repo = GitHubRepo(self.REPO_URL)
        assert repo.url == self.REPO_URL
        assert repo.owner == self.OWNER
        assert repo.repo == self.REPO

    @pytest.mark.asyncio
    async def test_creating_repo_raises_error_for_invalid_url(self):
        with pytest.raises(
            ValueError,
            match='Expected a url of GitHub repository of user. Example: https://github.com/{owner}/{repo}',
        ):
            GitHubRepo(self.INVALID_REPO_URL)

    @pytest.mark.asyncio
    @patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock)
    async def test_fetching_content_raises_error_if_status_code_404(self, mock_get):
        mock_get.return_value = httpx.Response(404, request=Request('get', self.CONTENT_REPO_URL))

        repo = GitHubRepo(self.REPO_URL)

        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await repo.fetch_content(client)

    @pytest.mark.asyncio
    @patch.object(GitHubRepo, '_http_get', new_callable=AsyncMock)
    async def test_fetching_content_returns_content(self, mock_get):
        mock_response_values = {
            self.CONTENT_REPO_URL: [
                {'type': 'file', 'path': 'file1.txt', 'url': 'file1_url'},
                {'type': 'dir', 'path': 'texts', 'url': 'dir_url'},
            ],
            'file1_url': {'path': 'file1.txt', 'content': bytes('SGVsbG8gV29ybGQ=', 'utf-8')},
            'dir_url': [{'type': 'file', 'path': 'file2.txt', 'url': 'file2_url'}],
            'file2_url': {'path': 'file2.txt', 'content': bytes('SGVsbG8gUHl0aG9u', 'utf-8')},
        }
        mock_get.side_effect = lambda client_, key, *args, **kwargs: mock_response_values[key]

        repo = GitHubRepo(self.REPO_URL)
        async with httpx.AsyncClient() as client:
            content = await repo.fetch_content(client)

        assert content == ['file1.txt: Hello World', 'file2.txt: Hello Python']

    @pytest.mark.asyncio
    @patch.object(GitHubRepo, '_http_get', new_callable=AsyncMock)
    async def test_fetching_content_returns_content_but_exclude_expected_extensions(self, mock_get):
        settings.exclude_extensions = ('.gitignore',)
        mock_response_values = {
            self.CONTENT_REPO_URL: [
                {'type': 'file', 'path': 'file1.txt', 'url': 'file1_url'},
                {'type': 'file', 'path': '.gitignore', 'url': 'git_url'},
            ],
            'file1_url': {'path': 'file1.txt', 'content': bytes('SGVsbG8gV29ybGQ=', 'utf-8')},
            'git_url': {'path': '.gitignore', 'content': bytes('SGVsbG8gUHl0aG9u', 'utf-8')},
        }
        mock_get.side_effect = lambda client_, key, *args, **kwargs: mock_response_values[key]

        repo = GitHubRepo(self.REPO_URL)
        async with httpx.AsyncClient() as client:
            content = await repo.fetch_content(client)

        assert content == ['file1.txt: Hello World']

    @pytest.mark.skipif(settings.skip_integration_tests, reason='Skipping integration tests.')
    @pytest.mark.asyncio
    async def test_integration_with_github(self):
        repo = GitHubRepo('https://github.com/BRANYA43/console_weather')
        async with httpx.AsyncClient() as client:
            content = await repo.fetch_content(client)

        assert bool(content)

        print(content[:20], '...]')  # noqa [T201]
