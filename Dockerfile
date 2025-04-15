# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables (can be overridden at runtime)
ENV DISCORD_TOKEN=""
ENV COMMAND_CHANNEL=""
ENV SKIP_LINES_FILE=""

# Run the bot
CMD ["python", "bot.py"]
