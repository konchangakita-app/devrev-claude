FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY scripts/ ./scripts/
COPY references/ ./references/
COPY templates/ ./templates/
COPY SKILL.md .

# Set Python to unbuffered mode for real-time logs
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["python3", "scripts/list_crawler_jobs.py"]
