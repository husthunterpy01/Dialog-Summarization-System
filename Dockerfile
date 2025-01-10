# Base image for Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and application files
COPY requirements.txt ./requirements.txt
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for Uvicorn and Streamlit
EXPOSE 8000 8501

# Default command
CMD ["bash", "-c", "uvicorn chatbot.main:app --host 0.0.0.0 --port 8000 & streamlit run chatbot/frontend/chatbotui.py --server.port 8501 --server.address 0.0.0.0"]
