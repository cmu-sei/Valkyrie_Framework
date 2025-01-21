FROM python:3.10-bullseye

# Install build tools and PostgreSQL headers
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/log /tmp/raw/data

# Add your project
ADD ./ip_maven/src /app
ADD ./ip_maven/readme.md /app
WORKDIR /app

# Install Python deps, including psycopg(2) or psycopg2-binary
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]