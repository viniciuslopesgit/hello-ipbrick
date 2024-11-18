FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY app/app.py app/requirements.txt /app/
RUN pip install -r requirements.txt
EXPOSE 5000
CMD [ "python3", "app.py"]