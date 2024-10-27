import re
from collections import deque
from types import MappingProxyType
from typing import cast

import httpx
from pydantic import BaseModel, Base64Str

from core.settings import settings

GITHUB_URL_PATTERN = re.compile(r'^https://github\.com/([^/]+)/([^/]+)$')
REPO_URL_PATTERN = r'https://api.github.com/repos/{owner}/{repo}/contents'
HEADERS = MappingProxyType(
    {'Authorization': f'Bearer {settings.github_api_token}', 'Accept': 'application/vnd.github.v3+json'}
)


class GitHubFile(BaseModel):
    path: str
    content: Base64Str

    def __str__(self):
        return f'{self.path}: {self.content}'


class GitHubRepo:
    def __init__(self, url: str):
        self._validate_url(url)
        self._url = url
        match_ = cast(re.Match[str], GITHUB_URL_PATTERN.match(self._url))
        self._owner, self._repo = match_.groups()
        self._content_url = REPO_URL_PATTERN.format(owner=self._owner, repo=self._repo)

    @property
    def url(self) -> str:
        return self._url

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def repo(self) -> str:
        return self._repo

    async def fetch_content(self, client: httpx.AsyncClient) -> list[GitHubFile]:
        """Returns all content of repo."""
        content: list[GitHubFile] = []
        response = await self._http_get(client, self._content_url)
        response_deque = deque(response)
        while response_deque:
            pop = response_deque.popleft()
            if pop['type'] == 'file' and not pop['path'].endswith(settings.exclude_extensions):
                file_response = await self._http_get(client, pop['url'])
                file_response = cast(dict, file_response)
                file = GitHubFile(path=file_response['path'], content=file_response['content'])
                content.append(file)
            elif pop['type'] == 'dir':
                dir_response = await self._http_get(client, pop['url'])
                response_deque.extendleft(dir_response)

        return content

    @staticmethod
    async def _http_get(client: httpx.AsyncClient, url, headers=HEADERS, timeout=10, **kwargs) -> list[dict] | dict:
        """Wrapper under httpx.AsyncClient.get"""
        response = await client.get(url=url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _validate_url(url):
        if re.match(GITHUB_URL_PATTERN, url) is None:
            raise ValueError('Expected a url of GitHub repository of user. Example: https://github.com/{owner}/{repo}')
