FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator files
COPY simulator.py .
COPY config.json .

# Run simulator with time acceleration: 1 sec = 10 min, duration 20 sec, interval 1 sec
CMD ["python", "simulator.py", "--interval", "1", "--duration", "20", "--time-acceleration", "10"]
