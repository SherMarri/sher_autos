# *** BEGIN common Dockerfile commands, to improve caching
# *** Please copy from Dockerfile.common
FROM python:3.9.10-bullseye

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y \
    libspatialindex-dev \
    postgresql-client \
    libopenblas-base \
    libomp-dev

# improve docker layer caching by installing requirements.txt early & separately
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# *** BEGIN service-specific customizations
COPY . /app

EXPOSE 8000
ENV PYTHONPATH=.
CMD [ "python app/manage.py runserver" ]
# *** END service-specific customizations
