# Use the official Python image from the Docker Hub
FROM python:3.9-slim as base

# Set the working directory
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt /app/requirements.txt

# Install the required packages
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code
COPY . /app

# Create a base image for the FastAPI service
FROM base as fastapi

# Set the working directory for the FastAPI service
WORKDIR /app/Chatbot

# Expose the port for FastAPI
EXPOSE 8000

# Command to run the FastAPI service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Create a base image for the Streamlit service
FROM base as streamlit

# Set the working directory for the Streamlit service
WORKDIR /app/ChatbotUI

# Expose the port for Streamlit
EXPOSE 8501

# Command to run the Streamlit service
CMD ["streamlit", "run", "main.py"]