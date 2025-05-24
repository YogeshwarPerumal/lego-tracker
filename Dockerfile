FROM python:3.9-slim

WORKDIR /app

# Copy the entire application
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user to run the application
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run the price tracker with scheduling
CMD ["python", "main.py"]
