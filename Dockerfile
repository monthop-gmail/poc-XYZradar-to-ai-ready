FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure data directory exists
RUN mkdir -p data

# Default command: Run MCP server in SSE mode
# You can override this to run process_radar.py or use stdio
CMD ["python", "pipeline/mcp_server.py", "--transport", "sse", "--port", "8000"]
