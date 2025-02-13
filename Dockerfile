# Use an official Python runtime as base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8080

# Command to run the FastAPI application
CMD ["uvicorn", "src.retrieval_api:app", "--host", "0.0.0.0", "--port", "8080"]
