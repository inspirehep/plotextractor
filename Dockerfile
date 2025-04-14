FROM python:3.11-bullseye AS plotextractor-py3-tests

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

COPY . .

RUN apt-get update -y && apt-get install -y ghostscript

RUN sed -i 's/domain="coder" rights="none"/domain="coder" rights="read\|write"/' /etc/ImageMagick-6/policy.xml

RUN pip install -e .[tests]

CMD ["/bin/bash"]
