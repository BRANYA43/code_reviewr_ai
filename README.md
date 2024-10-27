# How to Run the Application
- Set up the `.env` file before running the application. Use `copy example.env .env` to create the file and set your tokens.
- To run the app, use `uvicorn main:api --host 0.0.0.0 --port 8000` from the `src` folder.
- To run it in Docker, use `docker compose up`.

# API Endpoints
- http://0.0.0.0:8000/api/ping
- http://0.0.0.0:8000/api/review


# Part 2 — Scaling

To scale the system to handle 100+ review requests per minute and work with repositories containing over 100 files,
I propose the following approach:

1. **Using multiple instances and RabbitMQ**
   RabbitMQ will help efficiently split review requests between multiple app instances. This setup allows for
   parallel processing, making the system faster.

2. **Using a database for caching results**
   The database will store repository addresses, the latest commit, task descriptions, reviews of processed files,
   and final reviews. When a request for an already processed repository is made, the system checks the latest commit.
   If the commit is the same, it returns the saved final review. If the repository has a new commit, the system
   handles the changed files and updates only their reviews. In this case, `Redis` can be used for intermediate results
   and `PostgreSQL` for final results.

3. **Implement `rate limiting` and `backoff` strategies for APIs**
   To prevent hitting rate limits for the OpenAI and GitHub APIs, the `tenacity` library can be used. This will
   automatically add a pause before retrying a request if the last attempt failed.

4. **Optimize requests by processing multiple files at once**
   Sending multiple files in a single API request will reduce the total number of requests. For each request it's
   necessary to calculate the number of tokens not to out the limit.
