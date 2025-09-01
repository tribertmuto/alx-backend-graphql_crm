# CRM Django Application Setup

This document provides step-by-step instructions to set up and run the CRM Django application with Celery for asynchronous task processing.

## Prerequisites

- Python 3.8 or higher
- Redis server
- Django
- Celery

## Installation

1. **Install Redis**:
   - On Ubuntu/Debian: `sudo apt-get install redis-server`
   - On macOS: `brew install redis`
   - On Windows: Download from https://redis.io/download and follow installation instructions
   - Start Redis server: `redis-server`

2. **Install Python dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run Django migrations**:
   ```
   python manage.py migrate
   ```

## Running the Application

1. **Start Django development server**:
   ```
   python manage.py runserver
   ```

2. **Start Celery Worker** (in a separate terminal):
   ```
   celery -A crm worker -l info
   ```

3. **Start Celery Beat** (in a separate terminal):
   ```
   celery -A crm beat -l info
   ```

## Task Management

- The application includes a Celery task `generatecrmreport` defined in `crm/tasks.py`
- This task logs messages to `/tmp/crmreportlog.txt`
- You can trigger the task manually or schedule it using Celery Beat

## Verification

1. **Check Celery Worker**: Ensure the worker is running and connected to Redis
2. **Check Celery Beat**: Ensure the scheduler is running
3. **Verify Logs**: Check `/tmp/crmreportlog.txt` for task execution logs
4. **Test Task**: You can manually run the task using:
   ```
   python manage.py shell -c "from crm.tasks import generatecrmreport; generatecrmreport.delay()"
   ```

## Configuration

- Celery configuration is in `crm/settings.py`
- Broker: Redis at `redis://localhost:6379/0`
- Result backend: Redis at `redis://localhost:6379/0`
- Beat scheduler: Database scheduler from django-celery-beat

## Troubleshooting

- Ensure Redis is running on the default port (6379)
- Check Celery worker logs for any connection issues
- Verify Django settings are correctly configured for Celery
