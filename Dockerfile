# Use the official Python image from the Docker Hub
FROM python:3.10-slim
RUN apt-get update && apt-get install -y git ffmpeg && rm -rf /var/lib/apt/lists/*
# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/m-bain/whisperx.git
# Copy the rest of the application code into the container
COPY . .

# Command to run the application
CMD ["python", "main.py"]
