# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /server

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "fastapi[standard]"
RUN pip install -qU langchain-openai
RUN pip install six

# Copy the rest of the application code into the container
COPY . .

# Expose the port that FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
