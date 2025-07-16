FROM python:3.10-bullseye

# FOR PROXY UNCOMMENT BELOW AND ADD YOUR PROXY
#ENV HTTP_PROXY=""
#ENV HTTPS_PROXY=""
#ENV NO_PROXY=""

# ADD DIRECTORIES
RUN mkdir /app && mkdir /app/log && mkdir /tmp/raw && mkdir /tmp/raw/data
ADD ./bh_web /app
ADD ./readme.md /app
WORKDIR /app

# GATHER PYTHON MODULES
RUN pip install --upgrade pip
RUN pip install -r /app/beacon_huntress/src/setup/requirements.txt

