# Use the official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy application
COPY . .

# Install prerequisites
RUN apt-get update && \
    apt-get install -y curl gnupg2 unixodbc unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Add Microsoft repository
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/microsoft-prod.list

# Install ODBC Driver 18
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose application port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]