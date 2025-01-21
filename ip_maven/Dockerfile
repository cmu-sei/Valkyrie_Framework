FROM python:3.10-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ADD DIRECTORIES
RUN mkdir -p /app/log /tmp/raw/data
ADD ./ip_maven/src /app
ADD ./ip_maven/readme.md /app
WORKDIR /app

# GATHER PYTHON MODULES
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# EXPOSE DJANGO DEFAULT PORT
EXPOSE 8000

# START DJANGO SERVER
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
