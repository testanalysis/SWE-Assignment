# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Run the database initialization script
RUN python init_db.py

# Command to run the Flask app
CMD ["python", "app.py"]
