# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Update the package list
RUN apt-get update

# Install required system packages
RUN apt-get install -y --no-install-recommends pkg-config libmariadb-dev libmariadb-dev-compat gcc g++

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clean up to reduce image size
RUN apt-get clean

# Remove the package lists to reduce image size
RUN rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY ./swap/ /app/

# Ensure the swap module is in the Python path
ENV PYTHONPATH=/app

# Run collectstatic command to gather static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000