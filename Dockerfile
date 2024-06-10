# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ ./src/
COPY Logs/ ./Logs/
COPY Output/ ./Output/

# Set the default command to run the data processing and analysis scripts
CMD ["python", "src/Data_Parsing.py", "&&", "python", "src/Data_Cleaning.py", "&&", "python", "src/Data_Analysis.py", "&&", "python", "src/Anomalies.py"]
