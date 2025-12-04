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
pip install pandas
pip install streamlit
pip install requests
EOF

# Expose port
EXPOSE 8501

# Set working directory
WORKDIR /app

COPY . .

# Command to run the application
CMD ["streamlit", "run", "app.py"]
