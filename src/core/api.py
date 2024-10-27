import tenacity
from fastapi import FastAPI, HTTPException
import httpx

from core.schemas import ReviewInputSchema
from core.settings import settings
from integrations.chatgpt import ChatGPT
from integrations.github import GitHubRepo

from utils import async_iterator
from utils.prompts import reviewing_file_prompt, finally_review_prompt

api = FastAPI()
chatgpt_client = ChatGPT(settings.openai_model)
httpx_client = httpx.AsyncClient()


@api.get('/api/ping')
async def ping():
    return dict(status_code=200, message='pong')


@api.post('/api/review')
async def review(payload: ReviewInputSchema):
    repo_content = await get_repo_content(payload.github_repo_url)
    str_repo_content = [str(file) for file in repo_content]
    file_reviews = await get_file_reviews(str_repo_content, payload)
    finally_review = await get_finally_review(file_reviews)
    found_files = 'Found files:' + '\n'.join([file.path for file in repo_content])

    return found_files + finally_review


async def get_finally_review(file_reviews: list[str]) -> str:
    file_reviews_ = '\n'.join(file_reviews)
    finally_review_msg = await chatgpt_client.create_message(role='system', content=finally_review_prompt)
    finally_msg = await chatgpt_client.create_message(role='user', content=f'Report: {file_reviews_}')
    try:
        finally_review = await chatgpt_client.get_response([finally_review_msg, finally_msg], max_token=2000)
    except tenacity.RetryError as e:
        raise HTTPException(status_code=500, detail=str(e.last_attempt.exception()))
    return finally_review


async def get_file_reviews(repo_content: list[str], payload: ReviewInputSchema) -> list[str]:
    reviews = []
    reviewing_file_msg = await chatgpt_client.create_message(role='system', content=reviewing_file_prompt)
    async for file_content in async_iterator(repo_content):
        file_msg = await chatgpt_client.create_message(
            role='user',
            content=f'Assignment: {payload.assignment_description}, Code: {file_content}, '
            f'Developer level: {payload.candidate_level}',
        )
        try:
            response = await chatgpt_client.get_response([reviewing_file_msg, file_msg], max_token=150)
        except tenacity.RetryError as e:
            raise HTTPException(status_code=500, detail=str(e.last_attempt.exception()))
        reviews.append(response)
    return reviews


async def get_repo_content(github_repo_url: str):
    try:
        repo = GitHubRepo(str(github_repo_url))

        async with httpx_client as client:
            content = await repo.fetch_content(client)
        return content
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid GitHub repository URL.')
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail='Not Found GitHub repository.')
