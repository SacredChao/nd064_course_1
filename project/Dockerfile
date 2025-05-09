# Use the official Python 3.8 base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY techtrends/ /app/

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 3111

# Initialize the database
RUN python init_db.py

# Command to run the Flask application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=3111"]