FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Run the script, wait 6 hours, repeat. Adjust sleep duration as needed.
CMD ["sh", "-c", "while true; do python main.py; sleep 21600; done"]
