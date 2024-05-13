FROM ubuntu:latest
LABEL authors="nogorka"

#ENTRYPOINT ["top", "-b"]

FROM python:3.10

WORKDIR /

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 80

ENV MONGODB_URI=MONGODB_URI


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]