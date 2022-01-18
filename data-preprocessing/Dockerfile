FROM python:3.7-slim

WORKDIR /data-preprocessing

COPY ./requirements.txt /data-preprocessing/requirements.txt

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean \
    && apt-get install zip -y \
    && apt-get install p7zip-full -y

RUN pip install --upgrade pip \
    && pip install -r /data-preprocessing/requirements.txt \
    && rm -rf /root/.cache/pip

COPY ./kaggle.json /root/.kaggle/kaggle.json
COPY ./src /data-preprocessing/src/

CMD ["bash", "src/get_data.sh"]