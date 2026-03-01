FROM python:3.12.7-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure ENV
ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOGGING_CONFIG_LEVEL=INFO \
    LOGGING_CONFIG_NAMESPACES='["", "uvicorn"]'

# Directory for package
WORKDIR /package

# Install project dependencies (ensures cache before project change)
COPY pyproject.toml uv.lock tox.ini README.md .

# Inject a temporary .netrc from a build secret and run uv
RUN uv sync --no-install-project

# Install remaining project
COPY src ./src
COPY tests ./tests

# Install the project
RUN uv sync

# Streamlit defaults to 8501; using 80 is fine in containers but many prefer 8501.
EXPOSE 8501

# Default entrypoint for running Streamlit services
ENTRYPOINT ["uv", "run", "streamlit"]
CMD ["run", "src/ab_service/fe/main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
