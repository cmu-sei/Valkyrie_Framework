FROM python:3.10-bullseye

# FOR PROXY UNCOMMENT BELOW AND ADD YOUR PROXY
#ENV HTTP_PROXY ""
#ENV HTTPS_PROXY ""
#ENV NO_PROXY ""

RUN mkdir /app && mkdir /app/log && mkdir /tmp/raw && mkdir /tmp/raw/data
ADD ./src/. /app
ADD ./readme.md /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r ./setup/requirements.txt

CMD ["python", "beacon_huntress.py"]
