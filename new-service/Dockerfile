FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    default-jre \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies globally
RUN <<EOF
pip install vulture
pip install "fastapi[standard]"
pip install sqlmodel
pip install pydantic_settings
pip install psycopg[binary]
pip install pymupdf
pip install tenacity
pip install black
EOF

# Expose port
EXPOSE 8000

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["fastapi", "run", "app/main.py"]