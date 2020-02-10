
FROM ubuntu:18.04
RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential
COPY . /api
WORKDIR /api
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["api.py"]
