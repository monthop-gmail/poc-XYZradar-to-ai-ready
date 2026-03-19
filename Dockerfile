FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install modern MCP and other dependencies
RUN pip install --no-cache-dir mcp[cli] fastapi uvicorn pandas pyarrow requests

# Copy project files
COPY . .

# Ensure data directory exists
RUN mkdir -p data

# Run using the modern Streamable HTTP (via FastMCP)
CMD ["mcp", "run", "pipeline/mcp_server_modern.py", "--transport", "sse", "--port", "3000"]
