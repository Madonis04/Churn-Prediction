# Use an official lightweight Python image as a parent image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependency for LightGBM
RUN apt-get update && apt-get install -y libgomp1

# Copy the requirements file into the container
COPY ./requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]