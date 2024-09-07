# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory to /code
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY ./swap/ /app
