# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt first
COPY requirements.txt .

# Install the necessary dependencies from requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt

# Then copy the rest of the application
COPY . /app

# Expose the port that Streamlit will run on (default: 8501)
EXPOSE 8502

# Run the Streamlit app
RUN chmod +x docker-entrypoint.sh

# Command to run the streamlit app
CMD ["./docker-entrypoint.sh"]
