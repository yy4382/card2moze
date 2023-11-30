# Use an official Python runtime as a parent image
FROM python:3.12.0-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5500

# Run app.py when the container launches
CMD ["python", "src/app.py"]