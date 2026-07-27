FROM python:3.11-bullseye AS plotextractor-py3-tests

ARG APP_HOME=/code
ARG POETRY_VERSION=2.2.1

WORKDIR ${APP_HOME}

RUN apt-get update -y && apt-get install -y ghostscript poppler-utils

RUN sed -i 's/domain="coder" rights="none"/domain="coder" rights="read\|write"/' /etc/ImageMagick-6/policy.xml

RUN python -m pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY . .

RUN poetry install --extras tests

CMD ["/bin/bash"]
