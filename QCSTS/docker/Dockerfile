FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/base.txt requirements/base.txt
COPY requirements.txt .
RUN pip install --upgrade pip --root-user-action=ignore \
    && pip install -r requirements.txt --root-user-action=ignore

# Copy project
COPY . .

# Create logs directory
RUN mkdir -p logs

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]