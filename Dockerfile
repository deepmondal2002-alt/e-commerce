# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (update if needed)
EXPOSE 8080

# Command to run the application (update based on your app, e.g., uvicorn, gunicorn, or python)
CMD ["python", "main.py"]
