FROM python:3.11-bullseye

# Set environment variables
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST

ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}

ENV PYTHONBUFFERED=1

WORKDIR /django

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run manage.py to start the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000