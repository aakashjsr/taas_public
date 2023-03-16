# This handles our server API

FROM python:3.9

RUN apt update -y && apt upgrade -y && apt install postgresql postgresql-contrib -y

RUN apt-get install -y locales && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

RUN pip install --upgrade setuptools

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /opt/
WORKDIR /opt/

EXPOSE 8080

ENV LANG de_DE.UTF-8
ENV LC_ALL de_DE.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN mkdir -p logs

CMD ["bash", "entrypoint.sh"]