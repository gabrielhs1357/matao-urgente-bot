FROM cypress/browsers:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    cron

RUN apt-get install python3 -y

RUN echo $(python3 -m site --user-base)

COPY requirements.txt  .

ENV PATH /home/root/.local/bin:${PATH}

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

CMD ["python3", "./src/main.py"]
